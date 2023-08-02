from rest_framework import serializers


class ListSlotsValidator(serializers.Serializer):
    quantity = serializers.IntegerField(required=False, min_value=0, default=None)


class AmountValidator(serializers.Serializer):
    amount = serializers.DecimalField(required=True, min_value=0, max_value=99.99, decimal_places=2, max_digits=4)
