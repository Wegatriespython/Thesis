from Config import config
import random
from legacy.Worker import Worker
from legacy.firm1 import Firm1
from legacy.firm2 import Firm2
from legacy.Stats import DataCollector

class Economy:
    def __init__(self, num_workers, num_firm1, num_firm2):
        self.workers = [Worker() for _ in range(num_workers)]
        self.firm1s = [Firm1() for _ in range(num_firm1)]
        self.firm2s = [Firm2() for _ in range(num_firm2)]
        self.time = 0
        self.total_demand = 0 
        self.total_supply = 0
        self.global_productivity = 1
        self.average_consumption = 0
        self.average_investment = 0
        self.data_collector = DataCollector()

    def labor_market_matching(self):
        all_firms = self.firm1s + self.firm2s

        for firm in all_firms:
            firm.calculate_budget()
            workers_to_fire = []

            for worker in firm.workers:
                if firm.budget >= worker.wage:
                    firm.budget -= worker.wage
                    worker.savings += worker.wage
                else:
                    workers_to_fire.append(worker)
            
            for worker in workers_to_fire:
                firm.workers.remove(worker)
                worker.employed = False
                worker.employer = None
                worker.wage = 0

        available_workers = [w for w in self.workers if not w.employed]
        random.shuffle(available_workers)

        for worker in available_workers:
            hiring_firms = [f for f in all_firms if f.budget > config.MINIMUM_WAGE]
            if hiring_firms:
                hiring_firm = random.choice(hiring_firms)
                wage = min(hiring_firm.budget, config.INITIAL_WAGE)
                worker.employed = True
                worker.employer = hiring_firm
                worker.wage = wage
                hiring_firm.workers.append(worker)
                hiring_firm.budget -= wage
                hiring_firm.desired_workers -= 1

    def goods_market_clearing(self):
        all_firms = self.firm1s
        total_consumption = 0
        total_transactions = 0
        # Collect and sort all sell orders from largest to smallest
        all_sell_orders = []
        for seller in all_firms:
            all_sell_orders.extend([(seller, buyer, quantity, price) for buyer, quantity, price in seller.sell_orders])
        all_sell_orders.sort(key=lambda x: x[2], reverse=True)

        for seller, buyer, quantity, price in all_sell_orders:
            if seller.inventory >= quantity and buyer.budget >= quantity * price:
                # Execute the trade
                seller.inventory -= quantity
                seller.quantity_sold += quantity
                total_consumption += quantity
                total_transactions += 1
                seller.sales += quantity * price
                seller.budget += quantity * price

                buyer.capital += quantity  # Assuming the goods are capital
                buyer.budget -= quantity * price

           

        # Clear all orders after processing
        for firm in all_firms:
            firm.clear_orders()
        self.average_investment = total_consumption / total_transactions if total_transactions > 0 else 0
        print(f"Average investment raw: {self.average_investment}")

    def capital_goods_market(self):
        for firm1 in self.firm1s:
            firm1.demand = 0  # Reset demand for each Firm1

        for firm2 in self.firm2s:
            if firm2.investment_demand > 0:
                for firm1 in self.firm1s:
                    if firm1.inventory > 0:
                        quantity = min(firm2.investment_demand, firm1.inventory)
                        firm1.add_sell_order(firm2, quantity, firm1.price)
                        firm1.demand += quantity  # Directly update Firm1's demand
                        firm2.investment_demand -= quantity
                    elif firm2.investment_demand == 0:
                        break
                    else:
                        break

    def consumption_market_matching(self):
        for firm in self.firm2s:
            firm.demand = 0  # Reset demand for each Firm2
            if firm.inventory > 0:
                for worker in self.workers:
                    desired_consumption = worker.calculate_desired_consumption()
                    if desired_consumption > 0:
                        quantity = min(firm.inventory, desired_consumption / firm.price)
                        firm.add_sell_order(worker, quantity, firm.price)
                        firm.demand += quantity  # Directly update Firm2's demand   

    def execute_consumption_sales(self):
        total_consumption = 0
        total_transactions = 0

        for firm in self.firm2s:
            for buyer, quantity, price in firm.sell_orders:
                if firm.inventory >= quantity and buyer.savings >= quantity * price:
                    firm.inventory -= quantity
                    firm.quantity_sold += quantity
                    total_consumption += quantity
                    total_transactions += 1
                    firm.sales += quantity * price

                    buyer.savings -= quantity * price
                    buyer.consumption += quantity

        # Update worker satiation status
        for worker in self.workers:
            worker.satiated = (worker.consumption >= worker.calculate_desired_consumption())

        # Calculate average consumption for demand expectations
        average_consumption = total_consumption / total_transactions if total_transactions > 0 else 0
        self.average_consumption = average_consumption
        print(f"Average consumption raw: {average_consumption}")
        return average_consumption

    def update_firms(self):
        average_consumption = self.average_consumption
        average_investment = self.average_investment
        
        for firm in self.firm1s:
            firm.calculate_expected_demand(average_investment)
            firm.update_state()
        
        for firm in self.firm2s:
            firm.calculate_expected_demand(average_consumption)
            firm.update_state()

    def update_workers(self):
        for worker in self.workers:
            worker.update_state()

    def innovate_firms(self):
        for firm in self.firm1s:
            firm.innovate()
  


    def update_global_state(self):
        self.total_demand = sum(firm.demand for firm in self.firm1s + self.firm2s)
        self.total_supply = sum(firm.inventory for firm in self.firm1s + self.firm2s)
        self.global_productivity = self.calculate_global_productivity()

    def calculate_global_productivity(self):
        total_output = sum([firm.production for firm in self.firm1s + self.firm2s])
        total_labor = len([worker for worker in self.workers if worker.employed])
        return total_output / total_labor if total_labor > 0 else 1

    def get_data(self):
        return self.data_collector.get_data()

    def write_data_to_csv(self, filename="simulation_results.csv"):
        self.data_collector.write_to_csv(filename)


            
