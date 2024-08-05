import numpy as np
from typing import Dict, List, Tuple
import random
from collections import deque
import multiprocessing
from functools import partial

class Node:
    def __init__(self, state: Dict, parent=None):
        self.state = state
        self.parent = parent
        self.children: List['Node'] = []
        self.visits = 0
        self.value = 0.0

class MCTSSolver:
    def __init__(self, model: Dict, config: Dict, nn_handler):
        self.model = model
        self.config = config
        self.nn_handler = nn_handler
        self.max_time_steps = len(model['sets']['T'])
        self.root = None
        self.num_processes = config.get('num_processes', multiprocessing.cpu_count())
        self.aggregate = config.get('aggregate', False)
        self.F1 = model['sets']['F1']
        self.F2 = model['sets']['F2']

    def solve(self) -> List[Dict]:
        self.root = Node(self.model['initial_state']())
        for _ in range(self.config['num_iterations']):
            node = self.select(self.root)
            if node.state['t'] < self.max_time_steps - 1:
                child = self.expand(node)
                value = self.simulate(child)
                self.backpropagate(child, value)

        best_path = []
        node = self.root
        while node.children and len(best_path) < self.max_time_steps:
            node = max(node.children, key=lambda c: c.value / c.visits)
            best_path.append(node.state)

        while len(best_path) < self.max_time_steps:
            last_state = best_path[-1]
            next_state = self.model['transition'](last_state)
            best_path.append(next_state)

        return best_path

    def select(self, node: Node) -> Node:
        while node.children and node.state['t'] < len(self.model['sets']['T']) - 1:
            if not all(child.visits > 0 for child in node.children):
                return self.select_unexplored(node)
            node = self.select_ucb(node)
        return node

    def select_unexplored(self, node: Node) -> Node:
        unexplored = [child for child in node.children if child.visits == 0]
        return random.choice(unexplored)

    def select_ucb(self, node: Node) -> Node:
        log_parent_visits = np.log(node.visits)
        ucb_values = [
            (child.value / child.visits) +
            self.config['exploration_weight'] * np.sqrt(log_parent_visits / child.visits) +
            self.nn_handler.predict_value(child.state)
            for child in node.children
        ]
        return node.children[np.argmax(ucb_values)]

    def expand(self, node: Node) -> Node:
        if self.aggregate:
            agg_state = self.aggregate_state(node.state)
            new_agg_state = self.model['transition'](agg_state)
            new_agg_state = self.perturb_state(new_agg_state)
            new_state = self.disaggregate_state(new_agg_state, node.state)
        else:
            new_state = self.model['transition'](node.state)
            new_state = self.perturb_state(new_state)
        child = Node(new_state, parent=node)
        node.children.append(child)
        return child

    def perturb_state(self, state: Dict) -> Dict:
        new_state = state.copy()
        t = state['t']

        if self.aggregate:
            for var in ['L', 'K', 'w']:
                for sector in ['firm1', 'firm2']:
                    new_state[var][sector] *= (1 + np.random.normal(0, self.config['perturbation_scale']))
                    new_state[var][sector] = max(new_state[var][sector], 0)
            new_state['p'] *= (1 + np.random.normal(0, self.config['perturbation_scale']))
            new_state['p'] = max(new_state['p'], 0)
        else:
            for var in ['L', 'K', 'w']:
                if t not in new_state[var]:
                    new_state[var][t] = {firm: 0 for firm in self.model['sets']['F']}
                for firm in self.model['sets']['F']:
                    new_state[var][t][firm] *= (1 + np.random.normal(0, self.config['perturbation_scale']))
                    new_state[var][t][firm] = max(new_state[var][t][firm], 0)

            if t not in new_state['p']:
                new_state['p'][t] = 1.0
            new_state['p'][t] *= (1 + np.random.normal(0, self.config['perturbation_scale']))
            new_state['p'][t] = max(new_state['p'][t], 0)

        return new_state

    def simulate(self, node: Node) -> float:
        if node.state['t'] == self.max_time_steps - 1:
            return self.nn_handler.predict_value(node.state)

        state = node.state.copy()
        cumulative_value = 0
        discount_factor = 1

        while state['t'] < self.max_time_steps - 1:
            if not self.check_constraints(state):
                return float('-inf')

            cumulative_value += discount_factor * self.model['objective'](state)
            discount_factor *= (1 / (1 + self.model['parameters']['delta']))

            state = self.model['transition'](state)
            state = self.perturb_state(state)

        return cumulative_value

    def check_constraints(self, state: Dict) -> bool:
        t = state['t']
        return all(constraint(state, t) for constraint in self.model['constraints'])

    def backpropagate(self, node: Node, value: float):
        while node:
            node.visits += 1
            node.value += value
            node = node.parent

    def aggregate_state(self, state: Dict) -> Dict:
        t = state['t']
        agg_state = {
            't': t,
            'L': {'firm1': sum(state['L'][t][f] for f in self.F1),
                  'firm2': sum(state['L'][t][f] for f in self.F2)},
            'K': {'firm1': sum(state['K'][t][f] for f in self.F1),
                  'firm2': sum(state['K'][t][f] for f in self.F2)},
            'w': {'firm1': sum(state['w'][t][f] * state['L'][t][f] for f in self.F1) /
                           sum(state['L'][t][f] for f in self.F1),
                  'firm2': sum(state['w'][t][f] * state['L'][t][f] for f in self.F2) /
                           sum(state['L'][t][f] for f in self.F2)},
            'p': state['p'][t]
        }
        return agg_state

    def disaggregate_state(self, agg_state: Dict, original_state: Dict) -> Dict:
        new_state = original_state.copy()
        t = agg_state['t']

        for sector, firms in [('firm1', self.F1), ('firm2', self.F2)]:
            L_total = sum(original_state['L'][t][f] for f in firms)
            K_total = sum(original_state['K'][t][f] for f in firms)
            for f in firms:
                new_state['L'][t][f] = agg_state['L'][sector] * (original_state['L'][t][f] / L_total)
                new_state['K'][t][f] = agg_state['K'][sector] * (original_state['K'][t][f] / K_total)
                new_state['w'][t][f] = agg_state['w'][sector]

        new_state['p'][t] = agg_state['p']
        return new_state

def run_mcts_solver(model: Dict, config: Dict, nn_handler) -> Tuple[List[Dict], List[Tuple[Dict, float]]]:
    solver = MCTSSolver(model, config, nn_handler)
    best_path = solver.solve()

    training_data = []
    for node in solver.get_all_nodes():
        if node.visits > 0:
            training_data.append((node.state, node.value / node.visits))

    return best_path, training_data

# Example usage
if __name__ == "__main__":
    from model import define_model

    model = define_model()
    config = {
        'num_iterations': 1000,
        'exploration_weight': 1.4,
        'perturbation_scale': 0.1,
        'aggregate': True  # Set to True to use aggregation
    }

    best_path = run_mcts_solver(model, config)
    print(f"Found solution path of length {len(best_path)}")
    for t, state in enumerate(best_path):
        print(f"Time step {t}:")
        print(f"  Total Labor: {sum(state['L'][t].values()):.2f}")
        print(f"  Total Capital: {sum(state['K'][t].values()):.2f}")
        print(f"  Average Wage: {np.mean(list(state['w'][t].values())):.2f}")
        print(f"  Price: {state['p'][t]:.2f}")
    print(f"Final objective value: {model['objective'](best_path[-1]):.2f}")
