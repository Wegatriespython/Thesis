from legacy.firm1 import Firm1
from legacy.firm2 import Firm2
from legacy.Worker import Worker
import csv

class DataCollector:
    def __init__(self):
        self.data = []

    def collect_data(self, economy):
        """
        Collects data from all agents in the economy.
        """
        timestep_data = {
            "time": economy.time,
            "firm1_data": [self.collect_firm1_data(firm) for firm in economy.firm1s],
            "firm2_data": [self.collect_firm2_data(firm) for firm in economy.firm2s],
            "worker_data": [self.collect_worker_data(worker) for worker in economy.workers],
            "economy_data": self.collect_economy_data(economy)
        }
        self.data.append(timestep_data)

    def collect_firm1_data(self, firm: Firm1):
        """
        Collects data from a Firm1 object.
        """
        return {
            "capital": firm.capital,
            "productivity": firm.productivity,
            "price": firm.price,
            "inventory": firm.inventory,
            "sales": firm.sales,
            "workers": len(firm.workers),
            "RD_investment": firm.RD_investment,
            "demand": firm.demand,
            "budget": firm.budget,
            "production": firm.production,
            "wage_offers": len(firm.wage_offers)
        }

    def collect_firm2_data(self, firm: Firm2):
        """
        Collects data from a Firm2 object.
        """
        return {
            "capital": firm.capital,
            "productivity": firm.productivity,
            "price": firm.price,
            "sales": firm.sales,
            "inventory": firm.inventory,
            "workers": len(firm.workers),
            "demand": firm.demand,
            "budget": firm.budget,
            "sales": firm.sales,
            "investment": firm.investment,
            "investment_demand": firm.investment_demand,
            "desired_capital": firm.desired_capital,
            "production": firm.production,
            "wage_offers": len(firm.wage_offers)
        }
    def collect_worker_data(self, worker: Worker):
        return {
            "employed": worker.employed,
            "wage": worker.wage,
            "skills": worker.skills,
            "offers": len(worker.offers),
            "savings": worker.savings,
            "consumption": worker.consumption
              # Add this line
        }
    def get_data(self):
        """
        Returns the collected data.
        """
        return self.data
    
    
    def collect_economy_data(self, economy):
        return {
            "total_demand": economy.total_demand,
            "total_supply": economy.total_supply,
            "global_productivity": economy.global_productivity
        }

    def write_to_csv(self, filename="simulation_results.csv"):
        if not self.data:  # Check if there's any data to write
            print("No data to write to CSV.")
            return

        with open(filename, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            header = ["Time", "Total Demand", "Total Supply", "Global Productivity"]
            if self.data[0]["firm1_data"]:  # Check if there's any firm1 data
                for key in self.data[0]["firm1_data"][0].keys():
                    for i in range(len(self.data[0]["firm1_data"])):
                        header.append(f"Firm1_{i+1}_{key}")
            if self.data[0]["firm2_data"]:  # Check if there's any firm2 data
                for key in self.data[0]["firm2_data"][0].keys():
                    for i in range(len(self.data[0]["firm2_data"])):
                        header.append(f"Firm2_{i+1}_{key}")
            if self.data[0]["worker_data"]:  # Check if there's any worker data
                for key in self.data[0]["worker_data"][0].keys():
                    for i in range(len(self.data[0]["worker_data"])):
                        header.append(f"Worker_{i+1}_{key}")
            writer.writerow(header)
            
            # Write data
            for timestep in self.data:
                row = [
                    timestep["time"],
                    timestep["economy_data"]["total_demand"],
                    timestep["economy_data"]["total_supply"],
                    timestep["economy_data"]["global_productivity"]
                ]
                for firm1 in timestep["firm1_data"]:
                    row.extend(firm1.values())
                for firm2 in timestep["firm2_data"]:
                    row.extend(firm2.values())
                for worker in timestep["worker_data"]:
                    row.extend(worker.values())
                writer.writerow(row)

        print(f"Data has been written to {filename}")