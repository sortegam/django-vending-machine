import uuid
from _decimal import Decimal
from unittest.mock import ANY

import pytest
from apps.vending.tests.factories import ProductFactory, VendingMachineSlotFactory, UserFactory
from rest_framework import status

from apps.vending.models import Product, VendingMachineSlot, User


@pytest.fixture
def products_list() -> list[Product]:
    return [ProductFactory(name=f"Product {i}") for i in range(1, 11)]


@pytest.fixture
def slots_grid(products_list) -> list[VendingMachineSlot]:
    """returns a grid of slots of 5x2"""
    slots = []
    for row in range(1, 3):
        for column in range(1, 6):
            slot = VendingMachineSlotFactory(
                product=products_list.pop(), row=row, column=column, quantity=column-1
            )
            slots.append(slot)
    return slots



@pytest.fixture
def existent_user() -> User:
    return UserFactory()

@pytest.mark.django_db
class TestListVendingMachineSlots:
    def test_list_slots_returns_expected_response(self, client, slots_grid):
        
        response = client.get("/slots/")
        
        expected_response = [
            {
                "id": ANY,
                "quantity": 0,
                "coordinates": [1, 1],
                "product": {"id": ANY, "name": "Product 10", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 1,
                "coordinates": [2, 1],
                "product": {"id": ANY, "name": "Product 9", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 2,
                "coordinates": [3, 1],
                "product": {"id": ANY, "name": "Product 8", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 3,
                "coordinates": [4, 1],
                "product": {"id": ANY, "name": "Product 7", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 4,
                "coordinates": [5, 1],
                "product": {"id": ANY, "name": "Product 6", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 0,
                "coordinates": [1, 2],
                "product": {"id": ANY, "name": "Product 5", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 1,
                "coordinates": [2, 2],
                "product": {"id": ANY, "name": "Product 4", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 2,
                "coordinates": [3, 2],
                "product": {"id": ANY, "name": "Product 3", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 3,
                "coordinates": [4, 2],
                "product": {"id": ANY, "name": "Product 2", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 4,
                "coordinates": [5, 2],
                "product": {"id": ANY, "name": "Product 1", "price": "10.40"},
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_response

    def test_invalid_quantity_filter_returns_bad_request(self, client):
        response = client.get("/slots/?quantity=-1")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"quantity": ["Ensure this value is greater than or equal to 0."]}

    def test_list_slots_returns_filtered_response(self, client, slots_grid):
        response = client.get("/slots/?quantity=1")

        expected_response = [
            {
                "id": ANY,
                "quantity": 0,
                "coordinates": [1, 1],
                "product": {"id": ANY, "name": "Product 10", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 1,
                "coordinates": [2, 1],
                "product": {"id": ANY, "name": "Product 9", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 0,
                "coordinates": [1, 2],
                "product": {"id": ANY, "name": "Product 5", "price": "10.40"},
            },
            {
                "id": ANY,
                "quantity": 1,
                "coordinates": [2, 2],
                "product": {"id": ANY, "name": "Product 4", "price": "10.40"},
            },
        ]

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected_response

@pytest.mark.django_db
class TestUserLoginView:
    def test_unexistent_user_returns_401_unauthorized(self, client, existent_user):
        response = client.post(path="/login/", data={"username": "unknown"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"error": "Bad credentials"}

    def test_existent_user_returns_200_OK_with_user_found(self, client, existent_user):
        response = client.post(path="/login/", data={"username": "johndoe"})
        assert response.status_code == status.HTTP_200_OK
        expected_user_data = {
            "id": ANY,
            "username": "johndoe",
            "full_name": "John Doe",
            "balance": "50.00"
        }
        assert response.json() == expected_user_data

    def test_empty_user_returns_401(self, client, existent_user):
        response = client.post(path="/login/", data={"username": ""})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"error": "Bad credentials"}


@pytest.mark.django_db
class TestBalanceViewSet:
    def test_balance_drops_to_0_when_refund_is_called(self, client, existent_user):
        assert existent_user.balance > Decimal("0")
        response = client.post(path="/balance/refund/", data={"username": existent_user.username})
        assert response.status_code == status.HTTP_200_OK
        existent_user.refresh_from_db()
        assert existent_user.balance == Decimal("0")
        
    def test_balance_adds_normally_money(self, client, existent_user):
        assert existent_user.balance == Decimal("50")
        response = client.post(path="/balance/add/", data={"username": existent_user.username, "amount": 2.5})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"balance": 52.5} 
        existent_user.refresh_from_db()
        assert existent_user.balance == Decimal("52.5")
        
    def test_balance_can_not_add_a_huge_amount(self, client, existent_user):
        assert existent_user.balance == Decimal("50")
        response = client.post(path="/balance/add/", data={"username": existent_user.username, "amount": 400})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        existent_user.refresh_from_db()
        assert existent_user.balance == Decimal("50")

    def test_balance_can_not_bypass_the_maximum_balance_of_99_99(self, client, existent_user):
        assert existent_user.balance == Decimal("50")
        response = client.post(path="/balance/add/", data={"username": existent_user.username, "amount": 49.99})
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"balance": 99.99}
        existent_user.refresh_from_db()
        assert existent_user.balance == Decimal("99.99")
        response = client.post(path="/balance/add/", data={"username": existent_user.username, "amount": 0.1})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "Vending machine does not support more than 99.99$"}
        existent_user.refresh_from_db()
        assert existent_user.balance == Decimal("99.99")
        
    def test_balance_can_not_add_negative_numbers(self, client, existent_user):
        assert existent_user.balance == Decimal("50")
        response = client.post(path="/balance/add/", data={"username": existent_user.username, "amount": -5})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        existent_user.refresh_from_db()
        assert existent_user.balance == Decimal("50")


@pytest.mark.django_db
class TestBuyView:
    def test_it_buys_something_normally(self, client, slots_grid, existent_user):
        slot_to_purchase = slots_grid[2]
        assert existent_user.balance == Decimal("50")
        assert slot_to_purchase.quantity == 2
        response = client.post(path="/buy/", data={"username": existent_user.username, "slot_id": slot_to_purchase.id})
        assert response.status_code == status.HTTP_200_OK
        existent_user.refresh_from_db()
        slot_to_purchase.refresh_from_db()
        assert existent_user.balance == Decimal("50") - Decimal(slot_to_purchase.product.price)
        assert slot_to_purchase.quantity == 1
        
    def test_does_not_allow_to_buy_if_user_balance_is_not_enough(self, client, slots_grid, existent_user):
        slot_to_purchase = slots_grid[2]
        existent_user.balance = Decimal("1")
        existent_user.save()
        response = client.post(path="/buy/", data={"username": existent_user.username, "slot_id": slot_to_purchase.id})
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert response.json() == {"error": "Not enough balance to purchase"}
        existent_user.refresh_from_db()
        slot_to_purchase.refresh_from_db()
        assert existent_user.balance == Decimal("1")
        assert slot_to_purchase.quantity == 2
        
    def test_does_not_allow_to_buy_if_the_slot_is_empty(self, client, slots_grid, existent_user):
        slot_to_purchase = slots_grid[0]
        assert existent_user.balance == Decimal("50")
        response = client.post(path="/buy/", data={"username": existent_user.username, "slot_id": slot_to_purchase.id})
        assert response.status_code == status.HTTP_406_NOT_ACCEPTABLE
        assert response.json() == {"error": "There are products left in the slot"}
        existent_user.refresh_from_db()
        slot_to_purchase.refresh_from_db()
        assert existent_user.balance == Decimal("50")
        assert slot_to_purchase.quantity == 0

    def test_returns_an_error_if_slot_to_but_does_not_exists(self, client, slots_grid, existent_user):
        assert existent_user.balance == Decimal("50")
        response = client.post(path="/buy/", data={"username": existent_user.username, "slot_id": uuid.uuid4()})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == {"error": "Slot does not exist"}
        existent_user.refresh_from_db()
        assert existent_user.balance == Decimal("50")
