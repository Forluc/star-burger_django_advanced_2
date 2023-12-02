from django.db import transaction
from rest_framework.serializers import ModelSerializer

from foodcartapp.models import OrderElement, Order


class OrderElementSerializer(ModelSerializer):
    class Meta:
        model = OrderElement
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderElementSerializer(many=True, allow_empty=False, write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'firstname', 'lastname', 'phonenumber', 'address', 'products']

    @transaction.atomic
    def create(self, validated_data):
        order = Order.objects.create(
            firstname=validated_data['firstname'],
            lastname=validated_data['lastname'],
            phonenumber=validated_data['phonenumber'],
            address=validated_data['address'],
        )

        products_fields = validated_data['products']

        products = [OrderElement(order=order, price=fields['product'].price * fields['quantity'], **fields) for fields
                    in products_fields]
        OrderElement.objects.bulk_create(products)

        return order
