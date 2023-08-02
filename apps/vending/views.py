import logging
from _decimal import Decimal

from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.vending.decorators import validate_username
from apps.vending.models import VendingMachineSlot, User
from apps.vending.serializers import VendingMachineSlotSerializer, UserSerializer
from apps.vending.validators import ListSlotsValidator, AmountValidator


class VendingMachineSlotView(APIView):
    def get(self, request: Request) -> Response:
        validator = ListSlotsValidator(data=request.query_params)
        validator.is_valid(raise_exception=True)
        filters = {}
        if quantity := validator.validated_data["quantity"]:
            filters["quantity__lte"] = quantity

        slots = VendingMachineSlot.objects.filter(**filters)
        slots_serializer = VendingMachineSlotSerializer(slots, many=True)
        return Response(data=slots_serializer.data)


class UserLoginView(APIView):
    @validate_username
    def post(self, request: Request, user) -> Response:
        try:
            user_serializer = UserSerializer(user)
            return Response(status=status.HTTP_200_OK, data=user_serializer.data)
        except User.DoesNotExist:
            return Response(status=401, data="Bad credentials")


class BalanceViewSet(viewsets.ViewSet):
    @validate_username
    def add(self, request: Request, user) -> Response:
        try:
            validator = AmountValidator(data=request.data)
            validator.is_valid(raise_exception=True)
            validated_amount = validator.validated_data.get("amount", 0)
            if user.balance + validated_amount >= 100:
                raise Exception('Vending machine does not support more than 99.99$')   
            user.balance += validated_amount
            user.save()
            return Response(status=status.HTTP_200_OK, data={"balance": user.balance})            
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"error": str(e)})

    @validate_username
    def refund(self, request: Request, user) -> Response:
        user.balance = 0
        user.save()
        return Response(status=status.HTTP_200_OK)


class BuyView(APIView):
    @validate_username
    def post(self, request: Request, user) -> Response:
        slot_id = request.data.get('slot_id')
        try:
            slot = VendingMachineSlot.objects.get(id=slot_id)
            product = slot.product
            final_balance = user.balance - product.price
            if slot.quantity == 0:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data="There are products left in the slot")
            if final_balance < 0:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data="Not enough balance to purchase")

            slot.quantity -= 1
            user.balance = final_balance
            slot.save()
            user.save()

            return Response(status=status.HTTP_200_OK, data={"balance": user.balance})
        except VendingMachineSlot.DoesNotExist:
            return Response(status=400, data="Slot does not exist")
