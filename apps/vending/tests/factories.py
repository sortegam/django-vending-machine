from _decimal import Decimal
from datetime import datetime

from factory import Faker
from apps.vending.models import Product, VendingMachineSlot, User
import factory


# This is a framework agnostic factory
class VendingMachineUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    username = "Tom Wambsgans"
    email = "tomlet@greggs.com"


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    id = Faker("uuid4")
    name = "Snickers Bar"
    price = Decimal("10.40")
    created_at = datetime(2023, 5, 30, 12)
    updated_at = datetime(2023, 5, 30, 23)


class VendingMachineSlotFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = VendingMachineSlot
