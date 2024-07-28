from legacy.economy import Economy
from legacy.Scheduler import Scheduler
from Config import config

def run_simulation():
    economy = Economy(config.INITIAL_WORKERS, config.INITIAL_CAPITAL_FIRMS, config.INITIAL_CONSUMPTION_FIRMS)
    scheduler = Scheduler(economy)
    scheduler.run_simulation(config.SIMULATION_STEPS)

if __name__ == "__main__":
    run_simulation()