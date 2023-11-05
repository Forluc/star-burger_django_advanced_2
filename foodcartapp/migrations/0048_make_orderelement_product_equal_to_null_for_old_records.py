# Generated by Django 3.2.15 on 2023-11-05 15:16

from django.db import migrations, models
import django.db.models.deletion


def change_product(apps, _):
    OrderElement = apps.get_model("foodcartapp", "OrderElement")
    OrderElement.objects.filter(product__isnull=True).update(product=None)


class Migration(migrations.Migration):
    dependencies = [
        ('foodcartapp', '0047_alter_orderelement_product'),
    ]

    operations = [
        migrations.RunPython(change_product),
    ]