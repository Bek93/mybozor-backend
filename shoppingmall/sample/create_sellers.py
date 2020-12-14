# setup sys.path first if needed
import sys

# tell django which settings module to use
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
import sys

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)
os.environ['DJANGO_SETTINGS_MODULE'] = "annyongstore.settings.development"
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "annyongstore.settings.development")
import django

django.setup()

# import application models
import shoppingmall.models as m

# create and save db entries...

for i in range(1, 21):
    data = {
        "email": f"seller{i}@gmail.com",
        "username": f"seller{i}@gmail.com",
        "name": f"Seller {i}",
        "password": "12345678",
        "language": "uz",
        "is_shop_admin": True,

    }
    seller = m.Seller.objects.create(**data)
    seller.save()
