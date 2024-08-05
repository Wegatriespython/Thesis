import numpy as np
import math
from abc import ABC, abstractmethod
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import multiprocessing as mp
import time
import os
import json
import random


device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class EnlargedNeuralNetwork(nn.Module):
    def __init__(self, input_size, hidden_size=256, output_size=1):
        super(EnlargedNeuralNetwork, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.fc2 = nn.Linear(hidden_size, hidden_size)
        self.fc3 = nn.Linear(hidden_size, hidden_size // 2)
        self.fc4 = nn.Linear(hidden_size // 2, output_size)
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = self.dropout(x)
        x = torch.relu(self.fc2(x))
        x = self.dropout(x)
        x = torch.relu(self.fc3(x))
        return self.fc4(x)
class Node:
    def __init__(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0
        self.path_value = 0

class UpdatedNeuralMCTSSolver:
    def __init__(self, model, input_size, hidden_size=256, learning_rate=0.001):
        self.model = model
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.nn = EnlargedNeuralNetwork(input_size, hidden_size).to(device)
        self.optimizer = optim.Adam(self.nn.parameters(), lr=learning_rate)
        self.memory = deque(maxlen=10000)
        self.best_path = None
        self.best_path_value = float('-inf')
        self.last_save_time = time.time()
        # Load the neural network if a saved state exists
        self.load_nn_state()

    def solve(self, num_iterations, num_seeds):
        pool = mp.Pool(processes=mp.cpu_count())
        
        for seed in range(num_seeds):
            if seed == 0:
                initial_state = self.model.initial_state()
            else:
                initial_state = self.model.random_state()
            
            path = self.run_mcts(initial_state, num_iterations, pool)
            path_value = self.evaluate_path(path)
            
            if path_value > self.best_path_value:
                self.best_path = path
                self.best_path_value = path_value
            
            # Train neural network
            self.train_nn()
            
            # Save neural network state every 200 seconds
            current_time = time.time()
            if current_time - self.last_save_time > 200:
                self.save_nn_state()
                self.last_save_time = current_time
        
        pool.close()
        pool.join()
        
        # Save the final state of the neural network
        self.save_nn_state()
        
        return self.best_path
    
    def run_mcts(self, initial_state, num_iterations, pool):
        self.root = Node(initial_state)
        for _ in range(num_iterations):
            node = self.select(self.root)
            if node.state['t'] < self.model.T:
                leaf = self.expand(node)
                
                # Parallelize simulation
                states = [leaf.state for _ in range(10)]  # Simulate 10 times
                args = [(state, self.model) for state in states]  # Create args tuples
                values = pool.map(self.parallel_simulate, args)  # Pass args to parallel_simulate
                value = np.mean(values)
                
                self.backpropagate(leaf, value)
                
                # Store experience in memory
                self.memory.append((leaf.state, value))
        
        return self.get_best_path(self.root)

    def select(self, node):
        while node.children and node.state['t'] < self.model.T:
            if not all(child.visits > 0 for child in node.children):
                return node
            node = max(node.children, key=lambda n: self.uct_value(n))
        return node

    def expand(self, node):
        if node.state['t'] >= self.model.T:
            return node
        possible_states = self.model.get_possible_states(node.state)
        for state in possible_states:
            if self.model.is_valid_state(state):
                child = Node(state, parent=node)
                node.children.append(child)
        return np.random.choice(node.children) if node.children else node

    def backpropagate(self, node, value):
        while node:
            node.visits += 1
            node.value += value
            node.path_value = max(node.path_value, value)  # Update path value
            node = node.parent

    def get_best_path(self, node):
        path = []
        current_node = node
        while current_node:
            path.append(current_node.state)
            if not current_node.children or current_node.state['t'] >= self.model.T:
                break
            current_node = max(current_node.children, key=lambda n: n.path_value)
        return list(reversed(path))
    def evaluate_path(self, path):
        return sum(self.model.evaluate_state(state) for state in path)
    def uct_value(self, node):
        if node.visits == 0:
            return float('inf')
        
        nn_value = self.nn(self.state_to_input(node.state)).item()
        
        exploitation = node.path_value / node.visits
        exploration = math.sqrt(2 * math.log(node.parent.visits) / node.visits)
        
        return exploitation + exploration + 0.1 * nn_value

    def state_to_input(self, state):
        flattened_state = []
        t = state['t']
        
        # Include K_Raw_Init and K_Intermediate_Init
        flattened_state.extend(state['K_Raw_Init'].values())
        flattened_state.extend(state['K_Intermediate_Init'].values())
        
        # Include the current time step
        flattened_state.append(t)
        
        # Include the current price
        flattened_state.append(state['p'][t])

       
        return torch.tensor(flattened_state, dtype=torch.float32).unsqueeze(0)

    def train_nn(self):
        if len(self.memory) < 64:  # Wait until we have enough samples
            return
        
        # Sample a batch from memory
        batch = np.random.choice(len(self.memory), 64, replace=False)
        states, values = zip(*[self.memory[i] for i in batch])
        
        states = torch.cat([self.state_to_input(s) for s in states]).to(device)
        values = torch.tensor(values, dtype=torch.float32).unsqueeze(1).to(device)
        
        # Train the neural network
        self.optimizer.zero_grad()
        predictions = self.nn(states)
        loss = nn.MSELoss()(predictions, values)
        loss.backward()
        self.optimizer.step()
    
    @staticmethod
    def parallel_simulate(args):
        state, model = args
        node = Node(state)
        t = state['t']
        cumulative_value = 0
        while t <= model.T:
            cumulative_value += model.evaluate_state(state)
            if t == model.T:
                break
            possible_states = model.get_possible_states(state)
            valid_states = [s for s in possible_states if model.is_valid_state(s)]
            if not valid_states:
                break
            state = np.random.choice(valid_states)
            t = state['t']
        return cumulative_value

    def simulate(self, node):
        state = node.state
        cumulative_value = 0
        t = state['t']
        while t <= self.model.T:
            cumulative_value += self.model.evaluate_state(state)
            if t == self.model.T:
                break
            possible_states = self.model.get_possible_states(state)
            valid_states = [s for s in possible_states if self.model.is_valid_state(s)]
            if not valid_states:
                break
            state = np.random.choice(valid_states)
            t = state['t']
        return cumulative_value
    
    def save_nn_state(self):
        state = {
            'model_state_dict': self.nn.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'best_path': self.best_path,
            'best_path_value': self.best_path_value,
            'memory': list(self.memory)
        }
        torch.save(state, 'mcts_nn_state.pth')
        print(f"Neural network state saved at {time.time()}")

    def load_nn_state(self):
        if os.path.exists('mcts_nn_state.pth'):
            state = torch.load('mcts_nn_state.pth')
            self.nn.load_state_dict(state['model_state_dict'])
            self.optimizer.load_state_dict(state['optimizer_state_dict'])
            self.best_path = state['best_path']
            self.best_path_value = state['best_path_value']
            self.memory = deque(state['memory'], maxlen=10000)
            print("Loaded previous neural network state")
        else:
            print("No previous neural network state found. Starting from scratch.")

class UpdatedTwoSectorEconomyModel:
    def __init__(self, params):
        self.params = params
        self.F1 = params['F1']
        self.F2 = params['F2']
        self.T = params['T']
        self.N = params['N']
        self.delta = params['delta']
        self.alpha = params['alpha']
        self.A = params['A']
        self.w_min = params['w_min']
        self.K_total = params['K_total']

    def __getstate__(self):
        # Copy the object's state
        state = self.__dict__.copy()
        # Remove any non-picklable entries
        # state.pop('non_picklable_attribute', None)
        return state

    def __setstate__(self, state):
        # Restore instance attributes
        self.__dict__.update(state)
        # Reconstruct any non-picklable attributes if necessary
        # self.non_picklable_attribute = reconstruct_non_picklable_attribute()


    def initial_state(self):
        # Initialize with non-zero capital allocations
        k1_total = self.K_total * 0.4  # 40% to capital goods firms
        k2_total = self.K_total * 0.6  # 60% to consumption goods firms
        
        k1_alloc = np.random.dirichlet(np.ones(len(self.F1))) * k1_total
        k2_alloc = np.random.dirichlet(np.ones(len(self.F2))) * k2_total

        # Generate random labor allocations
        l_alloc = np.random.dirichlet(np.ones(len(self.F1) + len(self.F2))) * self.N

        # Generate random initial wages (at least minimum wage)
        w_alloc = np.random.uniform(self.w_min, self.w_min * 2, len(self.F1) + len(self.F2))

        # Generate random initial price
        p_init = np.random.uniform(0.5, 2.0)

        return {
            'K_Raw_Init': {f: k for f, k in zip(self.F1, k1_alloc)},
            'K_Intermediate_Init': {f: k for f, k in zip(self.F2, k2_alloc)},
            'L': {(1, f): l for f, l in zip(self.F1 + self.F2, l_alloc)},
            'K': {(1, f): (k1_alloc[i] if f in self.F1 else k2_alloc[i-len(self.F1)]) 
                for i, f in enumerate(self.F1 + self.F2)},
            'w': {(1, f): w for f, w in zip(self.F1 + self.F2, w_alloc)},
            'p': {1: p_init},
            't': 1
        }
    def evaluate_state(self, state):
        t = state['t']
        consumption = sum(
            self.A[i] * state['L'][(t, i)] ** (1 - self.alpha) * state['K'][(t, i)] ** self.alpha
            for i in self.F2
        )
        return math.log(max(consumption, 1e-6)) / (1 + self.delta) ** (t - 1)


    def random_state(self):
        # Generate random initial capital allocations
        k1_total = np.random.uniform(0.2, 0.4) * self.K_total
        k2_total = self.K_total - k1_total
        
        k1_alloc = np.random.dirichlet(np.ones(len(self.F1))) * k1_total
        k2_alloc = np.random.dirichlet(np.ones(len(self.F2))) * k2_total

        # Generate random labor allocations
        l_alloc = np.random.dirichlet(np.ones(len(self.F1) + len(self.F2))) * self.N

        # Generate random initial wages (at least minimum wage)
        w_alloc = np.random.uniform(self.w_min, self.w_min * 2, len(self.F1) + len(self.F2))

        # Generate random initial price
        p_init = np.random.uniform(0.5, 2.0)

        return {
            'K_Raw_Init': {f: k for f, k in zip(self.F1, k1_alloc)},
            'K_Intermediate_Init': {f: k for f, k in zip(self.F2, k2_alloc)},
            'L': {(1, f): l for f, l in zip(self.F1 + self.F2, l_alloc)},
            'K': {(1, f): 0 for f in self.F1 + self.F2},  # Will be updated in get_possible_states
            'w': {(1, f): w for f, w in zip(self.F1 + self.F2, w_alloc)},
            'p': {1: p_init},
            't': 1
        }
        
    def get_possible_states(self, state):
        new_states = []
        t = state['t']
        if t >= self.T:
            return new_states

        # Create a new state based on the current one
        new_state = {k: v.copy() if isinstance(v, dict) else v for k, v in state.items()}
        new_state['t'] = t + 1

        # Update capital allocations
        for i in self.F1:
            new_state['K'][(t+1, i)] = new_state['K_Raw_Init'][i]
        for i in self.F2:
            new_state['K'][(t+1, i)] = new_state['K_Intermediate_Init'][i] + sum(
                self.A[i] * new_state['L'][(t, i)] ** (1 - self.alpha) * new_state['K'][(t, i)] ** self.alpha
                for i in self.F1
            )

        # Generate variations
        for _ in range(10):  # Increase the number of variations
            variation = new_state.copy()
            
            # Adjust labor allocations
            total_labor = sum(variation['L'][(t, i)] for i in self.F1 + self.F2)
            labor_shares = np.random.dirichlet(np.ones(len(self.F1) + len(self.F2)))
            for i, share in zip(self.F1 + self.F2, labor_shares):
                variation['L'][(t+1, i)] = share * self.N

            # Adjust wages (ensure they're above minimum wage)
            for i in self.F1 + self.F2:
                variation['w'][(t+1, i)] = max(np.random.uniform(self.w_min, self.w_min * 2), self.w_min)

            # Adjust prices (within bounds)
            variation['p'][t+1] = np.random.uniform(0.1, 10)

            # Only add the variation if it's valid
            if self.is_valid_state(variation):
                new_states.append(variation)

        return new_states

    def is_valid_state(self, state):
        t = state['t']
        
        # 1. Labor market clearing/Conservation of Labor
        if sum(state['L'][(t, i)] for i in self.F1 + self.F2) > self.N:
            return False

        # 2. Capital market clearing
        capital_supply = sum(
            self.A[i] * state['L'][(t, i)] ** (1 - self.alpha) * state['K'][(t, i)] ** self.alpha
            for i in self.F1
        )
        capital_demand = sum(state['K'][(t, i)] for i in self.F2)
        if capital_supply < capital_demand:
            return False

        # 3. Consumption market clearing
        consumption_supply = sum(
            self.A[i] * state['L'][(t, i)] ** (1 - self.alpha) * state['K'][(t, i)] ** self.alpha
            for i in self.F2
        )
        wage_bill = sum(state['w'][(t, i)] * state['L'][(t, i)] for i in self.F1 + self.F2)
        if consumption_supply < wage_bill:
            return False

        # 4. Firm1 (capital goods) budget constraint
        for i in self.F1:
            if state['p'][t] * self.A[i] * state['L'][(t, i)] ** (1 - self.alpha) * state['K'][(t, i)] ** self.alpha < state['w'][(t, i)] * state['L'][(t, i)]:
                return False

        # 5. Firm2 (consumption goods) budget constraint
        for i in self.F2:
            if self.A[i] * state['L'][(t, i)] ** (1 - self.alpha) * state['K'][(t, i)] ** self.alpha < state['w'][(t, i)] * state['L'][(t, i)] + state['p'][t] * state['K'][(t, i)]:
                return False

        # 6. Conservation of Firm1 Capital
        if sum(state['K'][(t, i)] for i in self.F1) != sum(state['K_Raw_Init'].values()):
            return False

        # 7. Conservation of Firm2 Capital
        total_intermediate_capital = sum(state['K_Intermediate_Init'].values())
        total_produced_capital = sum(
            self.A[i] * state['L'][(t, i)] ** (1 - self.alpha) * state['K'][(t, i)] ** self.alpha
            for i in self.F1
        )
        if sum(state['K'][(t, i)] for i in self.F2) != total_intermediate_capital + total_produced_capital:
            return False

        # 8. Non-negativity constraints
        if any(value < 0 for values in [state['L'], state['K'], state['w'], state['p'].values()] for value in values.values()):
            return False

        # 9. Minimum Consumption
        if consumption_supply <= self.N:
            return False

        # 10. Minimum wage constraint
        if any(state['w'][(t, i)] < self.w_min for i in self.F1 + self.F2):
            return False

        # 11. Relative price bounds
        if not 0.1 <= state['p'][t] <= 10:
            return False

        return True

    def simulate(self, state):
        t = state['t']
        consumption = sum(
            self.A[i] * state['L'][(t, i)] ** (1 - self.alpha) * state['K'][(t, i)] ** self.alpha
            for i in self.F2
        )
        return math.log(max(consumption, 1e-6)) / (1 + self.delta) ** (t - 1)

    def evaluate_solution(self, state):
        return sum(self.simulate(state) for t in range(1, self.T + 1))

def print_state_summary(state, model):
    t = state['t']
    production_capital = sum(
        model.A[i] * state['L'][(t, i)] ** (1 - model.alpha) * state['K'][(t, i)] ** model.alpha
        for i in model.F1
    )
    production_consumption = sum(
        model.A[i] * state['L'][(t, i)] ** (1 - model.alpha) * state['K'][(t, i)] ** model.alpha
        for i in model.F2
    )

    print(f"Capital Sector Production: {production_capital:.2f}")
    print(f"Consumption Sector Production: {production_consumption:.2f}")
    print(f"Total Production: {production_capital + production_consumption:.2f}")

    total_consumption = production_consumption
    print(f"Total Consumption: {total_consumption:.2f}")

    print("Labor allocation:")
    for i in model.F1 + model.F2:
        print(f"  Firm {i}: {state['L'][(t, i)]:.2f}")
    print("Capital allocation:")
    for i in model.F1 + model.F2:
        print(f"  Firm {i}: {state['K'][(t, i)]:.2f}")
    print("Wages:")
    for i in model.F1 + model.F2:
        print(f"  Firm {i}: {state['w'][(t, i)]:.2f}")
    print(f"Price of capital goods: {state['p'][t]:.2f}")


def main():
    # Set random seed for reproducibility
    np.random.seed(42)

    # Define input parameters
    params = {
        'F1': ['firm1_1', 'firm1_2'],  # Set of capital goods firms
        'F2': ['firm2_1', 'firm2_2', 'firm2_3'],  # Set of consumption goods firms
        'T': 10,  # Number of time periods
        'N': 1000,  # Total number of workers
        'K_total': 10000,  # Total initial capital
        'delta': 0.05,  # Discount rate
        'alpha': 0.3,  # Capital elasticity
        'A': {  # Productivity of firms
            'firm1_1': 1.2, 'firm1_2': 1.3,
            'firm2_1': 1.0, 'firm2_2': 1.1, 'firm2_3': 1.2
        },
        'w_min': 5  # Minimum wage
    }

    # Initialize the model
    model = UpdatedTwoSectorEconomyModel(params)

    # Calculate input_size based on the actual structure of the flattened state
    input_size = (
        len(model.F1) +  # K_Raw_Init
        len(model.F2) +  # K_Intermediate_Init
        1 +  # Current time step
        1    # Current price
    )

    print(f"Calculated input_size: {input_size}")

    # Initialize the solver
    solver = UpdatedNeuralMCTSSolver(model, input_size=input_size, hidden_size=64)

    # Run the solver
    num_iterations = 5000
    num_seeds = 10
    solution_path = solver.solve(num_iterations=num_iterations, num_seeds=num_seeds)

    print("Final optimal path:")
    for t, state in enumerate(solution_path):
        print(f"\nTime period {t}:")
        print_state_summary(state, model)

    # Calculate and print overall economic metrics
    total_utility = solver.evaluate_path(solution_path)
    print(f"\nTotal Utility over all periods: {total_utility:.2f}")

    # Print additional metrics
    print("\nAdditional Metrics:")
    print(f"Average Capital Sector Production: {np.mean([sum(model.A[i] * state['L'][(state['t'], i)] ** (1 - model.alpha) * state['K'][(state['t'], i)] ** model.alpha for i in model.F1) for state in solution_path]):.2f}")
    print(f"Average Consumption Sector Production: {np.mean([sum(model.A[i] * state['L'][(state['t'], i)] ** (1 - model.alpha) * state['K'][(state['t'], i)] ** model.alpha for i in model.F2) for state in solution_path]):.2f}")
    print(f"Average Total Labor: {np.mean([sum(state['L'][(state['t'], i)] for i in model.F1 + model.F2) for state in solution_path]):.2f}")
    print(f"Average Total Capital: {np.mean([sum(state['K'][(state['t'], i)] for i in model.F1 + model.F2) for state in solution_path]):.2f}")

if __name__ == '__main__':
    mp.freeze_support()
    main()