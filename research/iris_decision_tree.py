import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from sklearn.tree import DecisionTreeClassifier
from sklearn import tree
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report


iris_data_df = pd.read_csv("./Iris.csv")

print(iris_data_df)

# perform data cldeeaning
print(iris_data_df.isna().sum()) # none all fields are not empty

# check shape, info() and value_counts
print(f"Iris data set is of shape : {iris_data_df.shape}")
print(f"Iris data set info is : \n {iris_data_df.info()}")

#check on species to know
print(f"Iris data has the following species : {iris_data_df["Species"].value_counts()}")


# exploratory data analysis
iris_setosa_df = iris_data_df[iris_data_df["Species"] == "Iris-setosa"] 
iris_virginica_df = iris_data_df[iris_data_df["Species"] == "Iris-versicolor"]
iris_versicolor_df = iris_data_df[iris_data_df["Species"] == "Iris-virginica"]


print(f"The iris_setosa_df : \n {iris_setosa_df}")
print("\n")
print(f"The iris_versicolor_df : \n {iris_versicolor_df}")
print("\n")
print(f"The iris_virginica_df : \n {iris_virginica_df}")


# getting some data from the SepalLengthCm SepalWidthCm PetalLengthCm  PetalWidthCm
# iris  setosa
iris_setosa_sepalLenghtCm_max = iris_setosa_df["SepalLengthCm"].max()
iris_setosa_SepalWidthCm_max = iris_setosa_df["SepalWidthCm"].max()
iris_setosa_PetalLengthCm_max = iris_setosa_df["PetalLengthCm"].max()
iris_setosa_PetalWidthCm_max = iris_setosa_df["PetalWidthCm"].max()
iris_setosa_sepalLenghtCm_min= iris_setosa_df["SepalLengthCm"].min()
iris_setosa_SepalWidthCm_min = iris_setosa_df["SepalWidthCm"].min()
iris_setosa_PetalLengthCm_min = iris_setosa_df["PetalLengthCm"].min()
iris_setosa_PetalWidthCm_min = iris_setosa_df["PetalWidthCm"].min()

# iris_versicolor
iris_versicolor_SepalLengthCm_max = iris_versicolor_df["SepalLengthCm"].max()
iris_versicolor_SepalWidthCm_max = iris_versicolor_df["SepalWidthCm"].max()
iris_versicolor_PetalLengthCm_max = iris_versicolor_df["PetalLengthCm"].max()
iris_versicolor_PetalWidthCm_max = iris_versicolor_df["PetalWidthCm"].max()
iris_versicolor_sepalLenghtCm_min= iris_versicolor_df["SepalLengthCm"].min()
iris_versicolor_SepalWidthCm_min = iris_versicolor_df["SepalWidthCm"].min()
iris_versicolor_PetalLengthCm_min = iris_versicolor_df["PetalLengthCm"].min()
iris_versicolor_PetalWidthCm_min = iris_versicolor_df["PetalWidthCm"].min()

# iris_virginica
iris_virginica_sepalLenghtCm_max = iris_virginica_df["SepalLengthCm"].max()
iris_virginica_SepalWidthCm_max = iris_virginica_df["SepalWidthCm"].max()
iris_virginica_PetalLengthCm_max = iris_virginica_df["PetalLengthCm"].max()
iris_virginica_PetalWidthCm_max = iris_virginica_df["PetalWidthCm"].max()
iris_virginica_sepalLenghtCm_min = iris_virginica_df["SepalLengthCm"].min()
iris_virginica_SepalWidthCm_min = iris_virginica_df["SepalWidthCm"].min()
iris_virginica_PetalLengthCm_min = iris_virginica_df["PetalLengthCm"].min()
iris_virginica_PetalWidthCm_min = iris_virginica_df["PetalWidthCm"].min()

print(f"""For Iris-setosa has the following characterstics: \n
    Iris-setosa SepalLengthCm_man : {iris_setosa_sepalLenghtCm_max} \n
    iris_setosa_SepalWidthCm_max  : {iris_setosa_SepalWidthCm_max } \n
    iris_setosa_PetalLengthCm_max : {iris_setosa_PetalLengthCm_max} \n
    iris_setosa_PetalWidthCm_max : {iris_setosa_PetalWidthCm_max} \n
    iris_setosa_sepalLenghtCm_min : {iris_setosa_sepalLenghtCm_min} \n
    iris_setosa_SepalWidthCm_min  : {iris_setosa_SepalWidthCm_min } \n
    iris_setosa_PetalLengthCm_min : {iris_setosa_PetalLengthCm_min} \n
    iris_setosa_PetalWidthCm_min : {iris_setosa_PetalWidthCm_min}
    """)

print(f"""For virginica has the following characterstics: \n
    iris_virginica_sepalLenghtCm_max : {iris_virginica_sepalLenghtCm_max} \n
    iris_virginica_SepalWidthCm_max  : {iris_virginica_SepalWidthCm_max } \n
    iris_virginica_PetalLengthCm_max : {iris_virginica_PetalLengthCm_max} \n
    iris_virginica_PetalWidthCm_max : {iris_virginica_PetalWidthCm_max} \n
    iris_virginica_sepalLenghtCm_min : {iris_virginica_sepalLenghtCm_min} \n
    iris_virginica_SepalWidthCm_min  : {iris_virginica_SepalWidthCm_min } \n
    iris_virginica_PetalLengthCm_min : {iris_virginica_PetalLengthCm_min} \n
    iris_virginica_PetalWidthCm_min : {iris_virginica_PetalWidthCm_min} 
    """)

print(f"""For Iris-versicolor has the following characterstics: \n
    iris_versicolor_SepalLengthCm_man : {iris_versicolor_SepalLengthCm_max}\n
    iris_versicolor_SepalWidthCm_max  : {iris_versicolor_SepalWidthCm_max }\n
    iris_versicolor_PetalLengthCm_max : {iris_versicolor_PetalLengthCm_max}\n
    iris_versicolor_PetalWidthCm_max :  {iris_versicolor_PetalWidthCm_max }\n
    iris_versicolor_sepalLenghtCm_min : {iris_versicolor_sepalLenghtCm_min}\n
    iris_versicolor_SepalWidthCm_min  : {iris_versicolor_SepalWidthCm_min }\n
    iris_versicolor_PetalLengthCm_min : {iris_versicolor_PetalLengthCm_min}\n
    iris_versicolor_PetalWidthCm_min :  {iris_versicolor_PetalWidthCm_min }
    """)
# Not performing outlier detection

# Get feature and targets
# x == dependent , SepalLengthCm,  , ,  
features = ["SepalLengthCm", "SepalWidthCm", "PetalLengthCm", "PetalWidthCm"]
X_dependent_df = iris_data_df[features]
Y_target = iris_data_df["Species"]


print(f"Print the first 10 lines of the features data set : \n {X_dependent_df.head(10)}")
print(f"Print the first 10 lines of the target data set : \n {Y_target.head(10)}")

# split the data
X_train,X_test, Y_train, Y_test = train_test_split(X_dependent_df,Y_target, test_size=0.3, random_state=1)


dtree = DecisionTreeClassifier()
iris_tree = dtree.fit(X_train,Y_train)
plt.switch_backend('TkAgg')
tree.plot_tree(dtree, feature_names=features, filled=True)
plt.show()

# perform testing
y_test_pred_results = iris_tree.predict(X_test)
print(f"Accuracy of Decision Tree-Test : {accuracy_score(y_test_pred_results, Y_test)}")

print(classification_report(y_test_pred_results, Y_test))


