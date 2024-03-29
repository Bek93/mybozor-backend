from django.urls import include, path
from rest_framework import routers

from shoppingmall.views.shop import user_views as shop_user_views, shop_views, product_views, collection_views, \
    image_views, order_views, dashboard_views, category_views as seller_category_views
from shoppingmall.views.customer import customer_views, product_views as customer_product_views, \
    collection_views as customer_category_views, customer_shop_views as customer_shop_views, cart_views, \
    order_views as customer_order_views, province_views
from shoppingmall.views.organization import organization_views
from shoppingmall.views.admin import dashboard_views as admin_dashboard_views, category_views

router = routers.DefaultRouter()
router.register(r'user', shop_user_views.ShopUserViewSet, basename="users"),
router.register(r'product', product_views.ProductViewSet, basename="product"),
router.register(r'collection', collection_views.CollectionViewSet, basename="collection"),
router.register(r'category', seller_category_views.CategoryViewSet, basename="category"),
router.register(r'images', image_views.ImagesViewSet, basename="images"),
router.register(r'shop', shop_views.ShopViewSet, basename="shop"),
router.register(r'order', order_views.OrderViewSet, basename="order"),
router.register(r'dashboard', dashboard_views.DashboardViewSet, basename="dashboard"),

organization = routers.DefaultRouter()
organization.register(r'', organization_views.OrganizationViewSet, basename="organization"),

admin = routers.DefaultRouter()
admin.register(r'dashboard', admin_dashboard_views.DashboardViewSet, basename="dashboard"),
admin.register(r'category', category_views.CategoryViewSet, basename="category"),
admin.register(r'shop', shop_views.ShopViewSet, basename="shop"),
admin.register(r'organization', organization_views.OrganizationViewSet, basename="organization"),
admin.register(r'seller', shop_user_views.ShopUserViewSet, basename="seller"),
admin.register(r'customer', customer_views.CustomerViewSet, basename="customer"),
admin.register(r'province', province_views.ProvinceViewSet, basename="province"),

user = routers.DefaultRouter()
user.register(r'', shop_user_views.ShopUserViewSet, basename="organization"),

customer = routers.DefaultRouter()
customer.register(r'customer', customer_views.CustomerViewSet, basename="customer"),
customer.register(r'cart', cart_views.CartViewSet, basename="cart"),
customer.register(r'order', customer_order_views.OrderViewSet, basename="order"),
customer.register(r'product', customer_product_views.ProductViewSet, basename="product"),
customer.register(r'category', customer_category_views.CollectionViewSet, basename="category"),
customer.register(r'images', image_views.ImagesViewSet, basename="images"),
customer.register(r'shops', customer_shop_views.CustomerShopViewSet, basename="shop"),
customer.register(r'province', province_views.ProvinceViewSet, basename="province"),

urlpatterns = [
    path('seller/', include(router.urls)),
    path('admin/', include(admin.urls)),
    path('organization/', include(organization.urls)),
    path('user/', include(user.urls)),
    path('', include(customer.urls)),
]
