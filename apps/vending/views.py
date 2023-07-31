from rest_framework import status
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


class UserView(APIView):
    def post(self, request: Request) -> Response:
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
            serializer = UserSerializer(user)
            return Response(status=status.HTTP_200_OK, data=serializer.data)
        except User.DoesNotExist:
            return Response(status=401, data="Bad credentials")
        
