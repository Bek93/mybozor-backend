# Generated by Django 3.1.1 on 2020-12-14 01:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingmall', '0007_auto_20201214_1003'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='discount',
            new_name='referral_fee',
        ),
        migrations.RemoveField(
            model_name='product',
            name='has_discount',
        ),
    ]