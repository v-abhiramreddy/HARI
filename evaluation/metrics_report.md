# Email Scorer Performance Evaluation Report

This report evaluates the scoring agent's accuracy and performance on a combined dataset of mock student emails and real-world phishing samples.

## Binary Classification Metrics
- **Positive Class**: Phishing or Scam (High risk)
- **Negative Class**: Safe or Spam (Low risk / Benign)

| Metric | Value | Details |
| :--- | :--- | :--- |
| **Total Emails Evaluated** | 38 | Combined mock-data datasets |
| **True Positives (TP)** | 28 | Phishing/scam correctly flagged |
| **True Negatives (TN)** | 10 | Safe/spam correctly identified as low risk |
| **False Positives (FP)** | 0 | Benign emails incorrectly flagged as phishing/scam |
| **False Negatives (FN)** | 0 | Phishing/scam missed by the filter |
| **Accuracy** | 100.00% | (38/38) |
| **Precision** | 100.00% | (28/28) |
| **Recall** | 100.00% | (28/28) |
| **F1 Score** | 100.00% | Harmonic mean of precision & recall |

## Detailed Category Breakdown
This table shows how individual ground truth categories were classified by the scorer.

| Ground Truth \ Predicted | Phishing | Scam | Spam | Safe |
| :--- | :---: | :---: | :---: | :---: |
| **phishing** | 21 | 2 | 0 | 0 |
| **borderline_phishing** | 5 | 0 | 0 | 0 |
| **safe** | 0 | 0 | 0 | 10 |

## Performance Interpretation

**Strengths**: The scorer performs well at:
- correctly identifying unambiguous phishing attempts (TP = 28), successfully catching emails with clear threat signals (lookalike domains, SPF/DKIM/DMARC failures, and high-urgency language combined with credential requests).
- correctly classifying legitimate university communications as safe (TN = 10), ensuring standard institutional mail is ignored by the filter.
- avoiding false alarms entirely (FP = 0), which guarantees that safe emails do not trigger warnings for users.
- capturing all dangerous emails (FN = 0) without letting threats leak into the inbox.

**Weaknesses**: No significant weaknesses were observed under the current test dataset (all threats detected, and no false alarms generated).

## Incorrectly Classified Examples

No incorrect predictions were found in this evaluation!
