import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

class KPIAnalysis:
    def __init__(self, df, labels):
        self.df = df
        self.labels = labels
        self.kpis = df.columns[:-1]  # Extract KPI feature names (should be 16)
        self.num_kpis = len(self.kpis)
    
    def calc_mean(self, data, cl, no_zeros=False):
        if no_zeros and cl != 3:  # For control classes, don't exclude zero KPI rows
            data = data.loc[(data == 0).astype(int).sum(axis=1) < 11]  # Ignore rows with more than 11 KPIs as zero
        return data.mean().tolist()[:-1]

    def calc_std(self, data, cl, no_zeros=False):
        if no_zeros and cl != 3:  # For control classes, don't exclude zero KPI rows
            data = data.loc[(data == 0).astype(int).sum(axis=1) < 11]  # Ignore rows with more than 11 KPIs as zero
        return data.std().tolist()[:-1]

    def plot_kpi_analysis(self, no_zeros=False):
        x = np.arange(self.num_kpis)  # Generate x-axis values

        # Create a 2x2 grid of subplots (one for each traffic class)
        fig, ax = plt.subplots(2, 2, figsize=(18, 10))

        # Loop through the traffic classes and calculate means and std deviations
        for i in range(2):
            for j in range(2):
                class_id = i * 2 + j  # Compute class index (0, 1, 2, 3)

                # Compute KPI means and standard deviations for the given class
                kpi_means = self.calc_mean(self.df[self.df['label'] == class_id], class_id, no_zeros)
                kpi_stds = self.calc_std(self.df[self.df['label'] == class_id], class_id, no_zeros)

                # Plot bar chart for KPI statistics
                ax[i][j].bar(
                    x, kpi_means,
                    yerr=kpi_stds,
                    align='center', alpha=0.7, ecolor='black', capsize=4
                )

                # Formatting the subplot
                ax[i][j].set_title(f"Traffic Class: {self.labels[class_id]}", fontsize=14, fontweight='bold')
                ax[i][j].set_xlabel("KPI Features", fontsize=12)
                ax[i][j].set_ylabel("Mean Value", fontsize=12)
                ax[i][j].set_xticks(x)  # Set x-ticks
                ax[i][j].set_xticklabels(self.kpis, rotation=45, ha='right', fontsize=10)  # Assign KPI names as labels

        # Adjust layout to prevent overlap
        plt.tight_layout()

        # Show the plot
        plt.show()

    def print_kpi_names(self):
        # Print KPI index and names
        for i in range(self.num_kpis):
            print(f"{i}: {self.kpis[i]}", end=" ; ")


