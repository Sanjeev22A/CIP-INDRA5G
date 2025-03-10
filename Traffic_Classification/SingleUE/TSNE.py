import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler

class TSNEAnalysis:
    def __init__(self, df, n_components=2, perplexity=30, n_iter=300, random_state=42):
        """
        Initialize the TSNEAnalysis class with the dataframe and t-SNE parameters.
        
        :param df: DataFrame containing the feature columns and a 'label' column for class labels.
        :param n_components: Number of components for t-SNE transformation (default is 2).
        :param perplexity: Perplexity for t-SNE (default is 30).
        :param n_iter: Number of iterations for t-SNE (default is 300).
        :param random_state: Random state for reproducibility (default is 42).
        """
        self.df = df
        self.features = df.drop(columns=['label'])  # Features excluding 'label'
        self.labels = df['label']  # Class labels
        self.n_components = n_components
        self.perplexity = perplexity
        self.n_iter = n_iter
        self.random_state = random_state

        # Perform t-SNE transformation
        self.tsne = TSNE(n_components=n_components, perplexity=perplexity, random_state=random_state, 
                         verbose=1, n_iter=n_iter)
        self.tsne_results = self.tsne.fit_transform(self.features)

        # Create a DataFrame with t-SNE results
        self.df_tsne = pd.DataFrame({'TSNE-1': self.tsne_results[:, 0], 'TSNE-2': self.tsne_results[:, 1], 'label': self.labels})

    def plot_tsne(self):
        """
        Plot the 2D t-SNE visualization using seaborn.
        """
        plt.figure(figsize=(10, 7))

        # Create a scatter plot using Seaborn
        sns.scatterplot(
            x="TSNE-1", y="TSNE-2",
            hue=self.df_tsne["label"],  # Color by label/class
            palette="tab10",  # Use a distinct color palette
            data=self.df_tsne,
            alpha=0.7  # Set transparency for better visibility
        )

        # Set title and labels
        plt.title("t-SNE Visualization of Features")
        plt.xlabel("t-SNE Component 1")
        plt.ylabel("t-SNE Component 2")

        # Show the legend
        plt.legend(title="Class Labels", bbox_to_anchor=(1.05, 1), loc='upper left')

        # Display the plot
        plt.show()

    def get_tsne_results(self):
        """
        Return the t-SNE results as a DataFrame for further analysis.
        """
        return self.df_tsne

