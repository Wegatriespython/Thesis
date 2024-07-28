# Project Overview and Guidelines: Agent-Based Macroeconomic Model

## Project Structure

Our project is an agent-based macroeconomic model with a focus on low-carbon innovation and labor markets. The codebase is hosted on GitHub under the repository "Weugatriespython/Thesis".

### Current Structure:
```
Thesis/
├── .github/
│   └── workflows/
│       └── python-tests.yml
├── tests/
│   └── test_worker.py
├── Worker.py
├── Basefirm.py
├── Config.py
├── Main.py
├── Scheduler.py
├── Stats.py
├── Wageoffer.py
├── economy.py
├── firm1.py
├── firm2.py
├── requirements.txt
└── README.md
```

## GitHub and Version Control

- Repository: https://github.com/Weugatriespython/Thesis
- Main branch: `main`
- Development branch: `Test`

We use GitHub for version control and collaboration. All significant changes should be made through pull requests from feature branches to the `Test` branch, and then from `Test` to `main` after thorough testing.

## Testing Framework

We use pytest for our testing suite. Currently, we have basic tests set up for the Worker class in `tests/test_worker.py`.

### Running Tests:
Tests can be run locally using:
```
python -m pytest tests/
```

Our GitHub Actions workflow automatically runs tests on every push and pull request.

## Future Expansion Plans for Testing

1. Expand test coverage:
   - Create test files for all major classes (Firm1, Firm2, Economy, etc.)
   - Aim for at least 80% code coverage

2. Implement integration tests:
   - Test interactions between different components (e.g., workers and firms)
   - Simulate small-scale model runs in tests

3. Performance testing:
   - Implement tests to measure and track model performance
   - Set benchmarks for simulation speed and resource usage

4. Data validation tests:
   - Ensure output data meets expected formats and ranges
   - Test data collection and statistics generation

5. Scenario testing:
   - Develop a suite of economic scenarios to test model behavior
   - Include edge cases and stress tests

6. Continuous Integration enhancements:
   - Implement code quality checks (e.g., flake8, black) in CI pipeline
   - Add automated performance benchmarking to CI

## Code Maintenance Guidelines

1. Code Style:
   - Follow PEP 8 guidelines for Python code style
   - Use meaningful variable and function names
   - Include docstrings for all classes and functions

2. Version Control:
   - Create feature branches for all new developments
   - Write clear, concise commit messages
   - Regularly pull changes from the main branch to stay updated

3. Documentation:
   - Keep the README.md up to date with project overview and setup instructions
   - Document complex algorithms and model assumptions in-line
   - Maintain a separate documentation folder for detailed explanations

4. Code Reviews:
   - All pull requests must be reviewed by at least one other team member
   - Use GitHub's code review features for discussions and suggestions

5. Testing:
   - Write tests for all new features before merging
   - Maintain and update existing tests as the codebase evolves
   - Aim to increase test coverage with each major update

6. Dependency Management:
   - Keep `requirements.txt` updated with all project dependencies
   - Regularly check for and update to newer, stable versions of dependencies

7. Performance Optimization:
   - Profile the code regularly to identify bottlenecks
   - Optimize critical sections of the code for better performance
   - Consider using Cython for performance-critical components

8. Data Handling:
   - Use efficient data structures (e.g., NumPy arrays for large datasets)
   - Implement proper error handling for data processing
   - Ensure data privacy and security in all operations

9. Modular Design:
   - Keep classes and functions focused on single responsibilities
   - Use inheritance and composition effectively
   - Design for extensibility to accommodate future model expansions

10. Regular Maintenance:
    - Schedule regular code cleanup sessions
    - Refactor code as needed to maintain clarity and efficiency
    - Address technical debt proactively

By following these guidelines, we aim to maintain a robust, efficient, and extensible codebase for our agent-based macroeconomic model. Regular reviews and updates to these guidelines are encouraged as the project evolves.