from src.axentx_product.portfolio import Portfolio
from src.axentx_product.product import Product

def test_portfolio_add_product():
    portfolio = Portfolio()
    product = Product("Test Product", 100.0)
    portfolio.add_product(product)
    assert len(portfolio.products) == 1

def test_portfolio_get_high_demand_products():
    portfolio = Portfolio()
    product1 = Product("Test Product 1", 100.0)
    product2 = Product("Test Product 2", 99.0)
    portfolio.add_product(product1)
    portfolio.add_product(product2)
    high_demand_products = portfolio.get_high_demand_products()
    assert len(high_demand_products) == 1
    assert high_demand_products[0].name == "Test Product 1"
