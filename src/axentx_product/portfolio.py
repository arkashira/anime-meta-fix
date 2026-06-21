from .product import Product

class Portfolio:
    def __init__(self):
        self.products = []

    def add_product(self, product):
        self.products.append(product)

    def get_high_demand_products(self):
        return [product for product in self.products if product.is_high_demand()]
