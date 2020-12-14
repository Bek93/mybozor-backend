from django.contrib import admin

# Register your models here.
from shoppingmall.models import User, Shop, ShopConfig

admin.site.register(User)
admin.site.register(Shop)
admin.site.register(ShopConfig)
