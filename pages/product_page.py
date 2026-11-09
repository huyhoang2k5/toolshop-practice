
from pages.base_page import BasePage


class ProductPage(BasePage):
    def __init__(self, page):
        super().__init__(page)

        # TODO B1.3: name, unit_price, quantity, add_to_cart_button
        # Find the data-test values with DevTools (F12) or: playwright codegen https://practicesoftwaretesting.com
        self.name = page.get_by_test_id("product-name")
        self.unit_price = page.get_by_test_id("unit-price")
        self.quantity = page.get_by_test_id("quantity")
        self.add_to_cart_button = page.get_by_test_id("add-to-cart")

    def add_to_cart(self, quantity: int = 1):
        # TODO B1.3: set the quantity field if quantity != 1, click "Add to cart", return self
        if quantity != 1:
            self.quantity.fill(str(quantity))
        self.add_to_cart_button.click()
        return self

    def price(self) -> float:
        # TODO B1.4: unit price as a float
        return float(self.unit_price.inner_text())
