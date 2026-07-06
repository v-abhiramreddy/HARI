"""
ml/train_model.py
-----------------
Trains a GradientBoostingClassifier and a LogisticRegression baseline.
Uses 80/20 stratified split + 5-fold CV for sanity checking.
"""

import sys
from pathlib import Path

import numpy as np
import joblib
from scipy.sparse import load_npz
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import LabelEncoder

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
ML_DIR = Path(__file__).resolve().parent
MODELS_DIR = ML_DIR / "models"
RANDOM_STATE = 42
TEST_SIZE = 0.2


def main():
    print("=" * 60)
    print("ML MODEL TRAINING")
    print("=" * 60)

    # --- Load features ---
    X = load_npz(MODELS_DIR / "X_features.npz")
    y = np.load(MODELS_DIR / "y_labels.npy")
    le = joblib.load(MODELS_DIR / "label_encoder.joblib")
    is_synthetic = np.load(MODELS_DIR / "is_synthetic.npy")
    body_texts = joblib.load(MODELS_DIR / "body_texts.joblib")

    print(f"Dataset: {X.shape[0]} rows, {X.shape[1]} features")
    print(f"Classes: {list(le.classes_)}")
    for i, cls in enumerate(le.classes_):
        count = np.sum(y == i)
        print(f"  {cls}: {count}")

    # --- Train/test split (stratified) ---
    X_train, X_test, y_train, y_test, idx_train, idx_test = train_test_split(
        X, y, np.arange(len(y)),
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )
    print(f"\nTrain: {X_train.shape[0]}, Test: {X_test.shape[0]}")

    # Save split indices for evaluation
    np.save(MODELS_DIR / "idx_train.npy", idx_train)
    np.save(MODELS_DIR / "idx_test.npy", idx_test)

    # --- Leakage check ---
    print("\n--- Leakage Check ---")
    train_bodies = set(body_texts[i] for i in idx_train)
    test_bodies = [body_texts[i] for i in idx_test]
    overlap = sum(1 for b in test_bodies if b in train_bodies)
    print(f"  Train/test overlap (exact body_text match): {overlap} rows")
    if overlap > 0:
        print(f"  WARNING: {overlap} rows in test set have exact body_text matches in training set!")
    else:
        print(f"  OK: Zero overlap detected.")
    # Save for report
    np.save(MODELS_DIR / "leakage_overlap_count.npy", np.array([overlap]))

    # --- Model 1: RandomForestClassifier ---
    # (GradientBoosting is too slow on sparse TF-IDF matrices; RandomForest
    #  handles sparse data natively and trains orders of magnitude faster)
    print("\n--- Training RandomForestClassifier ---")
    from sklearn.ensemble import RandomForestClassifier
    rf = RandomForestClassifier(
        n_estimators=200,
        max_depth=None,
        min_samples_split=5,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    # 5-fold CV on training set
    print("  Running 5-fold cross-validation...")
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(rf, X_train, y_train, cv=cv, scoring="accuracy")
    print(f"  CV Accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std():.4f})")
    print(f"  Per-fold: {[f'{s:.4f}' for s in cv_scores]}")

    # Fit on full training set
    print("  Fitting on full training set...")
    rf.fit(X_train, y_train)
    train_acc = rf.score(X_train, y_train)
    test_acc = rf.score(X_test, y_test)
    print(f"  Train accuracy: {train_acc:.4f}")
    print(f"  Test accuracy:  {test_acc:.4f}")

    joblib.dump(rf, MODELS_DIR / "classifier.joblib")
    print(f"  Saved: classifier.joblib")

    # --- Model 2: LogisticRegression baseline ---
    print("\n--- Training LogisticRegression baseline ---")
    lr = LogisticRegression(
        max_iter=1000,
        solver="lbfgs",
        random_state=RANDOM_STATE,
    )

    cv_scores_lr = cross_val_score(lr, X_train, y_train, cv=cv, scoring="accuracy")
    print(f"  CV Accuracy: {cv_scores_lr.mean():.4f} (+/- {cv_scores_lr.std():.4f})")

    lr.fit(X_train, y_train)
    train_acc_lr = lr.score(X_train, y_train)
    test_acc_lr = lr.score(X_test, y_test)
    print(f"  Train accuracy: {train_acc_lr:.4f}")
    print(f"  Test accuracy:  {test_acc_lr:.4f}")

    joblib.dump(lr, MODELS_DIR / "baseline_lr.joblib")
    print(f"  Saved: baseline_lr.joblib")

    # --- Save CV results ---
    joblib.dump({
        "rf_cv_mean": float(cv_scores.mean()),
        "rf_cv_std": float(cv_scores.std()),
        "rf_cv_folds": cv_scores.tolist(),
        "rf_train_acc": float(train_acc),
        "rf_test_acc": float(test_acc),
        "lr_cv_mean": float(cv_scores_lr.mean()),
        "lr_cv_std": float(cv_scores_lr.std()),
        "lr_cv_folds": cv_scores_lr.tolist(),
        "lr_train_acc": float(train_acc_lr),
        "lr_test_acc": float(test_acc_lr),
        "leakage_overlap": int(overlap),
    }, MODELS_DIR / "training_results.joblib")

    print(f"\n{'=' * 60}")
    print("TRAINING COMPLETE")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
