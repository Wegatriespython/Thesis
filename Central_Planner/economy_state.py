from dataclasses import dataclass

@dataclass
class EconomyState:
    labor_supply: float
    capital_supply: float
    price_firm1: float
    price_firm2: float
    wage: float
    labor_firm1: float
    labor_firm2: float
    capital_firm1: float
    capital_firm2: float
    assets_firm1: float
    assets_firm2: float
    worker_savings: float

class Config:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)