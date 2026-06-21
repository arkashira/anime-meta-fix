from src.axentx_product.product import Product

def test_product_init():
    product = Product("Test Product", 100.0)
    assert product.name == "Test Product"
    assert product.demand_score == 100.0

def test_product_is_high_demand():
    product = Product("Test Product", 100.0)
    assert product.is_high_demand() is True

    product = Product("Test Product", 99.0)
    assert product.is_high_demand() is False
