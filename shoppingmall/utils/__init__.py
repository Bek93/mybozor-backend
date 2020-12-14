from shoppingmall.serializers.users_serializers import CustomerSerializer, SellerSerializer, AdminSerializer


def jwt_response_payload_handler(token, user=None, request=None):
    if user.is_seller():
        user = SellerSerializer(user.seller, context={'request': request}).data
        user['token'] = token
    elif user.is_customer():
        user = CustomerSerializer(user.customer, context={'request': request}).data
        user['token'] = token
    elif user.is_admin():
        user = AdminSerializer(user.admin, context={'request': request}).data
        user['token'] = token
    return user
