# Generated by Django 3.1.1 on 2021-01-09 02:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingmall', '0024_auto_20201229_1749'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='overable',
            new_name='infinite',
        ),
    ]