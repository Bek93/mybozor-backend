import uuid

from django.conf import settings
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.core.exceptions import ValidationError
from django.utils import timezone

from django.db import models

LANGUAGE = (
    ('en', 'English'),
    ('ru', 'Russian'),
    ('uz', 'Uzbek'),
    ('kr', 'Korean')
)
GENDER = (
    ('male', 'Male'),
    ('female', 'Female'),
)
FILTER_TYPE = (
    ('all', 'All'),
    ('filter', 'Filter'),
)
CUSTOMERS = (
    ('telegram', 'Telegram'),
    ('app', 'App')
)

INVOICE_STATUS = (
    ('unpaid', 'Unpaid'),
    ('paid', 'Paid'),
    ('cancel', 'Cancel'),
)
ORDER_STATUS = (
    ('P', 'Pending'),
    ('A', 'Accepted'),
    ('C', 'Cancel'),
)

DELIVERY_STATUS = (
    ('P', 'Preparing'),
    ('S', 'Sent'),
)

SHOP_STATUS = (
    ('pending', 'Pending'),
    ('approved', 'Approved'),
)
SELL_OPTIONS = (
    ('self-service', 'Self-Service'),
    ('universal', 'Universal'),
)

ORDER_PAYMENT = (
    ('paid', 'Paid'),
    ('unpaid', 'UnPaid'),
)

QUANTITY_UNIT = (
    ('', ''),
    ('kg', 'kg'),
    ('pc', 'pc'),
)

ANNOUNCEMENT_UNIT = (
    ('message', 'message'),
    ('image', 'image'),
    ('video', 'Video'),
    ('product', 'Product'),
)

CURRENCY = (
    ('', ''),
    ('KRW', 'KRW'),
    ('USD', 'USD'),
    ('UZS', 'UZS'),
)
LOCALIZE = (
    ('classification', 'Classification'),
    ('category', 'Category'),
    ('subproduct', 'Subproduct'),
    ('product', 'Product'),
    ('collection', 'Collection'),
)
collection_IMAGE_CHOICES = (
    ('app', 'app'),
    ('telegram', 'telegram'),
)

LABEL_CHOICES = (
    ('N', 'New'),
    ('S', 'Sale')
)
IMAGE_TYPE = (
    ('product', 'Product'),
    ('collection', 'Collection')
)

ORDER_TYPE = (
    ('T', 'Telegram'),
    ('A', 'App'),
    ('D', 'Dashboard')
)

SERVER_TYPE = (
    ('T', 'Telegram'),
    ('A', 'App'),
    ('D', 'Dashboard')
)
METHOD = (
    ('GET', 'GET'),
    ('POST', 'POST'),
    ('PUT', 'PUT'),
    ('DELETE', 'DELETE')
)


# Create your models here.


class UserManager(BaseUserManager):
    """Custom manager for User."""

    def _create_user(self, username, password,
                     is_staff, is_admin, **extra_fields):
        now = timezone.now()
        is_active = extra_fields.pop("is_active", True)
        user = Admin(is_active=is_active, last_login=now, username=username,
                     date_joined=now, **extra_fields)
        if not is_admin:
            user = self.model(is_staff=is_staff, is_active=is_active, last_login=now,
                              is_admin=is_admin,
                              username=username,
                              date_joined=now, **extra_fields)

        if password is None or len(password) <= 7:
            raise ValidationError("password is required and it should be more then 7 chars")
        user.set_password(password)
        user.save(using=self._db)
        return user

    # def _app_create_user(self, username, password,
    #                      is_staff, is_admin, **extra_fields):
    #     now = timezone.now()
    #     is_active = extra_fields.pop("is_active", True)
    #     user = self.model(is_staff=is_staff, is_active=is_active, last_login=now,
    #                       is_admin=is_admin,
    #                       username=username,
    #                       date_joined=now, **extra_fields)
    #     if not is_admin:
    #         user = self.model(is_staff=is_staff, is_active=is_active, last_login=now,
    #                           is_admin=is_admin,
    #                           username=username,
    #                           date_joined=now, **extra_fields)
    #
    #     if password is None or len(password) <= 7:
    #         raise ValidationError("password is required and it should be more then 4 chars")
    #     user.set_password(password)
    #     user.save(using=self._db)
    #     return user

    # def create_user(self, username, image, phone, password=None, **extra_fields):
    #     is_staff = extra_fields.pop("is_staff", False)
    #     return self._create_user(username=username, password=password,
    #                              image=image, phone=phone, is_staff=is_staff,
    #                              is_admin=False,
    #                              **extra_fields)

    def create_shop_owner(self, username, password=None, **extra_fields):
        # is_staff = extra_fields.pop("is_staff", False)
        now = timezone.now()
        is_active = extra_fields.pop("is_active", True)
        user = self.model(is_active=is_active, last_login=now,
                          username=username,
                          date_joined=now, **extra_fields)
        if password is None or len(password) <= 7:
            raise ValidationError("password is required and it should be more then 7 chars")
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_customer(self, username, password=None, **extra_fields):
        now = timezone.now()
        is_active = extra_fields.pop("is_active", True)
        user = self.model(is_active=is_active, last_login=now,
                          username=username,
                          date_joined=now, **extra_fields)
        if password is None or len(password) <= 7:
            raise ValidationError("password is required and it should be more then 7 chars")
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password, **extra_fields):
        now = timezone.now()
        is_active = extra_fields.pop("is_active", True)
        user = Admin(is_active=is_active, last_login=now, is_admin=True, is_staff=True, name="Admin",
                     email="mybozor@mybozor.com",
                     username=username,
                     date_joined=now, **extra_fields)

        if password is None or len(password) <= 7:
            raise ValidationError("password is required and it should be more then 7 chars")
        user.set_password(password)
        user.save(using=self._db)
        return user


