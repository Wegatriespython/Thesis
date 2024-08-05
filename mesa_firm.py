from mesa import Agent
import numpy as np
from Simple_profit_maxxing import profit_maximization
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler
import logging

logging.basicConfig(level=logging.INFO)
class Firm(Agent):
    def __init__(self, unique_id, model, initial_capital, initial_productivity):
        super().__init__(unique_id, model)
        self.capital = initial_capital
        self.productivity = initial_productivity
        self.price = model.config.INITIAL_PRICE
        self.inventory = model.config.INITIAL_INVENTORY
        self.workers = []
        self.production = 0
        self.sales = 0
        self.budget = initial_capital
        self.historic_sales = [model.config.INITIAL_DEMAND] * 5
        self.expected_demand = model.config.INITIAL_DEMAND
        self.expected_price = model.config.INITIAL_PRICE
        self.labor_demand = 0
        self.investment_demand = 0
        self.mode = 'decentralized'
        self.demand_predictor = LinearRegression()
        self.scaler = StandardScaler()
        self.is_trained = False
        self.prediction_history = []
        self.wage = model.config.INITIAL_WAGE

    def step(self):
        print("Budget", self.budget)
        if self.mode == 'decentralized':
            self.decentralized_step()
        elif self.mode == 'centralized':
            self.centralized_step()

    def decentralized_step(self):
        self.update_firm_state()
        self.make_production_decision()
        self.update_historic_sales()
    def centralized_step(self):
        pass
    def update_firm_state(self):
        if isinstance(self, Firm1):
            self.expected_demand = self.get_market_demand('capital')
        elif isinstance(self, Firm2):
            self.expected_demand = self.get_market_demand('consumption')
        self.expected_price = self.calculate_expected_price()
        #self.train_demand_predictor()
        depreciation_amount = self.inventory * self.model.config.DEPRECIATION_RATE
        self.inventory = max(0, self.inventory - depreciation_amount)
        self.budget -= depreciation_amount * self.price

    def get_market_demand(self, market_type):
        if market_type == 'labor':
            potential_buyers = [agent for agent in self.model.schedule.agents if isinstance(agent, Firm)]
            buyer_demand = [firm.labor_demand for firm in potential_buyers]
        elif market_type == 'capital':
            potential_buyers = [agent for agent in self.model.schedule.agents if isinstance(agent, Firm)]
            buyer_demand = [firm.investment_demand for firm in potential_buyers]
        elif market_type == 'consumption':
            potential_buyers = [agent for agent in self.model.schedule.agents if hasattr(agent, 'consumption')]
            buyer_demand = [agent.consumption for agent in potential_buyers]
        else:
            raise ValueError(f"Invalid market type: {market_type}")

        return sum(buyer_demand)

    def predict_demand(self):
        if not self.is_trained:
            return np.mean(self.historic_sales)  # Fallback to historical average if not trained

        features = self.prepare_features()
        features_scaled = self.scaler.transform(features.reshape(1, -1))
        prediction = self.demand_predictor.predict(features_scaled)[0]

        return max(prediction, 0)  # Ensure non-negative demand

    def prepare_features(self):
        return np.array([
            self.capital,
            len(self.workers),
            self.productivity,
            self.price,
            self.inventory,
            self.budget,
            np.mean(self.historic_sales),
            np.std(self.historic_sales),
            self.model.get_average_wage(),  # Updated
            self.model.get_average_capital_price(),  # Updated
            self.model.get_average_consumption_good_price(),  # Updated
            self.get_market_demand(self.get_market_type())
        ])

    def train_demand_predictor(self):
        if len(self.historic_sales) < 10:  # Need some history to train
            return

        X = np.array([self.prepare_features() for _ in range(len(self.historic_sales) - 5)])
        y = np.array(self.historic_sales[5:])  # Predict next period's sales

        X_scaled = self.scaler.fit_transform(X)
        self.demand_predictor.fit(X_scaled, y)
        self.is_trained = True

        logging.info(f"Firm {self.unique_id} - Demand predictor trained. Coefficients: {self.demand_predictor.coef_}")

    def make_production_decision(self):
        # Update expected demand first
        if isinstance(self, Firm1):
            self.expected_demand = self.get_market_demand('capital')
        elif isinstance(self, Firm2):
            self.expected_demand = self.get_market_demand('consumption')

        #print("Calling profit_maximization with parameters:", {
            #'current_capital': self.capital,
            #'current_labor': len(self.workers),
            #'current_price': self.price,
            #'current_productivity': self.productivity,
            #'expected_demand': [self.expected_demand] * self.model.config.TIME_HORIZON,
            #'expected_price': [self.expected_price] * self.model.config.TIME_HORIZON,
            #'capital_price': self.model.get_average_capital_price(),  # Updated
            #'capital_elasticity': self.model.config.CAPITAL_ELASTICITY,
            #'current_inventory': self.inventory,
            #'depreciation_rate': self.model.config.DEPRECIATION_RATE,
            #'expected_periods': self.model.config.TIME_HORIZON,
            #'discount_rate': self.model.config.DISCOUNT_RATE,
            #'budget': self.budget,
            #'wage': self.wage
        #})

        result = profit_maximization(
            self.capital,
            len(self.workers),
            self.price,
            self.productivity,
            [self.expected_demand] * self.model.config.TIME_HORIZON,
            [self.expected_price] * self.model.config.TIME_HORIZON,
            self.model.get_average_capital_price(),  # Updated
            self.model.config.CAPITAL_ELASTICITY,
            self.inventory,
            self.model.config.DEPRECIATION_RATE,
            self.model.config.TIME_HORIZON,
            self.model.config.DISCOUNT_RATE,
            self.budget,
            self.wage
        )

        if result is None:
            print("Optimization failed")
            return


        optimal_labor = result['optimal_labor']
        optimal_capital = result['optimal_capital']
        optimal_price = result['optimal_price']
        optimal_production = result['optimal_production']

        print(f"Optimal labor From the Optimisation: {optimal_labor}, optimal capital: {optimal_capital}, optimal price: {optimal_price}, optimal production: {optimal_production}")

        self.labor_demand = max(0, optimal_labor - len(self.workers))
        self.price = self.adjust_price(self.price, self.sales, self.expected_demand)
        self.investment_demand = self.adjust_capital(self.capital, optimal_capital, self.budget, self.model.get_average_capital_price())  # Updated
        print(f"Production pre-optimisation: {self.production}")
        self.production = self.adjust_production(self.production, optimal_production)
        print(f"Production post-optimisation: {self.production}")
        #self.inventory += self.production


    def adjust_production(self, current_production: float, optimal_production: float, max_adjustment_rate: float = 0.1) -> float:
        """
        Adjust production gradually towards the optimal level.

        :param current_production: Current production level
        :param optimal_production: Optimal production level from profit maximization
        :param max_adjustment_rate: Maximum rate of change in production (default 10%)
        :return: New production level
        """
        if self.inventory - optimal_production >= 0:
            return 0

        production_difference = optimal_production - current_production
        max_change = 5

        if abs(production_difference) <= max_change:
            # If the difference is small, move directly to optimal

            return optimal_production
        elif production_difference > 0:
            # If we need to increase production
            #print("Current production", current_production + max_change)
            return current_production + max_change
        else:
            # If we need to decrease production
            return current_production - max_change

    def adjust_price(self, current_price: float, sales: float, expected_demand: float) -> float:
        """
        Adjust price based on sales vs expected demand.

        :param current_price: The current price of the good
        :param sales: Actual sales in the last period
        :param expected_demand: Expected demand for the last period
        :return: Adjusted price
        """
        if sales >= expected_demand:
            proposed_price = current_price * 1.05
            return proposed_price # Increase price by 5%
        else:
            print("Sales Shortfall", sales - expected_demand)
            proposed_price = current_price * 0.95
            return proposed_price  # Decrease price by 5%

    def adjust_capital(self, current_capital: float,
                    optimal_capital: float,
                    budget: float,
                    capital_price: float) -> float:
        """
        Adjust capital based on optimal capital and budget constraints.

        :param current_capital: Current capital stock
        :param optimal_capital: Optimal capital stock from profit maximization
        :param budget: Available budget for capital adjustment
        :param capital_price: Price of capital (in labor units)
        :return: New capital stock
        """
        desired_change = optimal_capital - current_capital
        max_affordable_change = budget / max(capital_price,1)

        if desired_change > 0:
            # Buying capital
            actual_change = min(desired_change, max_affordable_change)
        else:
            # Selling capital (assume we can sell any amount)
            return 0

        return actual_change



    def update_historic_sales(self):
        self.historic_sales.append(self.sales)
        if len(self.historic_sales) > 10:
            self.historic_sales.pop(0)
        self.sales = 0

    def calculate_expected_price(self):
        if len(self.historic_sales) < 10:
            return self.price
        return np.mean([self.price] + [self.model.get_average_consumption_good_price() for _ in range(4)])

    def calculate_production_capacity(self):
        return self.productivity * (self.capital ** self.model.config.CAPITAL_ELASTICITY) * (len(self.workers) ** (1 - self.model.config.CAPITAL_ELASTICITY))

    def hire_worker(self, worker, wage):
        self.workers.append(worker)
        self.budget -= wage
        self.labor_demand -= 1
        self.wage = wage  # Update the firm's wage

    def fire_workers(self, num_workers):
        for _ in range(min(num_workers, len(self.workers))):
            worker = self.workers.pop()
            worker.get_fired()

    def buy_capital(self, quantity, price):
        if isinstance(self, Firm2):
            self.capital += quantity
            self.investment_demand -= quantity
            self.budget -= quantity * price
    def sell_goods(self, quantity, price):
        self.inventory -= quantity
        self.sales += quantity
        self.budget += quantity * price  # Price already adjusted in execute_capital_market
        print("Sales Made", quantity)
        print("Budget added", quantity * price)


    def get_max_wage(self):
        return (self.budget / max(1, self.labor_demand)) if self.labor_demand >= 0.8 else 0

    def get_max_capital_price(self):
        return (self.budget / max(1, self.investment_demand)) if self.investment_demand >= 0.8 else 0

    def apply_central_decision(self, labor, capital, price):
        self.labor_demand = labor
        self.capital = capital
        if isinstance(self, Firm1):
            self.price = price * self.model.relative_price  # Adjust for relative price
        else:
            self.price = price  # Consumption goods are the numeraire
        self.produce()
    def update_after_markets(self):
        pass
    def get_market_type(self):
        if isinstance(self, Firm1):
            return 'capital'
        elif isinstance(self, Firm2):
            return 'consumption'
        else:
            return 'labor'
    def analyze_prediction_accuracy(self):
        if len(self.prediction_history) < 2:
            return

        actual_sales = self.historic_sales[-len(self.prediction_history)+1:]
        predictions = [p['predicted_demand'] for p in self.prediction_history[:-1]]  # Exclude the most recent prediction

        mse = np.mean((np.array(actual_sales) - np.array(predictions))**2)
        mae = np.mean(np.abs(np.array(actual_sales) - np.array(predictions)))

        logging.info(f"Firm {self.unique_id} - Prediction Accuracy: MSE: {mse:.2f}, MAE: {mae:.2f}")
