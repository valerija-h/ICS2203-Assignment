import csv
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score

# Loop through each line in the csv and store the details as an object.
def openFile(fileName):
    # Open the given file name.
    with open(fileName) as csv_file:
        csv_reader = csv.reader(csv_file)
        X,y = [],[] # Stores the data and labels.
        for i,row in enumerate(csv_reader):
            # Ignore row 1 because it's the column names.
            if i == 0:
                continue
            # For each row extract the Class ID and F1,F2,F3 values.
            temp_classID = int(row[6])
            temp_F1 = float(row[8])
            temp_F2 = float(row[9])
            temp_F3 = float(row[10])
            # Append new entry.
            X.append([temp_F1,temp_F2,temp_F3])
            y.append(temp_classID)
    # Shuffle entries and split them into data (X) and labels (y).
    return X,y

def buildConfusionMatrix(y_true,y_pred):
    print("\nThe confusion matrix is:")
    print(confusion_matrix(y_true,y_pred,labels=[1, 2, 3]))
    # Micro - calculates by counting total true positives, false negatives and false positives.
    print("F1 score:" + str(round(f1_score(y_true,y_pred, average='micro'),4)))

def doKNN(X,y,percent,rand,k,metric):
    # Split the data into training and testing set.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=percent, random_state=rand)
    # Create a KNN classifier with k neighbours and a given metric.
    knn = KNeighborsClassifier(n_neighbors=k, metric=metric)
    # Train the model by passing in our training data to fit our model to the training data.
    knn.fit(X_train, y_train)
    # Make predictions on the test data.
    y_pred = knn.predict(X_test)
    # Build a confusion matrix and displays the F1 score using the predicted and actual labels.
    buildConfusionMatrix(y_test,y_pred)

def runner():
    # Open file and obtain data and labels.
    X,y = openFile("Data.csv")
    # Customizable values for the KNN classifier and splitting percentage.
    percentage = 0.25
    k = 5
    metric = "manhattan"
    # Does KNN 5 times for different training/testing sets by changing the random seed generator.
    for i in range(5):
        doKNN(X, y, percentage, i, k, metric)
runner()