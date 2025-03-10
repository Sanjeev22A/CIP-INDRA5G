import numpy as np
import pandas as pd
import os
import sys
from tqdm import tqdm
import pickle
import time
from glob import glob
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import seaborn as sns
import numpy as np
from scipy.spatial.distance import cdist
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE

#from google.colab import drive
#drive.mount('/content/drive',force_remount=True)


class Preprocessing:
    def __init__(self, data_path, labels, normalise=False, mode="emuc"):
        self.data_path = data_path
        self.labels = labels
        self.normalise = normalise
        self.mode = mode

    def load_csv_dataset(self, data_path, isControlClass, trial):
        # Access the embb_clean files and then get their data and convert into dataframe
        embb_files = glob(os.path.join(data_path, os.path.join(trial, "embb_*clean.csv")))
        print(os.path.join(data_path, os.path.join(trial, "embb_*clean.csv")))

        embb_data = pd.concat([pd.read_csv(f, sep=",") for f in embb_files])
        embb_data['label'] = [0 for i in range(len(embb_data))]
        
        # Access the mmtc_clean files and then get their data and convert into dataframe
        mmtc_files = glob(os.path.join(data_path, os.path.join(trial, "mmtc_*clean.csv")))
        mmtc_data = pd.concat([pd.read_csv(f, sep=",") for f in mmtc_files])
        mmtc_data['label'] = [1 for i in range(len(mmtc_data))]

        # If the column ul_rssi is present in mmtc, just drop it for column alignment
        if 'ul_rssi' in mmtc_data.columns:
            mmtc_data = mmtc_data.drop(['ul_rssi'], axis=1)
        if 'ul_rssi' in embb_data.columns:
            embb_data = embb_data.drop(['ul_rssi'], axis=1)
        
        # Access the urllc_clean files and then get their data and convert into dataframe
        urllc_files = glob(os.path.join(data_path, os.path.join(trial, "urllc*_*clean.csv")))
        urllc_data = pd.concat([pd.read_csv(f, sep=",") for f in urllc_files])
        urllc_data['label'] = [2 for i in range(len(urllc_data))]
        
        print(os.path.join(data_path, os.path.join(trial, "urllc*_*clean.csv")))

        # If the control class is present, access it from null_clean.csv file and then concat it
        if isControlClass and os.path.exists(os.path.join(data_path, os.path.join(trial, "null_clean.csv"))):
            ctrl_data = pd.read_csv(os.path.join(data_path, os.path.join(trial, "null_clean.csv")), sep=",")
            ctrl_data['label'] = [3 for i in range(len(ctrl_data))]
            df = pd.concat([embb_data, mmtc_data, urllc_data, ctrl_data])
        else:
            df = pd.concat([embb_data, mmtc_data, urllc_data])

        # Drop unnecessary columns like timestamp, tc_errors downlink, and dl_cqi
        columns_drop = ['Timestamp', 'tx_errors downlink (%)']
        df.drop(columns_drop, axis=1, inplace=True)
        return df

    def gen_slice_data(self, trials):
        isControlClass = True if "c" in self.mode else False
        df = pd.DataFrame()
        for ix, trial in enumerate(trials):
            print(f"Generating dataframe: {trial}")

            new_df = self.load_csv_dataset(self.data_path, isControlClass, trial)
            df = pd.concat([df, new_df])

        # Normalize the data if required
        columns_maxim = {}
        if self.normalise:
            for i in df.columns:
                if i != 'label':
                    col = df[i]
                    val_max = df[i].max()
                    val_min = col.min()
                    print(f"Normalizing column, {i} -- Max: {val_max} -- Min: {val_min}")
                    df[i] = (col - val_min) / (val_max - val_min)
                    columns_maxim[i] = {"max": val_max, "min": val_min}

        # Print the number of entries for each class
        classes = [0, 1, 2, 3] if self.mode == "emuc" else [0, 1, 2]
        for c in classes:
            print(f"Class: {c}\tEntries: {len(df[df['label'] == c])}")

        return df, columns_maxim

class ApplyHeuristics:
    def __init__(self,df):
        self.df=df
    def applyHeuristic(self):
        kpi_columns=self.df.columns[:-1]
        zero_counts=(self.df[kpi_columns]==0).sum(axis=1)
        new_label=3
        self.df.loc[zero_counts>11,'label']=new_label
        return self.df
    def save_csv(df,path="/content/drive/My Drive/6G/CIP_Group_Sanjeev/logs/dataset_analysis.csv"):
        df.to_csv(path,index=False)
        print("File saved at",path)
