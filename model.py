"""
Hybrid neural network will be trained and tested here.
"""

import get_features
import analysis
import pandas as pd
# import tensorflow as tf 
# from tensorflow import keras

def normalizeNumericalData(data):
    numerical_data_mean = data[["Race Progress", "Tire age", "Driver duration"]].mean()
    data["Race Progress"] -= numerical_data_mean["Race Progress"]
    data["Tire age"] -= numerical_data_mean["Tire age"]
    data["Driver duration"] -= numerical_data_mean["Driver duration"]
    return data

def encode(data):
    return pd.get_dummies(data, columns=["Yellow flag", "Position", "Is close ahead", "Pursuer tire change"])
    # print(encoded_data.astype(float)) # might not need to convert all to float


if __name__ == "__main__":
    ra = analysis.RaceAnalysis()
    features = get_features.Features(ra.data, ra.gtd_positions)
    data = features.makeData()
    # print(data[:, 0])
    data = normalizeNumericalData(data)
    data = encode(data)
    print(data)