def shop_photo_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'shop_{}/{}'.format(instance.shop.id, filename)


class User(AbstractBaseUser):
    is_active = models.BooleanField('active', default=True, help_text=(
        'Designates whether this user should be treated as '
        'active. Unselect this instead of deleting accounts.'))

    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True, null=False)
    date_joined = models.DateTimeField('date_joined', default=timezone.now)
    # management
    objects = UserManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_full_name(self):
        """Return the email."""
        return self.name

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def is_admin(self):
        return hasattr(self, "admin")

    def is_seller(self):
        return hasattr(self, "seller")

    def is_customer(self):
        return hasattr(self, "customer")

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class Localize(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20, choices=LOCALIZE, blank=True)
    uz = models.TextField(blank=True)
    ru = models.TextField(blank=True)
    en = models.TextField(blank=True)
    kr = models.TextField(blank=True)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Province(models.Model):
    id = models.AutoField(primary_key=True)
    province = models.ForeignKey(Localize, on_delete=models.SET_NULL, null=True, related_name='province')
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Admin(User):
    is_admin = models.BooleanField(
        'admin_status', default=False, help_text=(
            'Designates whether the user can log into this admin site.'))

    is_staff = models.BooleanField(
        'staff_status', default=False, help_text=(
            'Designates whether the user can log into this admin site.'))
    email = models.CharField(max_length=100, unique=True, null=True)
    name = models.CharField(max_length=100, null=False, blank=False)


def user_profilepic_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    if instance.is_app_user:
        return 'user_{0}/address/{1}'.format(instance.username, filename)
    else:
        return 'user_{0}/{1}'.format(instance.username, filename)


class ShopConfig(models.Model):
    id = models.AutoField(primary_key=True)
    telegram_store = models.TextField(blank=True)
    telegram_new_order = models.TextField(blank=True)
    telegram_accept = models.TextField(blank=True)
    sms_enabled = models.BooleanField(default=False)
    telegram_enabled = models.BooleanField(default=False)
    app_enabled = models.BooleanField(default=False)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Shop(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=100, blank=False, null=False)
    country = models.CharField(max_length=100, blank=False, null=False)
    province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=100, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    bank = models.TextField(blank=False, null=False)
    address = models.TextField(blank=True, null=True)
    phone_number = models.TextField(blank=True, null=True)
    image = models.ImageField(null=True, upload_to=shop_photo_directory_path)
    currency = models.CharField(max_length=10, choices=CURRENCY, default="KRW")
    status = models.CharField(max_length=8, choices=SHOP_STATUS, default='pending')
    sell_option = models.CharField(max_length=20, choices=SELL_OPTIONS, default='universal')
    config = models.ForeignKey(ShopConfig, on_delete=models.SET_NULL, null=True)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Seller(User):
    is_shop_admin = models.BooleanField(
        'shop_admin_status', default=False, help_text=(
            'Designates whether the user can log into this admin site.'))

    is_shop_staff = models.BooleanField(
        'shop_staff_status', default=False, help_text=(
            'Designates whether the user can log into this admin site.'))
    is_shop_owner = models.BooleanField(
        'shop_owner_status', default=False, help_text=(
            'Designates whether the user can log into this admin site.'))
    email = models.CharField(max_length=100, unique=True, null=False)
    name = models.CharField(max_length=100, null=False, blank=False)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True, blank=True)
    language = models.CharField(max_length=5, choices=LANGUAGE, default="uz")


