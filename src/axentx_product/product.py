class Product:
    def __init__(self, name, demand_score):
        self.name = name
        self.demand_score = demand_score

    def __repr__(self):
        return f"Product('{self.name}', {self.demand_score})"

    def is_high_demand(self):
        return self.demand_score >= 100.0
