from sklearn.decomposition import PCA
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D

class PCAAnalysis:
    def __init__(self, df, n_components=6):
        self.df = df
        self.kpis = df.columns[:-1]  # Extract KPI features (excluding label)
        self.n_components = n_components
        self.X = df[self.kpis].values  # Convert to numpy array
        self.pca = PCA(n_components=n_components)
        self.X_pca = self.pca.fit_transform(self.X)  # PCA transformation
        self.explained_variance = self.pca.explained_variance_ratio_

    def explained_variance_summary(self):
        # Output the cumulative and total explained variance
        print(f"Explained Variance per Component: {self.explained_variance}")
        print(f"Cumulative Variance Explained: {self.explained_variance.cumsum()}")
        print(f"Total Variance Explained: {self.explained_variance.sum()}")

    def plot_2d_pca(self):
        # Create a dataframe with PCA components and label
        df_pca = pd.DataFrame(self.X_pca, columns=[f'PC{i+1}' for i in range(self.n_components)])
        df_pca['label'] = self.df['label'].reset_index(drop=True)

        # Scatter plot for first two principal components
        plt.figure(figsize=(12, 6))
        sns.scatterplot(
            x=df_pca["PC1"], y=df_pca["PC2"],
            hue=df_pca["label"],  # Color by class labels
            palette="tab10",
            alpha=0.5
        )
        plt.title("PCA: First Two Principal Components")
        plt.xlabel("PC1")
        plt.ylabel("PC2")
        plt.legend(title="Class")
        plt.show()

    def plot_3d_pca(self):
        # Create a dataframe with PCA components and label
        df_pca = pd.DataFrame(self.X_pca, columns=[f'PC{i+1}' for i in range(self.n_components)])
        df_pca['label'] = self.df['label'].reset_index(drop=True)

        # 3D scatter plot for the first three principal components
        fig = plt.figure(figsize=(10, 7))
        ax = fig.add_subplot(111, projection='3d')

        # Scatter plot using first 3 PCs
        ax.scatter(df_pca["PC1"], df_pca["PC2"], df_pca["PC3"],
                   c=pd.factorize(df_pca["label"])[0], cmap="tab10", alpha=0.6)

        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.set_zlabel("PC3")
        ax.set_title("PCA: First Three Principal Components")
        plt.show()

    def get_pca_components(self):
        # Return PCA components
        return self.pca.components_

    def get_pca_dataframe(self):
        # Return the transformed data as a DataFrame
        df_pca = pd.DataFrame(self.X_pca, columns=[f'PC{i+1}' for i in range(self.n_components)])
        df_pca['label'] = self.df['label'].reset_index(drop=True)
        return df_pca


