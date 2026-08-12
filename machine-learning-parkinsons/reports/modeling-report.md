# Predicting Parkinson's Disease from Voice Signals

## Executive summary

This project evaluated whether acoustic features extracted from voice recordings could distinguish people with Parkinson's disease from healthy controls. Multiple statistical and machine-learning classifiers were compared using cross-validation, discrimination metrics, and test-set predictions.

Among the primary model comparisons, a radial support vector machine (SVM) produced the strongest reported combination of training accuracy and ROC-AUC. The analysis also showed why high performance must be interpreted cautiously: the dataset contained far more predictors than participants, included repeated recordings from the same participant, and created substantial risk of overfitting and data leakage.

> **Portfolio context:** This is a retrospective coursework case study, not a clinically validated diagnostic model. Names, course identifiers, instructors, and institutional assessment details have been removed for public presentation.

## Research question

Can machine-learning algorithms use high-dimensional voice measurements to classify participants as having Parkinson's disease or being healthy controls?

Voice-based models may offer a low-burden way to support screening or monitoring. They are especially relevant to telehealth settings, but any clinical application would require participant-level validation, calibration, threshold selection, and evaluation in an independent population.

## Dataset overview

| Item | Description |
|---|---|
| Study population | 252 participants with Parkinson's disease or healthy control status |
| Repeated measurements | Three voice recordings per participant |
| Training set | 176 participants; 528 recordings |
| Test set | 76 participants; 228 recordings |
| Outcome | Binary classification: Parkinson's disease vs. healthy control |
| Candidate predictors | 753 acoustic features |
| Feature-selection result | 154 features confirmed by Boruta |

The original feature dataset is not distributed in this repository because its redistribution terms were not documented. The public repository contains only the analysis code, a de-identified prediction output, and this summarized report.

## Predictor families

| Feature family | Examples or dimensions |
|---|---|
| Baseline acoustic measures | Jitter, shimmer, fundamental-frequency parameters, harmonicity, RPDE, DFA, and PPE |
| Time-frequency measures | Intensity, bandwidth, and formant-frequency measures |
| Mel-frequency cepstral coefficients | 84 MFCC features |
| Wavelet-transform measures | 182 features |
| Vocal-fold measures | Glottis quotient, GNE, VFER, and empirical mode decomposition measures |
| Tunable Q-factor wavelet transform | 432 TQWT features |

## Analytical approach

The original analysis used repeated 10-fold cross-validation and the R `caret` framework to tune and compare several classifiers. Performance was summarized with accuracy, Cohen's kappa, sensitivity, specificity, ROC-AUC, and precision-recall curves.

Models considered included:

- multiple logistic regression;
- quadratic discriminant analysis;
- LASSO logistic regression;
- naive Bayes;
- radial SVM;
- classification tree;
- K-nearest neighbors;
- neural network;
- random forest after feature selection.

Boruta was used to reduce the feature space from 753 candidate predictors to 154 confirmed features. Participant-level aggregation was also explored as one way to address the correlation among repeated recordings.

## Primary model comparison

The table below reports the metrics documented in the original analysis. A dash indicates that a metric was not reported in the source narrative.

| Model | Tuning detail | Accuracy | Cohen's kappa | ROC-AUC | Sensitivity | Specificity |
|---|---:|---:|---:|---:|---:|---:|
| Multiple logistic regression | — | 0.497 | 0.022 | 0.526 | — | — |
| LASSO logistic regression | alpha = 1 | 0.883 | 0.660 | 0.925 | — | — |
| Quadratic discriminant analysis | Feature-selected fit | — | — | 0.905 | — | — |
| Classification tree | Tuned complexity parameter | 0.836 | 0.576 | 0.832 | 0.659 | 0.885 |
| K-nearest neighbors | k = 5 | 0.873 | 0.609 | — | — | — |
| Radial SVM | Tuned cost | **0.915** | **0.766** | **0.960** | — | — |

The radial SVM was selected for test-set prediction because it produced the strongest reported accuracy and ROC-AUC across the main comparisons. LASSO provided a useful regularized benchmark and substantially outperformed unregularized logistic regression in this high-dimensional setting.

## Feature selection and repeated-measure analyses

