from sklearn import metrics
from sklearn.neural_network import MLPClassifier
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import datetime
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score


def predict_nn(x, y, z, clf):
    clf.fit(x, y)
    predicted = clf.predict(z)
    return predicted


if __name__ == "__main__":

    startTime = datetime.datetime.now()

    #Load training data
    x = np.load('data/train_encoded_array_new.npy')
    x[np.where(x == 0)] = 0.001
    y = np.load('data/train_target_array_new.npy')
    y = y.astype('int')
    y = y.flatten()

    #Load test data
    z = np.load('data/test_encoded_array_new.npy')
    z[np.where(z == 0)] = 0.001
    t = np.load('data/test_target_array_new.npy')
    t = t.astype('int')
    t = t.flatten()

    # Dimensionality reduction to 200 dimensions using PCA
    pca = PCA(n_components=500).fit(x)
    x_500d = pca.transform(x)
    z_500d = pca.transform(z)

    learningRate = [0.001]
    for lr in learningRate:
        clf = MLPClassifier(solver='sgd', hidden_layer_sizes=(40, 20), batch_size='auto', learning_rate='adaptive',
                            learning_rate_init=lr, early_stopping=True)
        clf.fit(x_500d, y)
        p = clf.predict(z_500d)

        print("For learning rate: ", lr)
        print("Neural Network with 500 features")

        # Compute accuracy
        accuracy = metrics.accuracy_score(t, p, normalize=False)
        print("Classified %s correctly", accuracy)
        print("Accuracy: ", (accuracy / len(t)) * 100)

        # Confusion matrix
        confusion_matrix = metrics.confusion_matrix(t, p)
        print("Confusion Matrix:\n", confusion_matrix)

        # Replace 4s with 1s
        t[np.where(t == 4)] = 1
        p[np.where(p == 4)] = 1

        y_scores = clf.predict_proba(z)

        # Plot the Precision-Recall curve
        precision, recall, _ = precision_recall_curve(t, y_scores[:, 1])
        plt.figure()
        plt.step(recall, precision, color='b', alpha=0.2, where='post')
        plt.fill_between(recall, precision, step='post', alpha=0.2, color='b')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.ylim([0.0, 1.05])
        plt.xlim([0.0, 1.0])
        average_precision = average_precision_score(t, p)
        plt.title('Neural Network 500d Precision-Recall curve: AP={0:0.2f}'.format(average_precision))
        filename = "data/neuralnetwork_500d_" + str(lr) + "_precisionRecall.png"
        plt.savefig(filename)

    endTime = datetime.datetime.now() - startTime
    print("Total time taken to train: ", endTime)