# Import necessary classes
from Preprocessing import Preprocessing
from Analysis import KPIAnalysis
from GraphViewer import GraphView
from PCA import PCAAnalysis
from TSNE import TSNEAnalysis
from UMAP import UMAPAnalysis
from RandomForest import RandomForestModel
from XGBClassifier import XGBModel
from SVM import SVMModel

# Define the trials, data path, and labels
TRIALS = ['Trial1', 'Trial2', 'Trial3', 'Trial4', 'Trial5', 'Trial6']
data_path = '/content/drive/My Drive/6G/CIP_Group_Sanjeev/logs/SingleUE/'
labels = {0: 'eMBB', 1: 'mMTC', 2: 'URLLC', 3: 'ctrl'}

# Function to preprocess the data and generate slice data
def preprocess_data():
    preprocessor = Preprocessing(data_path, labels, normalise=True, mode="emuc")
    df, col_max = preprocessor.gen_slice_data(TRIALS)
    return df, col_max

# Function to generate and display graphs
def generate_graphs(df):
    graph_view = GraphView(df, labels)
    graph_view.generate_graphs()

# Function to perform KPI analysis and display results
def perform_kpi_analysis(df):
    kpi_analysis = KPIAnalysis(df, labels)
    kpi_analysis.plot_kpi_analysis(no_zeros=False)
    kpi_analysis.print_kpi_names()
    kpi_analysis.plot_kpi_analysis(no_zeros=True)
    kpi_analysis.print_kpi_names()

# Function to perform PCA analysis and return the transformed dataframe
def perform_pca_analysis(df, n_components=6):
    pca_analysis = PCAAnalysis(df, n_components=n_components)
    pca_analysis.explained_variance_summary()
    pca_analysis.plot_2d_pca()
    pca_analysis.plot_3d_pca()

    # Get PCA results as a dataframe
    df_pca = pca_analysis.get_pca_results()
    return df_pca

# Function to perform t-SNE analysis and return the transformed dataframe
def perform_tsne_analysis(df):
    tsne_analysis = TSNEAnalysis(df)
    tsne_analysis.plot_tsne()

    # Get t-SNE results as a dataframe
    df_tsne = tsne_analysis.get_tsne_results()
    return df_tsne

# Function to perform UMAP analysis and return the transformed dataframe
def perform_umap_analysis(df):
    umap_analysis = UMAPAnalysis(df)
    umap_analysis.plot_umap()

    # Get UMAP results as a dataframe
    df_umap = umap_analysis.get_umap_results()
    return df_umap

# Function to train and evaluate Random Forest model
def run_random_forest(df_pca):
    rf_model = RandomForestModel(data=df_pca, label_column='label')
    rf_model.run()

# Function to train and evaluate XGBoost model
def run_xgboost(df_pca):
    xgb_model = XGBModel(data=df_pca, label_column='label')
    xgb_model.run()

# Function to train and evaluate SVM model
def run_svm(df_pca):
    svm_model = SVMModel(data=df_pca, label_column='label')
    svm_model.run()

# Main function that drives all processes and returns transformed dataframes
def main():
    # Step 1: Preprocess data
    df, col_max = preprocess_data()
    print(df.head())

    # Step 2: Perform PCA analysis and get the PCA dataframe
    df_pca = perform_pca_analysis(df)
    print("PCA results:")
    print(df_pca.head())

    # Step 3: Perform t-SNE analysis and get the t-SNE dataframe
    df_tsne = perform_tsne_analysis(df)
    print("t-SNE results:")
    print(df_tsne.head())

    # Step 4: Perform UMAP analysis and get the UMAP dataframe
    df_umap = perform_umap_analysis(df)
    print("UMAP results:")
    print(df_umap.head())

    # Step 5: Optionally train models using the transformed data (df_pca, df_tsne, df_umap)
    run_random_forest(df_pca)  # You can use df_tsne or df_umap for training as well
    run_xgboost(df_pca)
    run_svm(df_pca)

    run_random_forest(df_tsne)
    run_xgboost(df_tsne)  
    run_svm(df_tsne)

    run_xgboost(df_umap)
    run_svm(df_umap)    
    run_random_forest(df_umap)

# Run the main function
if __name__ == "__main__":
    main()
