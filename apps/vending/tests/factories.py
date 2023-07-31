import factory
from apps.vending.models import Product, VendingMachineSlot


class ProductFactory(factory.Factory):
    class Meta:
        model = Product


class VendingMachineSlotFactory(factory.Factory):
    class Meta:
        model = VendingMachineSlot
