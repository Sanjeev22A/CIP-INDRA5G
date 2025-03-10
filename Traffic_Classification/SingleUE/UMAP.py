import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import umap

class UMAPAnalysis:
    def __init__(self, df, n_components=2, n_neighbors=30, min_dist=0.3, random_state=42):
        """
        Initialize the UMAPAnalysis class with the dataframe and UMAP parameters.
        
        :param df: DataFrame containing the feature columns and a 'label' column for class labels.
        :param n_components: Number of components for UMAP transformation (default is 2).
        :param n_neighbors: Number of neighbors for UMAP (default is 30).
        :param min_dist: Minimum distance between points for UMAP (default is 0.3).
        :param random_state: Random state for reproducibility (default is 42).
        """
        self.df = df
        self.features = df.drop(columns=['label'])  # Features excluding 'label'
        self.labels = df['label']  # Class labels
        self.n_components = n_components
        self.n_neighbors = n_neighbors
        self.min_dist = min_dist
        self.random_state = random_state

        # Perform UMAP transformation
        self.umap = umap.UMAP(n_components=n_components, n_neighbors=n_neighbors, min_dist=min_dist, random_state=random_state)
        self.umap_results = self.umap.fit_transform(self.features)

        # Create a DataFrame with UMAP results
        self.df_umap = pd.DataFrame(self.umap_results, columns=[f'UMAP-{i+1}' for i in range(n_components)])
        self.df_umap['label'] = self.labels.values

    def plot_umap(self):
        """
        Plot the 2D UMAP visualization using seaborn.
        """
        plt.figure(figsize=(10, 7))

        # Create a scatter plot using Seaborn
        sns.scatterplot(
            x='UMAP-1', y='UMAP-2',
            hue=self.df_umap['label'],
            palette=sns.color_palette('hsv', len(self.df_umap['label'].unique())),
            alpha=0.7,
            data=self.df_umap
        )

        # Set title and labels
        plt.title("UMAP Dimensionality Reduction (2D)")
        plt.xlabel("UMAP-1")
        plt.ylabel("UMAP-2")
        plt.legend(title="Traffic Class")

        # Display the plot
        plt.show()

    def get_umap_results(self):
        """
        Return the UMAP results as a DataFrame for further analysis.
        """
        return self.df_umap

