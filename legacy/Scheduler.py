from Config import config


class Scheduler:
    def __init__(self, economy):
        self.economy = economy
        self.time = 0

    def step(self):
        self.time += 1
        
        if self.time == 1:
            self.initialize_firms()
        
        # 1. Innovation
        self.economy.innovate_firms()
        
        # 2. Capital firms receive Sell_orders
        self.economy.capital_goods_market()
        
        # 3. Labor market Matching
        self.economy.labor_market_matching()
        
        # 4. Production
        self.handle_production()
        
        # 5. Consumption Market Matching
        self.economy.consumption_market_matching()
        
        # 6. Consumption Sales Executed
        average_consumption = self.economy.execute_consumption_sales()
        
        # 7. Capital Sales Executed
        self.economy.goods_market_clearing()
        
        # 8. Statistics computed
        self.economy.update_global_state()
        self.economy.data_collector.collect_data(self.economy)
        
        # 9. Firms update state (includes demand expectations, production, and hiring objectives)
        self.economy.update_firms()
        
        # 10. End of step
        self.print_statistics()

    def initialize_firms(self):
        for firm in self.economy.firm1s + self.economy.firm2s:
            firm.demand = config.INITIAL_DEMAND
            firm.production = config.INITIAL_CAPITAL
            firm.desired_workers = config.INITIAL_WORKERS // (len(self.economy.firm1s) + len(self.economy.firm2s))

    def update_firms(self):
        for firm in self.economy.firm1s:
            firm.innovate()  # Firm1 specific method
            firm.calculate_expected_demand( self.economy.calculate_average_investment())
            firm.update_state()
        for firm in self.economy.firm2s:
            firm.update_state()
            firm.calculate_expected_demand( self.economy.calculate_average_consumption())

    def handle_production(self):
        for firm in self.economy.firm1s + self.economy.firm2s:
            firm.produce()

    def handle_pricing(self):
        for firm in self.economy.firm1s + self.economy.firm2s:
            firm.adjust_price()

    def print_statistics(self):
        data = self.economy.data_collector.data[-1]  # Get the latest data point
        
        print(f"\nTimestep {self.time} Stats:")
        print(f"Total Firm1 production: {sum(firm['production'] for firm in data['firm1_data'])}")
        print(f"Total Firm2 production: {sum(firm['production'] for firm in data['firm2_data'])}")
        print(f"Total Firm2 consumption demand: {sum(firm['demand'] for firm in data['firm2_data'])}")
        print(f"Total Firm1 consumption demand: {sum(firm['demand'] for firm in data['firm1_data'])}")
        print(f"Total Firm2 inventory: {sum(firm['inventory'] for firm in data['firm2_data'])}")
        print(f"Total Firm1 inventory: {sum(firm['inventory'] for firm in data['firm1_data'])}")
        print(f"Total employed workers: {sum(1 for worker in data['worker_data'] if worker['employed'])}")
        print(f"Total Firm1 workers: {sum(firm['workers'] for firm in data['firm1_data'])}")
        print(f"Total Firm2 workers: {sum(firm['workers'] for firm in data['firm2_data'])}")
        print(f"Total firm2 sales: {sum(firm['sales'] for firm in data['firm2_data'])}")
        print(f"Total Firm2 Budget: {sum(firm['budget'] for firm in data['firm2_data'])}")
        print(f"Average wage: {sum(worker['wage'] for worker in data['worker_data']) / len(data['worker_data']):.2f}")
        print(f"Average consumption: {sum(worker['consumption'] for worker in data['worker_data']) / len(data['worker_data']):.2f}")
     
        print(f"Firm1 budget: {sum(firm['budget'] for firm in data['firm1_data'])}")

    def run_simulation(self, num_steps):
        for _ in range(num_steps):
            self.step()
        self.economy.write_data_to_csv()