class Classification(models.Model):
    id = models.AutoField(primary_key=True)
    titles = models.ForeignKey(Localize, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    referral_rate = models.FloatField(default=0.0)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Category(models.Model):
    id = models.AutoField(primary_key=True)
    classification = models.ForeignKey(Classification, on_delete=models.SET_NULL, null=True)
    titles = models.ForeignKey(Localize, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Subproduct(models.Model):
    id = models.AutoField(primary_key=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    titles = models.ForeignKey(Localize, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField('date_created', default=timezone.now)


def customer_address_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'customer/address/{}_{}'.format(instance.id, filename)


class Customer(User):
    name = models.CharField(max_length=100, null=False, blank=False)
    phone_number = models.CharField(max_length=100, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    type = models.CharField(max_length=10, choices=CUSTOMERS, default="telegram")
    province = models.ForeignKey(Province, on_delete=models.CASCADE, blank=True, null=True)
    age = models.IntegerField(default=0, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER, blank=True)
    address = models.CharField(null=True, max_length=255, blank=True)
    address_image = models.ImageField(null=True, upload_to=customer_address_directory_path)
    language = models.CharField(max_length=5, choices=LANGUAGE, default="uz")
    deleted = models.BooleanField(default=False)


class Collection(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    parent_id = models.IntegerField(default=0)
    titles = models.ForeignKey(Localize, on_delete=models.SET_NULL, null=True)
    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    titles = models.ForeignKey(Localize, on_delete=models.SET_NULL, null=True, related_name='titles')
    descriptions = models.ForeignKey(Localize, on_delete=models.SET_NULL, null=True, related_name='descriptions')
    subproduct = models.ForeignKey(Subproduct, on_delete=models.SET_NULL, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True)
    condition = models.CharField(max_length=100, blank=True)
    brand = models.CharField(max_length=100, blank=True)
    made_in = models.CharField(max_length=100, blank=True)
    buying = models.IntegerField(default=0)
    selling = models.IntegerField(default=0)
    referral_fee = models.IntegerField(default=0)
    quantity = models.IntegerField(default=0)
    infinite = models.BooleanField(default=False)
    has_delivery_fee = models.BooleanField(default=False)
    label = models.CharField(max_length=10, choices=LABEL_CHOICES, blank=True)
    unit = models.CharField(max_length=10, choices=QUANTITY_UNIT, blank=True)
    currency = models.CharField(max_length=10, choices=CURRENCY, default="KRW")
    has_option = models.BooleanField(default=False)
    banner = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)
    data = models.TextField(blank=True)
    date_created = models.DateTimeField('date_created', default=timezone.now)
    date_modified = models.DateTimeField('date_modified', default=timezone.now)


def photo_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'shop_{}/collection/{}'.format(instance.shop.id, filename)


def product_photo_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{}/product/{}'.format(instance.shop.id, filename)


class DeliveryPolicy(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    unit_from = models.IntegerField(default=0)
    unit_to = models.IntegerField(default=0)
    fee = models.IntegerField(default=0.0)
    currency = models.CharField(max_length=10, choices=CURRENCY, default="KRW")
    comment = models.TextField(blank=True)
    date_created = models.DateTimeField('date_created', default=timezone.now)

    class Meta:
        unique_together = ('shop', 'unit_from')


class Images(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True)
    type = models.CharField(max_length=20, choices=IMAGE_TYPE)
    image = models.ImageField(null=True, upload_to=photo_directory_path)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class ProductImages(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(null=True, upload_to=product_photo_directory_path)
    is_main = models.BooleanField(default=False)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class CollectionImages(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='collection')
    telegram_image = models.ImageField(null=True, upload_to=photo_directory_path)
    app_image = models.ImageField(null=True, upload_to=photo_directory_path)
    language = models.CharField(max_length=10, blank=True, choices=LANGUAGE)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Options(models.Model):
    id = models.AutoField(primary_key=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='option')
    buying = models.FloatField(default=0.0)
    selling = models.FloatField(default=0.0)
    quantity = models.IntegerField(default=0)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class OptionValue(models.Model):
    id = models.AutoField(primary_key=True)
    option = models.ForeignKey(Options, on_delete=models.CASCADE, related_name='option')
    title = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Cart(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Customer, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, null=True, blank=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    option = models.ForeignKey(Options, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.IntegerField(blank=False)
    date_created = models.DateTimeField('date_created', default=timezone.now)


def receipt_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    # filenames = filename.split(".")
    # filename = f"{instance.order_number}.{filenames[1]}"
    return 'shop_{}/receipt/{}/{}'.format(instance.shop.id, instance.order_number, filename)


class Invoice(models.Model):
    id = models.AutoField(primary_key=True)
    invoice_number = models.CharField(max_length=20, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    month = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='unpaid')
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Order(models.Model):
    id = models.AutoField(primary_key=True)
    order_number = models.CharField(max_length=100, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=ORDER_TYPE, blank=True)
    # user info
    name = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=100, blank=True)
    address = models.TextField(blank=True)
    address_image = models.URLField(blank=True)
    language = models.CharField(max_length=5, choices=LANGUAGE, default="uz")

    # price info
    total_buying = models.IntegerField(default=0)
    total_selling = models.IntegerField(default=0)
    delivery_fee = models.IntegerField(default=0)
    total_referral_fee = models.FloatField(default=0.0)
    # delivery
    posting_date = models.DateField(max_length=20, blank=True, null=True)
    shipping_date = models.DateField(max_length=20, blank=True, null=True)
    post_code = models.CharField(max_length=100, blank=True)
    delivery_comment = models.TextField(blank=True)

    # status
    status = models.CharField(max_length=100, choices=ORDER_STATUS, default='P')
    delivery = models.CharField(max_length=100, choices=DELIVERY_STATUS, blank=True, null=True)
    payment = models.CharField(max_length=100, choices=ORDER_PAYMENT, default='unpaid')
    deleted = models.BooleanField(default=False)
    # receipt
    is_paid = models.BooleanField(default=False)
    is_read = models.BooleanField(default=False)
    receipt = models.ImageField(null=True, upload_to=receipt_directory_path)

    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, blank=True, null=True)
    accepted_by = models.IntegerField(blank=True, null=True)
    # date
    date_created = models.DateTimeField('date_created', default=timezone.now)


class OrderedProduct(models.Model):
    id = models.AutoField(primary_key=True)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    option = models.ForeignKey(Options, null=True, blank=True, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    buying = models.FloatField(default=0.0)
    selling = models.FloatField(default=0.0)
    referral_fee = models.FloatField(default=0.0)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Logs(models.Model):
    id = models.AutoField(primary_key=True)
    request_size = models.FloatField(default=0.0)
    response_size = models.FloatField(default=0.0)
    status_code = models.IntegerField(default=0)
    server_type = models.CharField(max_length=10, choices=SERVER_TYPE)
    method = models.CharField(max_length=10, choices=METHOD)
    path = models.CharField(max_length=250)
    data_string = models.TextField(blank=True)
    payload_string = models.TextField(blank=True)
    shop_id = models.CharField(max_length=100)
    user_id = models.IntegerField(default=0)
    customer_id = models.IntegerField(default=0)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class ProductView(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class ShopView(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Contract(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(Admin, on_delete=models.CASCADE)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    referral_rate = models.FloatField(0.0)
    date_created = models.DateTimeField('date_created', default=timezone.now)


def announcement_image_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'shop_{}/announcement/image/{}'.format(instance.shop.id, filename)


def announcement_video_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'shop_{}/announcement/video/{}'.format(instance.shop.id, filename)


class Filter(models.Model):
    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=10, choices=FILTER_TYPE, default="all")
    province = models.IntegerField(null=True)
    language = models.CharField(max_length=5, choices=LANGUAGE, null=True)
    gender = models.CharField(max_length=10, choices=GENDER, null=True)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class Announcement(models.Model):
    id = models.AutoField(primary_key=True)
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, blank=True)
    type = models.CharField(max_length=10, choices=ANNOUNCEMENT_UNIT, blank=True)
    filter = models.ForeignKey(Filter, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, blank=True, null=True)
    titles = models.ForeignKey(Localize, on_delete=models.SET_NULL, null=True, related_name='announcement_titles')
    descriptions = models.ForeignKey(Localize, on_delete=models.SET_NULL, null=True,
                                     related_name='announcement_descriptions')
    image = models.ImageField(null=True, upload_to=announcement_image_directory_path)
    is_completed = models.BooleanField(default=False)
    total_target_count = models.IntegerField(blank=True, null=True)
    started_at = models.DateTimeField('start_at', blank=True, null=True)
    ended_at = models.DateTimeField('end_at', blank=True, null=True)
    date_created = models.DateTimeField('date_created', default=timezone.now)


class DeliveredAnnouncement(models.Model):
    id = models.AutoField(primary_key=True)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)
    is_sent = models.BooleanField(default=False)
    is_failed = models.BooleanField(default=False)
    date_created = models.DateTimeField('date_created', default=timezone.now)
