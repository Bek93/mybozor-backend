# Generated by Django 3.1.1 on 2020-12-26 06:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shoppingmall', '0015_announcement_total_target_count'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seller',
            name='age',
        ),
        migrations.RemoveField(
            model_name='seller',
            name='gender',
        ),
        migrations.RemoveField(
            model_name='seller',
            name='province',
        ),
        migrations.AddField(
            model_name='seller',
            name='is_shop_owner',
            field=models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='shop_owner_status'),
        ),
    ]