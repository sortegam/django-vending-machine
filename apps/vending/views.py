from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.views import APIView

from apps.vending.models import VendingMachineSlot, User
from apps.vending.serializers import VendingMachineSlotSerializer, UserSerializer
from apps.vending.validators import ListSlotsValidator


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
    def post(self, request: Request) -> Response:
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
            user_serializer = UserSerializer(user)
            return Response(status=status.HTTP_200_OK, data=user_serializer.data)
        except User.DoesNotExist:
            return Response(status=401, data="Bad credentials")


class BalanceViewSet(viewsets.ViewSet):
    def add(self, request: Request) -> Response:
        username = request.data.get('username')
        amount = request.data.get('amount')
        # TODO Validate amount
        try:
            user = User.objects.get(username=username)
            user.balance += amount
            user.save()
            return Response(status=status.HTTP_200_OK, data={"balance": user.balance})
        except User.DoesNotExist:
            return Response(status=401, data="Bad username")

    def refund(self, request: Request) -> Response:
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
            user.balance = 0
            user.save()
            return Response(status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(status=401, data="Bad username")


class BuyView(APIView):
    def post(self, request: Request) -> Response:
        username = request.data.get('username')
        slot_id = request.data.get('slot_id')
        try:
            user = User.objects.get(username=username)
            slot = VendingMachineSlot.objects.get(id=slot_id)
            product = slot.product
            final_balance = user.balance - product.price
            if slot.quantity == 0:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data="There are products left in the slot")
            if final_balance < 0:
                return Response(status=status.HTTP_406_NOT_ACCEPTABLE, data="Not enough balance to purchase")
            
            slot.quantity = -1
            user.balance = final_balance
            slot.save()
            user.save()
            
            return Response(status=status.HTTP_200_OK, data={"balance": user.balance})
        except VendingMachineSlot.DoesNotExist:
            return Response(status=400, data="Slot does not exist")
        except User.DoesNotExist:
            return Response(status=401, data="Bad credentials")
