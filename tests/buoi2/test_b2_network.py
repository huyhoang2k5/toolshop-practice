"""Buoi 2 - route / mocking, and API + UI together.

Run:  pytest tests/buoi2/test_b2_network.py --headed
"""
import json
import re

import pytest  # noqa: F401
from playwright.sync_api import expect

from pages.account_page import AccountPage  # noqa: F401
from pages.home_page import HomePage  # noqa: F401

# Open DevTools > Network on the home page and look at how the product list is loaded:
#   PROD:   QUERY https://api.practicesoftwaretesting.com/products          (JSON body)
#   BUGGY:  GET   https://api-with-bugs.../products?between=price,1&page=1
# One regex catches both, and NOT /products/search or /products/{id}:
PRODUCT_LIST = re.compile(r"/products(\?.*)?$")
EMPTY_PAGE = {"current_page": 1, "data": [], "from": None, "last_page": 1,
              "per_page": 9, "to": None, "total": 0}



# ---------------------------------------------------------------- B2.7
def test_b2_7_home_without_images_still_lists_products(page):
    """Verify products remain visible when images are blocked."""

    blocked_images = []

    def block_image(route):
        blocked_images.append(route.request.url)
        route.abort()

    image_pattern = re.compile(
        r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$",
        re.IGNORECASE,
    )

    # Register route before navigation
    page.route(image_pattern, block_image)

    # Open Toolshop homepage
    page.goto("/")

    # Wait for product cards
    products = page.locator("[data-test='product-name']")
    products.first.wait_for(state="visible")

    assert products.count() > 0, "No products displayed"

    # Verify that image requests were blocked
    assert len(blocked_images) > 0, (
        "No image requests were intercepted"
    )




# ---------------------------------------------------------------- B2.8
def test_b2_8_home_with_empty_product_list_shows_no_results(page):
    """Verify empty product list displays the correct message."""

    mocked_requests = []

    def mock_empty_products(route):
        mocked_requests.append(route.request.url)
        route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps(EMPTY_PAGE),
        )

    # Register the mock before opening the page
    page.route(PRODUCT_LIST, mock_empty_products)

    # Open homepage
    page.goto("/")

    # Verify the empty-state message
    empty_message = page.get_by_text(
        "There are no products found.",
        exact=True,
    )
    expect(empty_message).to_be_visible()

    # Verify no product cards are displayed
    products = page.locator("[data-test='product-name']")
    expect(products).to_have_count(0)

    # Verify the mock was actually used
    assert len(mocked_requests) > 0, (
        "Product API request was not intercepted"
    )




# ---------------------------------------------------------------- B2.9
def test_b2_9_home_when_product_api_fails_page_stays_usable(page):
    """Verify homepage remains usable when product API returns 500."""

    mocked_requests = []

    def mock_server_error(route):
        mocked_requests.append(route.request.url)
        route.fulfill(
            status=500,
            content_type="application/json",
            body=json.dumps({"message": "Internal Server Error"}),
        )

    # Register mock before navigation
    page.route(PRODUCT_LIST, mock_server_error)

    # Open homepage
    page.goto("/")

    # Verify no product cards are displayed
    products = page.locator("[data-test='product-name']")
    expect(products).to_have_count(0)

    # Verify search box remains editable
    search_box = page.locator("[data-test='search-query']")
    expect(search_box).to_be_visible()
    expect(search_box).to_be_editable()

    search_box.fill("hammer")
    expect(search_box).to_have_value("hammer")

    # Verify API request was intercepted
    assert len(mocked_requests) > 0, (
        "Product API request was not intercepted"
    )




# ---------------------------------------------------------------- B2.10 (challenge)
def test_b2_10_home_renders_price_from_api_response(page):
    """Verify UI displays the modified price from API."""

    intercepted_requests = []

    def modify_product_price(route):
        # Fetch the real API response
        response = route.fetch()
        assert response.status == 200

        body = response.json()
        assert len(body["data"]) > 0

        # Change the first product price
        body["data"][0]["price"] = 999.99

        intercepted_requests.append(route.request.url)

        # Return the modified response
        route.fulfill(
            response=response,
            json=body,
        )

    # Register route before navigation
    page.route(PRODUCT_LIST, modify_product_price)

    # Open homepage
    page.goto("/")

    # Verify the first product price
    prices = page.locator("[data-test='product-price']")
    expect(prices.first).to_be_visible()
    expect(prices.first).to_have_text("$999.99")

    # Verify the API response was intercepted
    assert len(intercepted_requests) > 0, (
        "Product API request was not intercepted"
    )




# ---------------------------------------------------------------- B2.11 (challenge)
def test_b2_11_account_page_with_token_injected_skips_login_form(
    page, auth_token
):
    """Verify account page opens with token injected into localStorage."""

    # Inject authentication token before page navigation
    page.add_init_script(
        f"window.localStorage.setItem('auth-token', {json.dumps(auth_token)})"
    )

    # Open account page without using login form
    account = AccountPage(page).open()

    # Verify account page title
    expect(account.title).to_have_text("My account")

    # Verify logged-in user menu
    expect(account.nav_menu).to_be_visible()
    expect(account.nav_menu).to_contain_text("QA Bot")



# ---------------------------------------------------------------- B2.12 (given): storage state, login once per session
def test_b2_12_logged_in_page_shows_user_menu(logged_in_page):
    """Goal: reuse a saved login (fixture auth_state in conftest.py). Precondition: none.
    Expected: user menu shows the account name."""
    account = AccountPage(logged_in_page).open()
    expect(account.title).to_have_text("My account")
    expect(account.nav_menu).to_contain_text("QA Bot")
