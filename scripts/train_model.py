import os
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix,
)


def main():
    df = pd.read_csv("data/processed/clauses_clean.csv")
    X = df["quote_text"].astype(str)
    y = df["label"]

    X_train, X_temp, y_train, y_temp = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=42
    )
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp, test_size=0.50, stratify=y_temp, random_state=42
    )

    X_train_final = pd.concat([X_train, X_val])
    y_train_final = pd.concat([y_train, y_val])

    vectorizer = TfidfVectorizer(
        lowercase=True,
        ngram_range=(1, 2),
        min_df=2,
        max_df=0.95,
        sublinear_tf=True,
    )
    X_train_final_tfidf = vectorizer.fit_transform(X_train_final)
    X_test_tfidf = vectorizer.transform(X_test)

    model = SVC(kernel="rbf", C=10, gamma=0.1, random_state=42)
    model.fit(X_train_final_tfidf, y_train_final)

    y_pred = model.predict(X_test_tfidf)
    print(classification_report(y_test, y_pred))

    os.makedirs("models/selected_model", exist_ok=True)
    joblib.dump(vectorizer, "models/selected_model/vectorizer.joblib")
    joblib.dump(model, "models/selected_model/model.joblib")
    print("Saved model and vectorizer to models/selected_model/")


if __name__ == "__main__":
    main()
