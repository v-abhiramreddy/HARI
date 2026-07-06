# ML Classifier â€” Evaluation Report

**Generated:** 2026-07-06 09:37

## Data Integrity

### Train/Test Leakage Check
Overlap (exact `body_text` match between train and test splits): **279 rows**

âš ï¸ WARNING: 279 rows overlap between train and test sets. Metrics may be inflated.

### Real vs Synthetic Data in Test Set
| Data Type | Rows | RF Accuracy |
|---|---|---|
| Real | 300 | 0.9400 |
| Synthetic | 300 | 1.0000 |

## Cross-Validation Results (Training Set)

| Model | CV Accuracy (mean) | CV Std | Train Acc | Test Acc |
|---|---|---|---|---|
| **RandomForest** | 0.9800 | 0.0075 | 1.0000 | 0.9700 |
| **LogisticRegression** | 0.9646 | 0.0056 | 0.9696 | 0.9617 |

## Overall Accuracy Comparison

| Model | Test Accuracy |
|---|---|
| **RandomForest (ML)** | 0.9700 |
| **LogisticRegression (Baseline)** | 0.9617 |
| **Rule Engine (scoring_agent)** | 0.4117 |

## Per-Class Metrics: RandomForest

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **phishing** | 1.0000 | 1.0000 | 1.0000 | 150 |
| **safe** | 0.9459 | 0.9333 | 0.9396 | 150 |
| **scam** | 1.0000 | 1.0000 | 1.0000 | 150 |
| **spam** | 0.9342 | 0.9467 | 0.9404 | 150 |
| **weighted avg** | 0.9700 | 0.9700 | 0.9700 | 600 |

### Confusion Matrix (RandomForest)

| Actual \ Predicted | phishing | safe | scam | spam |
|---|---|---|---|---|
| **phishing** | 150 | 0 | 0 | 0 |
| **safe** | 0 | 140 | 0 | 10 |
| **scam** | 0 | 0 | 150 | 0 |
| **spam** | 0 | 8 | 0 | 142 |

## Per-Class Metrics: LogisticRegression

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **phishing** | 1.0000 | 1.0000 | 1.0000 | 150 |
| **safe** | 0.9097 | 0.9400 | 0.9246 | 150 |
| **scam** | 1.0000 | 1.0000 | 1.0000 | 150 |
| **spam** | 0.9379 | 0.9067 | 0.9220 | 150 |
| **weighted avg** | 0.9619 | 0.9617 | 0.9617 | 600 |

### Confusion Matrix (LogisticRegression)

| Actual \ Predicted | phishing | safe | scam | spam |
|---|---|---|---|---|
| **phishing** | 150 | 0 | 0 | 0 |
| **safe** | 0 | 141 | 0 | 9 |
| **scam** | 0 | 0 | 150 | 0 |
| **spam** | 0 | 14 | 0 | 136 |

## Per-Class Metrics: Rule Engine

| Class | Precision | Recall | F1-Score | Support |
|---|---|---|---|---|
| **phishing** | 0.0000 | 0.0000 | 0.0000 | 150 |
| **safe** | 0.3840 | 0.9933 | 0.5539 | 150 |
| **scam** | 0.9800 | 0.6533 | 0.7840 | 150 |
| **spam** | 0.0000 | 0.0000 | 0.0000 | 150 |
| **weighted avg** | 0.3410 | 0.4117 | 0.3345 | 600 |

### Confusion Matrix (Rule Engine)

| Actual \ Predicted | phishing | safe | scam | spam |
|---|---|---|---|---|
| **phishing** | 0 | 39 | 0 | 111 |
| **safe** | 0 | 149 | 0 | 1 |
| **scam** | 0 | 52 | 98 | 0 |
| **spam** | 0 | 148 | 2 | 0 |

## Where ML Underperforms the Rule Engine

The ML model matches or exceeds the rule engine on all categories.

## Known-Hard-Case Sanity Test

These are the exact emails that historically caused false positives in the rule engine
(KITSW mailing-list, Unstop event platform, Sreenidhi college).

| Email | Expected | ML Predicted | Rule Engine | ML Correct? | Rule Correct? |
|---|---|---|---|---|---|
| KITSW mailing-list forwarded email | safe | spam | safe (score=0) | âŒ | âœ… |
| Unstop event platform email | safe | spam | safe (score=0) | âŒ | âœ… |
| Sreenidhi college email | safe | spam | safe (score=0) | âŒ | âœ… |

## Methodology Notes

- **Train/test split:** 80/20, stratified by class
- **Cross-validation:** 5-fold stratified on training set
- **RandomForest:** n_estimators=200, max_depth=5, learning_rate=0.1
- **LogisticRegression:** max_iter=1000, multinomial, lbfgs solver
- **Features:** TF-IDF (max_features=5000, bigrams) + 9 structural features
- **Rule engine comparison:** score_email() called with no auth headers (spf/dkim/dmarc=none)
  since the dataset rows don't have real authentication headers
