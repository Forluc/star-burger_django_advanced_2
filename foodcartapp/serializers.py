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
