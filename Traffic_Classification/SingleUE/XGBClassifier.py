import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

class XGBModel:
    def __init__(self, data, label_column, test_size=0.2, n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42):
        """
        Initialize the XGBModel class with dataset and parameters.
        
        :param data: DataFrame containing the features and the label column.
        :param label_column: Name of the label column in the dataset.
        :param test_size: Proportion of the data to be used for testing (default is 0.2).
        :param n_estimators: Number of trees in the XGBoost model (default is 100).
        :param learning_rate: Step size shrinkage used in the model (default is 0.1).
        :param max_depth: Maximum depth of trees (default is 6).
        :param random_state: Random state for reproducibility (default is 42).
        """
        self.data = data
        self.label_column = label_column
        self.test_size = test_size
        self.n_estimators = n_estimators
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.random_state = random_state

        # Extract features and labels
        self.X = self.data.drop(columns=[self.label_column])  # Features
        self.y = self.data[self.label_column]  # Labels

        # Split the data into training and testing sets
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=self.test_size, random_state=self.random_state, stratify=self.y)

        # Initialize the XGBClassifier
        self.xgb_model = XGBClassifier(
            n_estimators=self.n_estimators,
            learning_rate=self.learning_rate,
            max_depth=self.max_depth,
            random_state=self.random_state
        )

    def train(self):
        """Train the XGBoost model."""
        self.xgb_model.fit(self.X_train, self.y_train)

    def predict(self):
        """Make predictions using the trained model."""
        return self.xgb_model.predict(self.X_test)

    def evaluate(self, y_pred):
        """Evaluate the model's performance."""
        # Compute Accuracy
        accuracy = accuracy_score(self.y_test, y_pred)
        print(f"XGBoost Accuracy: {accuracy:.2f}")
        
        # Print Classification Report
        print("\nClassification Report:\n", classification_report(self.y_test, y_pred))

        # Compute Confusion Matrix
        conf_matrix = confusion_matrix(self.y_test, y_pred)
        
        # Visualize Confusion Matrix
        plt.figure(figsize=(6, 5))
        sns.heatmap(conf_matrix, annot=True, fmt="d", cmap="Blues", xticklabels=np.unique(self.y), yticklabels=np.unique(self.y))
        plt.xlabel("Predicted Label")
        plt.ylabel("True Label")
        plt.title("Confusion Matrix - XGBoost")
        plt.show()

    def run(self):
        """Train the model, make predictions, and evaluate the results."""
        self.train()
        y_pred = self.predict()
        self.evaluate(y_pred)

