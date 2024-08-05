import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('economic_model_data.csv')

# Separate features and targets
X = df.drop(['actual_demand', 'sales', 'firm_id'], axis=1)
y_demand = df['actual_demand']
y_sales = df['sales']

# Split the data
X_train, X_test, y_demand_train, y_demand_test, y_sales_train, y_sales_test = train_test_split(
    X, y_demand, y_sales, test_size=0.2, random_state=42
)

# Scale the features
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# Function to evaluate models
def evaluate_model(model, X_train, X_test, y_train, y_test, model_name, target_name):
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"{model_name} - {target_name}")
    print(f"MSE: {mse:.4f}")
    print(f"R2 Score: {r2:.4f}")
    print("Cross-validation scores:")
    cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring='r2')
    print(f"R2 scores: {cv_scores}")
    print(f"Mean R2: {np.mean(cv_scores):.4f}")
    print()

    # Feature importance for Random Forest
    if isinstance(model, RandomForestRegressor):
        feature_importance = model.feature_importances_
        features = X.columns
        plt.figure(figsize=(10, 6))
        plt.bar(features, feature_importance)
        plt.title(f"Feature Importance - {model_name} ({target_name})")
        plt.xticks(rotation=90)
        plt.tight_layout()
        plt.show()

# Linear Regression
lr_demand = LinearRegression()
lr_sales = LinearRegression()

evaluate_model(lr_demand, X_train_scaled, X_test_scaled, y_demand_train, y_demand_test, "Linear Regression", "Demand")
evaluate_model(lr_sales, X_train_scaled, X_test_scaled, y_sales_train, y_sales_test, "Linear Regression", "Sales")

# Random Forest
rf_demand = RandomForestRegressor(n_estimators=100, random_state=42)
rf_sales = RandomForestRegressor(n_estimators=100, random_state=42)

evaluate_model(rf_demand, X_train_scaled, X_test_scaled, y_demand_train, y_demand_test, "Random Forest", "Demand")
evaluate_model(rf_sales, X_train_scaled, X_test_scaled, y_sales_train, y_sales_test, "Random Forest", "Sales")

# Analyze differences between Firm1 and Firm2
firm1_data = df[df['firm_id'].isin([30, 31])]
firm2_data = df[df['firm_id'].isin(range(32, 37))]

print("Firm1 data summary:")
print(firm1_data.describe())
print("\nFirm2 data summary:")
print(firm2_data.describe())

# You can add more analysis here, such as correlation matrices, scatter plots, etc.