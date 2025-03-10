import matplotlib.pyplot as plt

class GraphView:
    def __init__(self, df, labels):
        self.df = df
        self.labels = labels
        self.labels_list = []
        self.zero_percent_list = []

    def plot_traffic_class_distribution(self):
        # Count occurrences of each class
        col = [len(self.df[self.df['label'] == c]) for c in self.labels]
        print(col)

        # Plot the traffic class distribution bar graph
        plt.figure(figsize=(8, 5))
        plt.bar(self.labels.values(), col, color=['blue', 'red', 'green', 'purple'])

        # Labels and title
        plt.xlabel("Traffic Class")
        plt.ylabel("Count")
        plt.title("Traffic Class Distribution")
        plt.show()

    def calculate_zero_populated_rows(self):
        # Calculate the zero-populated rows for each class
        for i in self.labels.keys():
            print("Class : ", self.labels[i], "Entries : ", len(self.df[self.df['label'] == i]))
            zero_rows = len(self.df[(self.df['label'] == i) & ((self.df == 0).astype(int).sum(axis=1) > 11)])
            n_samples = len(self.df[self.df['label'] == i])
            self.labels_list.append(self.labels[i])
            self.zero_percent_list.append(round(zero_rows / n_samples * 100, 2))
            print(f"Out of {n_samples} samples, {zero_rows} are Zero populated rows which is about {round(zero_rows / n_samples * 100, 2)}%")

        print("\nRows with more than 11 zero KPIs are zero populated rows")

    def plot_zero_populated_rows(self):
        # Plotting the percentage of zero-populated rows per traffic class
        plt.figure(figsize=(10, 5))
        plt.bar(self.labels_list, self.zero_percent_list, color=['blue', 'red', 'green', 'purple'])
        plt.xlabel("Traffic Classes")
        plt.ylabel("Percentage of Zero Populated Rows")
        plt.title("Zero Populated Rows Percentage KPI rows per class")
        plt.ylim(0, 100)
        plt.grid(axis="y", linestyle="--", alpha=0.7)
        plt.show()

    def generate_graphs(self):
        # Method to calculate and plot both graphs
        self.plot_traffic_class_distribution()
        self.calculate_zero_populated_rows()
        self.plot_zero_populated_rows()



