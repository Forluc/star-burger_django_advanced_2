from django.http import JsonResponse
from django.shortcuts import render
from django.templatetags.static import static
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Order, Product, OrderElements


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    request = request.data
    if not request.get('products'):
        return Response({'error': 'Products is empty or null or does not exist'}, status=status.HTTP_400_BAD_REQUEST)
    elif not isinstance(request.get('products'), list):
        return Response({'error': 'Products is not a list'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        order = Order.objects.create(
            firstname=request.get('firstname'),
            lastname=request.get('lastname'),
            phone_number=request.get('phonenumber'),
            address=request.get('address'),
        )

        for product in request.get('products'):
            OrderElements.objects.create(
                order=order,
                product=Product.objects.get(id=product.get('product')),
                count=product.get('quantity'),
            )
        return Response({'Status': '200'})
    except ValueError:
        return Response({'error': 'ValueError'}, status=status.HTTP_400_BAD_REQUEST)
