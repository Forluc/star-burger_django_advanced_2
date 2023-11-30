from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class OrderQuerySet(models.QuerySet):
    def get_restaurants_for_order(self, all_restaurants):
        menu_items = RestaurantMenuItem.objects.filter(availability=True).select_related('restaurant', 'product')

        for order in self:
            suitable_restaurants = []
            for ordered_product in order.orders.all():
                suitable_restaurants.append(
                    [menu_item.restaurant for menu_item in menu_items
                     if ordered_product.product.id == menu_item.product.id]
                )
            capable_restaurants = []
            for restaurant in all_restaurants:
                amount = 0
                for avalable_restaurant in suitable_restaurants:
                    if restaurant in avalable_restaurant:
                        amount += 1
                if amount == len(suitable_restaurants):
                    capable_restaurants.append(restaurant)

            order.selected_restaurants = capable_restaurants
        return self


class Order(models.Model):
    class StatusChoice(models.TextChoices):
        MANAGER = 'M', 'Передан менеджеру'
        RESTAURANT = 'R', 'Передан ресторану'
        COURIER = 'C', 'Передан курьеру'
        PROCESSED = 'P', 'Обработанный'

    class PaymentChoice(models.TextChoices):
        CASH = 'C', 'Наличные'
        NONCASH = 'N', 'Безналичные'

    status = models.CharField(verbose_name='Статус заказа', max_length=2, choices=StatusChoice.choices,
                              db_index=True, default=StatusChoice.MANAGER)
    payment = models.CharField(verbose_name='Способ оплаты', max_length=2, choices=PaymentChoice.choices,
                               db_index=True, default=PaymentChoice.CASH)
    restaurant = models.ForeignKey('Restaurant', verbose_name='Ресторан', on_delete=models.CASCADE, blank=True,
                                   null=True, related_name='restaurants')
    firstname = models.CharField(verbose_name='Имя', max_length=20)
    lastname = models.CharField(verbose_name='Фамилия', max_length=20)
    phonenumber = PhoneNumberField(verbose_name='Телефон', db_index=True)
    address = models.TextField(verbose_name='Адрес доставки')

    comment = models.TextField(verbose_name='Комментарий', blank=True)
    registered_at = models.DateTimeField('Зарегистрирован в', default=timezone.now)
    called_at = models.DateTimeField('Позвонили в', db_index=True, null=True, blank=True)
    delivered_at = models.DateTimeField('Доставлен в', db_index=True, null=True, blank=True)

    objects = OrderQuerySet.as_manager()

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'{self.firstname} {self.lastname} {self.address}'


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name='ресторан',
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',

    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f'{self.restaurant.name} - {self.product.name}'


class OrderElement(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, verbose_name='Заказ', related_name='orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Товар', related_name='products')
    quantity = models.IntegerField('Количество', validators=[MinValueValidator(0), MaxValueValidator(20)])
    price = models.DecimalField('Цена заказа', max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])

    class Meta:
        verbose_name = 'Элемент заказа'
        verbose_name_plural = 'Элементы заказа'

    def __str__(self):
        return f'{self.order}-{self.product}'
