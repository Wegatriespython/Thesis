import torch
import torch.nn as nn
import torch.optim as optim
from typing import Dict, List, Tuple
import numpy as np

class EconomicNN(nn.Module):
    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super(EconomicNN, self).__init__()
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size)
        )

    def forward(self, x):
        return self.network(x)

class NNHandler:
    def __init__(self, model: Dict, config: Dict):
        self.model = model
        self.config = config
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        input_size = self._calculate_input_size()
        self.nn = EconomicNN(input_size, config['hidden_size'], 1).to(self.device)
        self.optimizer = optim.Adam(self.nn.parameters(), lr=config['learning_rate'])
        self.criterion = nn.MSELoss()

    def _calculate_input_size(self) -> int:
        # Calculate input size based on model structure
        num_firms = len(self.model['sets']['F'])
        return 1 + 3 * num_firms + 1  # t, L, K, w for each firm, and p

    def state_to_tensor(self, state: Dict) -> torch.Tensor:
        t = state['t']
        features = [t]
        for firm in self.model['sets']['F']:
            features.extend([
                state['L'][t][firm],
                state['K'][t][firm],
                state['w'][t][firm]
            ])
        features.append(state['p'][t])
        return torch.tensor(features, dtype=torch.float32).unsqueeze(0).to(self.device)
    def predict_value(self, state: Dict) -> float:
        self.nn.eval()
        with torch.no_grad():
            state_tensor = self.state_to_tensor(state)
            value = self.nn(state_tensor)
        return value.item()

    def train(self, states: List[Dict], values: List[float]):
        self.nn.train()
        state_tensors = torch.cat([self.state_to_tensor(state) for state in states])
        value_tensors = torch.tensor(values, dtype=torch.float32).unsqueeze(1).to(self.device)

        for _ in range(self.config['train_iterations']):
            self.optimizer.zero_grad()
            predictions = self.nn(state_tensors)
            loss = self.criterion(predictions, value_tensors)
            loss.backward()
            self.optimizer.step()

    def update_mcts_config(self, mcts_config: Dict) -> Dict:
        # Update MCTS config to use NN for value estimation
        def nn_evaluation(state: Dict) -> float:
            return self.predict_value(state)

        mcts_config['value_estimation'] = nn_evaluation
        return mcts_config

def create_nn_handler(model: Dict, config: Dict) -> NNHandler:
    nn_config = {
        'hidden_size': 64,
        'learning_rate': 0.001,
        'train_iterations': 100
    }
    nn_config.update(config.get('nn_config', {}))
    return NNHandler(model, nn_config)

# Example usage
if __name__ == "__main__":
    from MCTS_Solver.model import define_model

    model = define_model()
    config = {
        'nn_config': {
            'hidden_size': 128,
            'learning_rate': 0.0005,
            'train_iterations': 200
        }
    }

    nn_handler = create_nn_handler(model, config)

    # Example of training
    example_states = [model['initial_state']() for _ in range(10)]
    example_values = [model['objective'](state) for state in example_states]
    nn_handler.train(example_states, example_values)

    # Example of prediction
    test_state = model['initial_state']()
    predicted_value = nn_handler.predict_value(test_state)
    print(f"Predicted value for test state: {predicted_value:.4f}")

    # Example of updating MCTS config
    mcts_config = {'some_existing_config': 'value'}
    updated_mcts_config = nn_handler.update_mcts_config(mcts_config)
    print("Updated MCTS config:", updated_mcts_config)