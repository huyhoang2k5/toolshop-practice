"""Buoi 2 - API testing with APIRequestContext (not the requests library).

Fixtures you can use (see conftest.py): api, test_user, auth_token, auth_headers
Helpers: register_user(api, email, password), new_email(), strong_password()

Run:  pytest tests/buoi2/test_b2_api.py -v
"""
import json
from pathlib import Path

import pytest

from conftest import new_email, register_user, strong_password  # noqa: F401  (you will need them)

KEYWORDS = json.loads((Path(__file__).parents[2] / "data" / "search_keywords.json").read_text())


# ---------------------------------------------------------------- B2.1 (together)
@pytest.mark.smoke
@pytest.mark.api
def test_b2_1_status_returns_toolshop(api):
    """Goal: API is alive. Precondition: none. Expected: 200 and app_name Toolshop."""
    response = api.get("/status")
    assert response.status == 200, response.text()
    assert response.json()["app_name"] == "Toolshop"



# ---------------------------------------------------------------- B2.2
@pytest.mark.api
def test_b2_2_products_first_page_has_pagination_and_product_shape(api):
    """Check pagination and product JSON structure."""

    response = api.get("/products")
    assert response.status == 200, response.text()

    body = response.json()

    required_keys = {
        "current_page",
        "data",
        "per_page",
        "total",
        "last_page",
    }
    assert required_keys.issubset(body.keys())

    products = body["data"]
    assert isinstance(products, list)
    assert 0 < len(products) <= body["per_page"]

    for product in products:
        assert isinstance(product["id"], (str, int))
        assert isinstance(product["name"], str)
        assert product["name"].strip()
        assert float(product["price"]) > 0




# ---------------------------------------------------------------- B2.3 data-driven
@pytest.mark.api
@pytest.mark.parametrize("case", KEYWORDS, ids=[c["keyword"] for c in KEYWORDS])
def test_b2_3_search_api_returns_only_matching_names(api, case):
    """Verify that search results match the keyword."""

    keyword = case["keyword"]
    expected = case["must_contain"]

    response = api.get("/products/search", params={"q": keyword})

    assert response.status == 200, response.text()

    body = response.json()
    products = body["data"]

    assert len(products) > 0, f"No products found for: {keyword}"

    for product in products:
        name = product["name"].lower()
        assert expected.lower() in name, (
            f"Product '{name}' does not contain '{expected}'"
        )




# ---------------------------------------------------------------- B2.4a
@pytest.mark.api
@pytest.mark.parametrize(
    "endpoint, expected_status",
    [
        ("/users/me", 401),
        ("/products/does-not-exist", 404),
    ],
)
def test_b2_4a_protected_or_missing_resource_returns_4xx(
    api, endpoint, expected_status
):
    """Verify unauthorized access and missing resources."""

    response = api.get(endpoint)

    assert response.status == expected_status, (
        f"Expected {expected_status}, "
        f"but got {response.status}: {response.text()}"
    )




@pytest.mark.api
def test_b2_4b_register_empty_body_returns_422_with_field_errors(api):
    """Verify registration rejects an empty JSON body."""

    response = api.post("/users/register", data={})

    assert response.status == 422, response.text()

    body = response.json()

    assert isinstance(body, dict)

    required_fields = [
        "first_name",
        "last_name",
        "email",
        "password",
    ]

    for field in required_fields:
        assert field in body, f"Missing validation error: {field}"
        assert isinstance(body[field], list)
        assert len(body[field]) > 0
        assert all(
            isinstance(message, str) and message.strip()
            for message in body[field]
        )




@pytest.mark.api
def test_b2_4c_register_leaked_password_is_rejected(api):
    """Verify that a known leaked password is rejected."""

    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": new_email(),
        "password": "Welcome01!",
    }

    response = api.post("/users/register", data=user_data)

    assert response.status == 422, response.text()

    body = response.json()

    assert isinstance(body, dict)
    assert "password" in body, (
        f"Expected password validation error, got: {body}"
    )
    assert body["password"], "Password error message is empty"




# ---------------------------------------------------------------- B2.5a
@pytest.mark.api
def test_b2_5a_users_me_with_token_returns_own_profile(
    api, auth_headers, test_user
):
    """Verify Bearer Token authentication and user profile."""

    response = api.get("/users/me", headers=auth_headers)

    assert response.status == 200, response.text()

    body = response.json()

    assert isinstance(body, dict)
    assert "email" in body

    assert body["email"].lower() == test_user["email"].lower(), (
        f"Expected {test_user['email']}, "
        f"but received {body['email']}"
    )




# ---------------------------------------------------------------- B2.5b
@pytest.mark.api
def test_b2_5b_register_response_does_not_expose_password(api):
    """Verify registration response does not expose passwords."""

    password = strong_password()

    user_data = {
        "first_name": "Test",
        "last_name": "User",
        "email": new_email(),
        "password": password,
    }

    response = api.post("/users/register", data=user_data)

    assert response.status == 201, response.text()

    body = response.json()

    assert isinstance(body, dict)

    assert "password" not in body, (
        "Security issue: password field exposed in response"
    )

    assert password not in response.text(), (
        "Security issue: plaintext password exposed"
    )




# ---------------------------------------------------------------- B2.6 your own fixture
@pytest.fixture
def new_cart(api):
    response = api.post("/carts")
    assert response.status == 201, response.text()
    return response.json()["id"]


def test_b2_6_cart_add_product_quantity_two_is_stored(api, new_cart):
    """Verify adding a product with quantity 2."""

    # Get the first available product
    response = api.get("/products")
    assert response.status == 200, response.text()

    products = response.json()["data"]
    assert len(products) > 0

    product_id = products[0]["id"]

    # Add two units of the product to the new cart
    response = api.post(
        f"/carts/{new_cart}",
        data={
            "product_id": product_id,
            "quantity": 2,
        },
    )

    assert response.status in (200, 201), response.text()
    
    # Read the cart to verify stored data
    response = api.get(f"/carts/{new_cart}")

    assert response.status == 200, response.text()

    cart = response.json()
    items = cart["cart_items"]

    assert len(items) == 1, (
        f"Expected 1 cart item, got {len(items)}"
    )

    item = items[0]

    assert int(item["quantity"]) == 2
    assert str(item["product_id"]) == str(product_id)


