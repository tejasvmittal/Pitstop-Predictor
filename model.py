"""
Hybrid neural network will be trained and tested here.
"""

import get_data
import analysis
import pandas as pd
import tensorflow as tf 
from tensorflow import keras
from sklearn.utils.class_weight import compute_class_weight
import numpy as np

def normalizeNumericalData(data):
    numerical_data_mean = data[["Race Progress", "Tire age", "Driver duration"]].mean()
    data["Race Progress"] -= numerical_data_mean["Race Progress"]
    data["Tire age"] -= numerical_data_mean["Tire age"]
    data["Driver duration"] -= numerical_data_mean["Driver duration"]
    return data


def encode(data):
    return pd.get_dummies(data, columns=["Yellow flag", "Position", "Is close ahead", "Pursuer tire change"])
    # print(encoded_data.astype(float)) # might not need to convert all to float



def FFNN(data):
    num_classes = 1  # Binary classification, so one output node with sigmoid activation

    # Model architecture
    model = keras.models.Sequential()
    model.add(keras.layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.0005), input_shape=(data.shape[0],)))
    model.add(keras.layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.0005)))
    model.add(keras.layers.Dense(64, activation='relu', kernel_regularizer=tf.keras.regularizers.l2(0.0005)))
    model.add(keras.layers.Dense(num_classes, activation='sigmoid'))  # Sigmoid activation for binary classification

    # Compile the model
    optimizer = tf.keras.optimizers.Nadam()
    model.compile(optimizer=optimizer, loss='binary_crossentropy', metrics=['accuracy'])

    # Assuming 'y_train' is your training labels
    # Compute class weights
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)

    # Convert class weights to a dictionary for passing to the model
    class_weight_dict = {0: class_weights[0], 1: class_weights[1]}

    # Train the model with class weights and specified batch size
    model.fit(X_train, y_train, epochs=10, batch_size=256, class_weight=class_weight_dict)

    # Evaluate the model on the test set
    accuracy = model.evaluate(X_test, y_test)[1]
    print(f"Test Accuracy: {accuracy * 100:.2f}%")



if __name__ == "__main__":
    ra = analysis.RaceAnalysis()
    features = get_data.Features(ra.data, ra.gtd_positions)
    data = features.makeData()
    # print(data[:, 0])
    data = normalizeNumericalData(data)
    data = encode(data)
    print(data)




