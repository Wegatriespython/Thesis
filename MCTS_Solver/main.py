import json
from typing import Dict, List
import matplotlib.pyplot as plt
from model import define_model
from solver import run_mcts_solver
from neural_network import create_nn_handler
import logging
import numpy as np

def load_config(config_file: str) -> Dict:
    with open(config_file, 'r') as f:
        return json.load(f)

def setup_logging():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def plot_results(best_path: List[Dict], model: Dict):
    T = model['sets']['T']
    F = model['sets']['F']

    fig, axs = plt.subplots(2, 2, figsize=(15, 10))

    # Adjust plotting for aggregated results if necessary
    if isinstance(best_path[0]['L'], dict) and 'firm1' in best_path[0]['L']:  # Check if results are aggregated
        axs[0, 0].plot(T, [state['L']['firm1'] + state['L']['firm2'] for state in best_path])
        axs[0, 1].plot(T, [state['K']['firm1'] + state['K']['firm2'] for state in best_path])
        axs[1, 0].plot(T, [(state['w']['firm1'] * state['L']['firm1'] + state['w']['firm2'] * state['L']['firm2']) /
                           (state['L']['firm1'] + state['L']['firm2']) for state in best_path])
        axs[1, 1].plot(T, [state['p'] for state in best_path])
    else:
        axs[0, 0].plot(T, [sum(state['L'][t].values()) for state in best_path for t in [state['t']]])
        axs[0, 1].plot(T, [sum(state['K'][t].values()) for state in best_path for t in [state['t']]])
        axs[1, 0].plot(T, [np.mean(list(state['w'][t].values())) for state in best_path for t in [state['t']]])
        axs[1, 1].plot(T, [state['p'][t] for state in best_path for t in [state['t']]])

    axs[0, 0].set_title('Total Labor')
    axs[0, 1].set_title('Total Capital')
    axs[1, 0].set_title('Average Wage')
    axs[1, 1].set_title('Price')

    for ax in axs.flat:
        ax.set(xlabel='Time')

    axs[0, 0].set(ylabel='Labor')
    axs[0, 1].set(ylabel='Capital')
    axs[1, 0].set(ylabel='Wage')
    axs[1, 1].set(ylabel='Price')

    plt.tight_layout()
    plt.savefig('economic_model_results.png')
    plt.close()

def main():
    setup_logging()
    try:
        config = load_config('config.json')
        logging.info("Configuration loaded")

        use_aggregation = config.get('aggregate', True)
        model = define_model(aggregate=use_aggregation)
        logging.info(f"Economic model defined with aggregation: {use_aggregation}")

        nn_handler = create_nn_handler(model, config)
        logging.info("Neural network handler created")

        mcts_config = config.get('mcts_config', {})
        mcts_config['aggregate'] = use_aggregation

        for iteration in range(config.get('num_global_iterations', 1)):
            logging.info(f"Starting global iteration {iteration + 1}")

            best_path, training_data = run_mcts_solver(model, mcts_config, nn_handler)
            logging.info("MCTS solver completed")

            # Train neural network on MCTS results
            if training_data:
                states, values = zip(*training_data)
                nn_handler.train(states, values)
                logging.info("Neural network trained on MCTS results")

            # Log intermediate results
            if best_path:
                intermediate_objective = model['objective'](best_path[-1])
                logging.info(f"Intermediate objective value: {intermediate_objective:.4f}")

        # Plot and save final results
        if best_path:
            plot_results(best_path, model)
            logging.info("Final results plotted and saved")

            # Print final objective value
            final_objective = model['objective'](best_path[-1])
            logging.info(f"Final objective value: {final_objective:.4f}")
        else:
            logging.warning("No solution path found")

    except FileNotFoundError:
        logging.error("Config file not found. Please ensure 'config.json' exists in the current directory.")
    except json.JSONDecodeError:
        logging.error("Error parsing the config file. Please ensure it's valid JSON.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()
