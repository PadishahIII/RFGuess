from unittest import TestCase


class TestPIIRFTrainner(TestCase):
    def test__classify(self):
        self.fail()

    def test__classify_proba(self):
        from sklearn.ensemble import RandomForestClassifier
        import numpy as np

        # Generate sample data
        X = np.array([[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]])
        y = np.array([0, 1, 2, 1])  # Class labels

        # Create a Random Forest classifier
        clf = RandomForestClassifier()
        clf.fit(X, y)

        # Define a new feature vector to classify
        new_sample = np.array([[3, 4, 5]])

        # Get the predicted class probabilities for the new sample
        proba = clf.predict_proba(new_sample)

        # Get the predicted classes
        predicted_classes = clf.predict(new_sample)

        # Print the results
        print("Predicted Class Probabilities:")
        for class_label, probability in zip(clf.classes_, proba[0]):
            print(f"Class {class_label}: {probability:.3f}")

        print("Predicted Class:", predicted_classes[0])

        d = zip(clf.classes_,proba[0])
        ds = sorted(d,key=lambda x:x[1],reverse=True)
        for class_label, proba in ds:
            print(f"Class {class_label}: {proba:.3f}")


    def test__train(self):
        self.fail()
