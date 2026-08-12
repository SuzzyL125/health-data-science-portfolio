# Predicting Parkinson's disease from voice signals

Graduate machine-learning case study comparing classification algorithms for Parkinson's disease screening using high-dimensional acoustic features.

## Problem

Voice changes are common in Parkinson's disease and may support low-burden screening or monitoring. The project asked which classification method best separated participants with Parkinson's disease from healthy participants using features extracted from voice recordings.

This is a coursework analysis and is **not** a clinically validated diagnostic model.

## Data

- 252 participants: Parkinson's disease and healthy controls
- Three voice recordings per participant
- 753 acoustic predictors across baseline, time-frequency, MFCC, wavelet, vocal-fold, and TQWT feature families
- Course-provided split: 176 participants for training and 76 for testing

The original training feature table is not included because its redistribution terms were not documented. See [data/README.md](data/README.md).

## Methods compared

- Logistic regression
- Quadratic discriminant analysis
- LASSO logistic regression
- Naive Bayes
- Radial support vector machine
- Classification tree
- K-nearest neighbors
- Neural network
- Random forest after feature selection

Boruta feature selection reduced 753 predictors to 154 confirmed features. Model performance was examined with repeated 10-fold cross-validation using accuracy, Cohen's kappa, sensitivity, specificity, ROC-AUC, and precision-recall curves. Participant-level aggregation was explored to address repeated recordings.

## Main coursework findings

- Radial SVM produced the strongest reported combination of training accuracy (0.915) and ROC-AUC (0.960) among the primary comparisons.
- LASSO achieved ROC-AUC 0.925 and provided a regularized parametric benchmark.
- After Boruta selection, radial SVM accuracy increased to 0.926.
- A random forest fit to participant-aggregated data reached 0.994 training accuracy, a warning sign for overfitting rather than evidence of near-perfect clinical performance.
- On the 76-person test set, the selected SVM produced consistent Parkinson's predictions for 50 participants, consistent healthy predictions for 7, and conflicting classifications across repeated recordings for 19.

## What I contributed

This was a collaborative project. My coursework file focused on Boruta feature selection and comparison of logistic regression, LASSO, KNN, random forest, classification tree, radial SVM, neural networks, and participant-level aggregation. The public modeling report is anonymized for portfolio presentation.

## Files

- `analysis/portfolio-analysis.R`: cleaned, portable analysis outline
- `analysis/original-analysis.Rmd`: original submitted coursework analysis
- `results/model-predictions.csv`: cleaned course test predictions
- [`reports/modeling-report.md`](reports/modeling-report.md): public, privacy-cleaned report with narrative and result tables
- `slides/final-team-presentation.pptx`: original team presentation

## Methodological lessons

The project demonstrates broad model comparison, but it also highlights important design issues for healthcare ML:

1. Repeated recordings from one participant are correlated. Cross-validation should split by participant, not by recording, to prevent leakage.
2. Feature selection must be performed inside each resampling fold; selecting features once before cross-validation can inflate performance.
3. A screening model needs calibration, confidence intervals, decision thresholds, and external validation—not only ROC-AUC.
4. Class imbalance makes accuracy insufficient; sensitivity, specificity, precision-recall, and clinical utility should be reported.
5. Highly flexible models require careful tuning and independent evaluation when predictors greatly outnumber participants.

These caveats are central to how I would redesign the analysis for research or production use.
