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
        assert response.json() == "Bad credentials"

    def test_existent_user_returns_200_OK_with_user_found(self, client, existent_user):
        response = client.post(path="/login/", data={"username": "johndoe"})
        assert response.status_code == status.HTTP_200_OK
        expected_user_data = {
            "id": ANY,
            "username": "johndoe",
            "full_name": "John Doe",
            "balance": "10.00"
        }
        assert response.json() == expected_user_data

    def test_empty_user_returns_401(self, client, existent_user):
        response = client.post(path="/login/", data={"username": ""})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == "Bad credentials"


@pytest.mark.django_db
class TestBalanceViewSet:
    def test_unexistent_user_returns_401_unauthorized(self, client, existent_user):
        response = client.post(path="/login/", data={"username": "unknown"})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == "Bad credentials"

