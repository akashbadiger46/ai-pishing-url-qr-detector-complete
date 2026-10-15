"""Train and compare multiple classifiers using a labelled URL CSV.

Default input is synthetic demo data. Its scores are pipeline checks only and
must not be described as real-world phishing detection performance.
For genuine evaluation, provide a suitable public/curated labelled CSV using
--data path/to/file.csv and inspect dataset provenance and licensing yourself.
Required CSV columns: url,label (label 1=phishing, 0=legitimate).
"""
from pathlib import Path
import argparse, json
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, ExtraTreesClassifier
from src.data_utils import load_dataset

BASE = Path(__file__).resolve().parent

def main():
    parser = argparse.ArgumentParser(description="Train and compare URL classifiers.")
    parser.add_argument("--data", default=str(BASE / "data" / "urls_demo.csv"), help="CSV with url,label columns")
    parser.add_argument("--mode", choices=["demo", "external"], default=None,
                        help="Label the run as demo or external data. Defaults based on input path.")
    args = parser.parse_args()
    data_path = Path(args.data)
    X, y = load_dataset(data_path)
    mode = args.mode or ("demo_synthetic" if data_path.resolve() == (BASE / "data" / "urls_demo.csv").resolve() else "external_labelled")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )
    candidates = {
        "Logistic Regression": Pipeline([
            ("scale", StandardScaler()),
            ("classifier", LogisticRegression(max_iter=2000, class_weight="balanced", random_state=42))
        ]),
        "Decision Tree": DecisionTreeClassifier(max_depth=8, class_weight="balanced", random_state=42),
        "Random Forest": RandomForestClassifier(n_estimators=160, max_depth=10, class_weight="balanced", random_state=42),
        "Extra Trees": ExtraTreesClassifier(n_estimators=160, max_depth=10, class_weight="balanced", random_state=42),
    }
    results = []
    fitted = {}
    for name, model in candidates.items():
        model.fit(X_train, y_train)
        prediction = model.predict(X_test)
        result = {
            "model": name,
            "accuracy": round(float(accuracy_score(y_test, prediction)), 4),
            "precision_phishing": round(float(precision_score(y_test, prediction, zero_division=0)), 4),
            "recall_phishing": round(float(recall_score(y_test, prediction, zero_division=0)), 4),
            "f1_phishing": round(float(f1_score(y_test, prediction, zero_division=0)), 4),
            "confusion_matrix_labels_0_1": confusion_matrix(y_test, prediction, labels=[0, 1]).tolist(),
        }
        results.append(result)
        fitted[name] = model
        print(f"{name}: accuracy={result['accuracy']:.3f}, precision={result['precision_phishing']:.3f}, "
              f"recall={result['recall_phishing']:.3f}, f1={result['f1_phishing']:.3f}")
    # Select by phishing-class F1, with recall as a tie-breaker.
    best_result = max(results, key=lambda item: (item["f1_phishing"], item["recall_phishing"]))
    best_name = best_result["model"]
    model_dir = BASE / "model"
    model_dir.mkdir(exist_ok=True)
    bundle = {"model": fitted[best_name], "model_name": best_name, "data_mode": mode,
              "feature_names": list(X.columns)}
    joblib.dump(bundle, model_dir / "url_classifier.joblib")
    report = {
        "data_mode": mode,
        "dataset_file": str(data_path.name),
        "sample_count_after_validation": int(len(X)),
        "train_count": int(len(X_train)),
        "test_count": int(len(X_test)),
        "positive_label": "phishing (1)",
        "metrics_note": ("Synthetic demo data: scores only verify that the training pipeline runs; "
                         "they are not meaningful real-world performance estimates."
                         if mode == "demo_synthetic" else
                         "Results depend on the provided labelled dataset and split; inspect its provenance, representativeness, and possible duplicates."),
        "models": results,
        "selected_model": best_name,
        "selected_model_classification_report": classification_report(
            y_test, fitted[best_name].predict(X_test), labels=[0, 1],
            target_names=["legitimate", "phishing"], zero_division=0, output_dict=True
        ),
    }
    (model_dir / "metrics.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"Selected model: {best_name}")
    print(f"Saved model: {model_dir / 'url_classifier.joblib'}")
    print(f"Saved evaluation: {model_dir / 'metrics.json'}")
    print(f"DATA MODE: {mode}. {report['metrics_note']}")

if __name__ == "__main__":
    main()