class Firm1(Firm):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, model.config.FIRM1_INITIAL_CAPITAL, model.config.INITIAL_PRODUCTIVITY)

    def step(self):
        super().step()
        self.price = self.model.config.INITIAL_PRICE * self.model.config.INITIAL_RELATIVE_PRICE_CAPITAL   # Reset price to initial value
        if self.mode == 'decentralized':
            self.innovate()

    def innovate(self):
        if self.model.random.random() < self.model.config.INNOVATION_ATTEMPT_PROBABILITY:
            rd_investment = self.capital * self.model.config.FIRM1_RD_INVESTMENT_RATE
            self.budget -= rd_investment
            if self.model.random.random() < self.model.config.PRODUCTIVITY_INCREASE_PROBABILITY:
                self.productivity *= (1 + self.model.config.PRODUCTIVITY_INCREASE)

class Firm2(Firm):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model, model.config.FIRM2_INITIAL_CAPITAL, model.config.INITIAL_PRODUCTIVITY)
        self.capital_inventory = 0  # Separate inventory for capital goods
    def buy_capital(self, quantity, price): # SUS
        self.capital_inventory += quantity
        self.investment_demand -= quantity
        self.budget -= quantity * price
    def produce_consumption_goods(self):
        capital_input = min(self.capital_inventory, self.model.config.MAX_CAPITAL_USAGE)
        self.production = self.productivity * (capital_input ** self.model.config.CAPITAL_ELASTICITY) * (len(self.workers) ** (1 - self.model.config.CAPITAL_ELASTICITY))
        self.inventory += self.production
        self.capital_inventory -= capital_input  # Consume the capital goods used in production
