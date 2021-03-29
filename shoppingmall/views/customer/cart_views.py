from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from telegram_notify import TelegramNotify
from ...models import Order, OrderedProduct, Cart, Product, Shop
from ...serializers.cart_serializers import CartDetailSerializer, CartSerializer
from ...serializers.order_serializers import OrderSerializer, OrderDetailsSerializer
from ...serializers.shop_serializers import ShopSerializer, ShopReadSerializer
from ...utils.config import getNewOrderNumber
from ...utils.logger import Logger


class CartViewSet(viewsets.ModelViewSet):
    queryset = Cart.objects.all().order_by('-date_created')
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]
    """
    Retrieve a model instance.
    """

    def get_serializer_context(self):
        user = self.request.user
        language = "uz"
        if user.is_authenticated and user.is_customer():
            language = user.customer.language
        if 'lang' in self.request.query_params:
            language = self.request.query_params['lang']
        return {"language": language, "request": self.request}

    def create(self, request, *args, **kwargs):

        user = self.request.user
        data = request.data
        if user.is_customer():

            try:
                if "option" in data:
                    cart = Cart.objects.get(user=user.pk, product=data['product'], option=data['option'])
                else:
                    cart = Cart.objects.get(user=user.pk, product=data['product'])
                if cart:
                    cart.quantity = cart.quantity + data['quantity']
                    cart.save()
            except Exception as e:
                data["user"] = user.pk
                product = Product.objects.get(id=data['product'])
                data['shop'] = product.shop.id
                serializer = self.get_serializer(data=data)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                cart = Cart.objects.get(id=serializer.data['id'])

            cart_serializer = CartSerializer(cart, context=self.get_serializer_context())
            response = cart_serializer.data
            headers = self.get_success_headers(cart_serializer.data)
            Logger().d(data_string=data, method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=200)

            return Response(cart_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            response = {"error": ["Only customer can access"]}
            Logger().d(data_string=data, method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=403)
            return Response(response, status=status.HTTP_403_FORBIDDEN)

    @action(methods=['post'], detail=False)
    def order(self, request):
        user = request.user.customer
        data = request.data
        if user.is_customer():
            carts = data.pop("carts")
            if carts:
                order_responses = []
                for cart in carts:
                    ids = cart.pop('ids')
                    shop = Shop.objects.get(id=cart['shopId'])
                    shop = ShopReadSerializer(shop, context=self.get_serializer_context()).data
                    data["user"] = user.pk
                    data["shop"] = cart['shopId']
                    data['name'] = user.customer.name
                    data['phone'] = user.customer.phone_number
                    data['address'] = user.customer.address
                    data['address_image'] = user.customer.address_image
                    data['language'] = user.customer.language
                    userId = user.id
                    order = OrderSerializer(data=data)
                    order.is_valid(raise_exception=True)
                    self.perform_create(order)
                    data = order.data
                    order = Order.objects.get(id=data['id'])
                    total_selling = 0
                    total_buying = 0
                    quantity_amount = 0
                    total_referral_fee = 0
                    savedProductCount = 0
                    for id in ids:
                        try:
                            cart = Cart.objects.get(id=id)
                            if cart.user.id == userId:
                                orderedProduct = OrderedProduct(order=order, product=cart.product,
                                                                quantity=cart.quantity,
                                                                buying=cart.product.buying,
                                                                selling=cart.product.selling,
                                                                referral_fee=cart.product.referral_fee)
                                orderedProduct.save()
                                total_buying += cart.product.buying * cart.quantity
                                total_selling += cart.product.selling * cart.quantity
                                total_referral_fee += cart.product.referral_fee * cart.quantity
                                quantity_amount += cart.quantity
                                cart.delete()
                                savedProductCount = savedProductCount + 1
                        except Exception as ex:
                            print(ex)
                            continue

                    if savedProductCount == 0:
                        order.delete()
                        data = {
                            "message": "Cart already was ordered or deleted"
                        }
                        return Response(data, status=status.HTTP_406_NOT_ACCEPTABLE)

                    delivery_policy = shop['delivery_policy']
                    delivery_fee = 0
                    for policy in delivery_policy:
                        if policy['unit_from'] < quantity_amount <= policy['unit_to']:
                            delivery_fee = policy['fee']

                    order.total_buying = total_buying
                    order.total_selling = total_selling
                    order.delivery_fee = delivery_fee
                    order.total_referral_fee = total_referral_fee
                    order.order_number = getNewOrderNumber(order.id)
                    order.save()
                    order_ser = OrderDetailsSerializer(order, context=self.get_serializer_context())
                    response = order_ser.data
                    response['shop'] = shop
                    order_responses.append(response)
                    telegram = TelegramNotify()
                    try:
                        telegram.send_new_order(response, shop)
                    except Exception as ex:
                        print(ex)
                        pass

                    Logger().d(data_string='', method=request.method, path=request.path,
                               shop_id=shop['id'], user_id=user.id, payload_string=response, status_code=200)

                return Response(order_responses, status=status.HTTP_201_CREATED)
            else:
                response = {"carts": ["Only customer can access"]}
                Logger().d(data_string=data, method=request.method, path=request.path,
                           shop_id=0, user_id=user.id, payload_string=response, status_code=403)
                return Response(response, status=status.HTTP_403_FORBIDDEN)
        else:
            response = {"error": ["Only customer can access"]}
            Logger().d(data_string=data, method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=403)
            return Response(response, status=status.HTTP_403_FORBIDDEN)

    """
    List a queryset.
    """

    def list(self, request, *args, **kwargs):
        user = request.user

        if user.is_customer():
            cart_all = []
            shops = Cart.objects.filter(user=user.pk).values('shop').annotate(shop_count=Count('shop'))
            for shop in shops:
                cart_by_shop = {}
                shop = Shop.objects.get(id=shop['shop'])
                shopSerializer = ShopReadSerializer(shop, context=self.get_serializer_context())
                cart = Cart.objects.filter(user=user.pk, shop=shop.id)
                serializer = CartDetailSerializer(cart, context=self.get_serializer_context(), many=True)
                response = serializer.data
                cart_by_shop = {
                    "shop": shopSerializer.data,
                    "carts": serializer.data
                }
                cart_all.append(cart_by_shop)
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id='', user_id=user.id, payload_string=cart_all, status_code=200)
            return Response(cart_all, status=status.HTTP_200_OK)
        else:
            response = {"error": ["Only customer can access"]}
            Logger().d(data_string='', method=request.method, path=request.path,
                       shop_id=0, user_id=user.id, payload_string=response, status_code=403)
            return Response(response, status=status.HTTP_403_FORBIDDEN)

    def get_permissions(self):
        return super(CartViewSet, self).get_permissions()