| Analysis | Accuracy | Cohen's kappa | Interpretation |
|---|---:|---:|---|
| Logistic regression after Boruta | 0.822 | 0.552 | Improved after dimensionality reduction, but remained below the nonlinear models |
| Radial SVM after Boruta | 0.926 | 0.800 | Best reported result after feature selection |
| Participant-aggregated radial SVM | 0.897 | 0.715 | Explicitly incorporated participant-level aggregation |
| Participant-aggregated random forest | 0.994 | 0.982 | Implausibly high training performance and a strong warning for overfitting |

The random-forest result should not be described as near-perfect clinical prediction. With a small number of participants and many candidate predictors, extremely high training performance is more consistent with model flexibility and optimistic validation than with reliable generalization.

## Test-set predictions

The selected SVM generated three predictions per participant because each participant had three recordings. Participant-level summaries were based on agreement across those repeated predictions.

| Participant-level result | Participants | Percentage |
|---|---:|---:|
| Consistently predicted Parkinson's disease | 50 | 65.8% |
| Consistently predicted healthy | 7 | 9.2% |
| Conflicting predictions across recordings | 19 | 25.0% |
| **Total** | **76** | **100.0%** |

The conflicting classifications are analytically important. They suggest that measurement variability and participant-level correlation must be handled directly rather than treating each recording as an independent observation.

## Interpretation

The coursework findings suggest that nonlinear classifiers—particularly radial SVM—were better suited than ordinary logistic regression for these high-dimensional voice features. Feature selection improved several models and reduced computational burden. However, the study should be viewed as a model-development exercise rather than evidence that the classifier is ready for clinical use.

The most important result is not simply that one algorithm achieved the largest ROC-AUC. The project demonstrates how model choice, dimensionality, correlated observations, class imbalance, and validation design can materially change apparent performance.

## Limitations and improved validation plan

### Limitations of the original workflow

1. **Repeated recordings:** Recordings from one participant are correlated. If recordings from the same person enter both training and validation folds, estimated performance may be optimistic.
2. **Feature-selection leakage:** Selecting variables before cross-validation allows information from validation observations to influence the model-development process.
3. **High dimensionality:** There were 753 predictors but only 176 training participants, increasing instability, collinearity, and overfitting risk.
4. **Class imbalance:** Accuracy alone can hide weak detection of the less common class.
5. **Incomplete participant-level test labels:** The available prediction file does not contain the reference outcome required to compute independent test accuracy, ROC-AUC, calibration, or confidence intervals.
6. **No external validation:** The model was not evaluated in a separate clinical population or data-collection setting.

### Recommended production-grade redesign

- create resampling folds by participant ID so all recordings from one participant remain together;
- nest feature selection and hyperparameter tuning inside the resampling procedure;
- preserve a truly untouched test cohort;
- report confidence intervals, calibration, precision-recall, and threshold-specific sensitivity and specificity;
- assess performance by relevant demographic and clinical subgroups;
- compare recording-level and participant-level models explicitly;
- perform external validation before making clinical claims;
- document preprocessing, random seeds, package versions, and data provenance.

## Skills demonstrated

| Area | Evidence in this project |
|---|---|
| Machine learning | Comparative classification using regularized linear and nonlinear models |
| Feature engineering | Review of multiple acoustic-feature families and Boruta selection |
| Model evaluation | Cross-validation, ROC-AUC, precision-recall, accuracy, kappa, sensitivity, and specificity |
| Longitudinal thinking | Identification of repeated recordings and participant-level dependence |
| Clinical interpretation | Translation of model performance into screening implications and validation requirements |
| Reproducibility | Version-controlled R analysis, explicit data-availability note, and documented limitations |

## Repository resources

- [Portfolio-ready analysis outline](../analysis/portfolio-analysis.R)
- [Original analysis code](../analysis/original-analysis.Rmd)
- [De-identified prediction output](../results/model-predictions.csv)
- [Data availability and expected schema](../data/README.md)

## Conclusion

Radial SVM was the strongest classifier in the original model comparison, with reported training accuracy of 0.915 and ROC-AUC of 0.960. More importantly, the project illustrates the need to align machine-learning validation with the structure of health data. Participant-level splitting, nested feature selection, calibration, and external validation would be essential before using a voice-based classifier for clinical screening or decision support.
