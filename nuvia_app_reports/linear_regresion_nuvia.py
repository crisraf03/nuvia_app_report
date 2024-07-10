# Calculation of the linear regresions

from sklearn.linear_model import LinearRegression
import numpy as np 
import pandas as pd

def determinate_linear_regresion(x, y):
    model = LinearRegression()
    if len(x) == 0:
        print("No hay muestras para ajustar el modelo de regresión.")
        return [None, None, None]

    # Verify if x is an instance of pd.Series and convert to a matriz 2D if it´s needed
    if isinstance(x, pd.Series):
        x = x.values.reshape(-1, 1)
    elif isinstance(x, (int, float)):  # Additional comprobation in case it´s a scalar variable
        x = np.array(x).reshape(-1, 1)

    model.fit(x,y)
    slope = model.coef_[0]
    intercept = model.intercept_
    r_squared = model.score(x, y)
    return [slope , intercept , r_squared]


def calculate_mean_std(dataframe, column):
    # Check if the column exists in the DataFrame
    if column not in dataframe.columns:
        return ["Error: The specified column does not exist in the DataFrame."]

    # Calculate mean and standard deviation
    mean_value = dataframe[column].mean()
    std_value = dataframe[column].std()

    # Create a list with the results
    results = [mean_value , std_value]
    return results