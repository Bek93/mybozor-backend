def receipt_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'shop_{}/receipt/{}'.format(instance.shop.id, filename)


def customer_address_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'customer/address/{}_{}'.format(instance.id, filename)


def shop_photo_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'shop_{}/{}'.format(instance.shop.id, filename)


def photo_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return 'shop_{}/collection/{}'.format(instance.shop.id, filename)


def product_photo_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/user_<id>/<filename>
    return '{}/product/{}'.format(instance.shop.id, filename)