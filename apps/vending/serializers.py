from rest_framework import serializers

from apps.vending.models import User, VendingMachineSlot, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'name', 'price')


class VendingMachineSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendingMachineSlot
        fields = ('id', 'quantity', 'product', 'coordinates')

    coordinates = serializers.SerializerMethodField()

    def get_coordinates(self, instance) -> list[int, int]:
        return [instance.column, instance.row]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'full_name', 'balance')


