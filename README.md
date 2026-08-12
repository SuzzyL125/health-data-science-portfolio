# Health Data Science Portfolio

Applied machine learning, statistical computing, and scalable data-processing work focused on health research.

This repository brings together two graduate-coursework projects and presents them as concise case studies for healthcare data science and real-world evidence roles. The emphasis is on the decisions behind the analysis: high-dimensional modeling, repeated measurements, model evaluation, computational tradeoffs, and reproducible implementation.

## Portfolio projects

| Project | What it demonstrates | Tools |
|---|---|---|
| [Parkinson's disease classification from voice signals](machine-learning-parkinsons/) | High-dimensional binary classification, feature selection, cross-validation, ROC-AUC evaluation, repeated-measures considerations, clinical interpretation | R, caret, Boruta, glmnet, random forest, SVM, KNN |
| [Data science computing](data-science-computing/) | Algorithm analysis, benchmarking, dynamic programming, concurrency, external sorting, multiprocessing, and GPU-computing concepts | Python, NumPy, threading, multiprocessing, PyOpenCL |

## Why these projects matter for health data science

My broader research background includes epidemiology, causal inference, longitudinal and survival analysis, SEER-Medicare data, Epic EHR review, REDCap, SQL-based validation, and regulated clinical programming. These coursework projects add evidence of predictive modeling and computing fundamentals:

- comparing multiple models rather than reporting a single preferred method;
- evaluating discrimination, sensitivity, specificity, accuracy, and overfitting risk;
- recognizing patient-level clustering and repeated-measure structure;
- choosing computational strategies based on workload and resource constraints;
- communicating technical results in a clinical context.

## Repository scope and attribution

The Parkinson's project was completed as a team project. The original report and presentation retain the full contributor list. The analysis file included here is Zhuoyun Li's coursework file. The computing examples are adapted from Zhuoyun Li's submitted coursework and have been reorganized for readability and portability.

Course slides, instructor solutions, exams, and other teaching materials are intentionally excluded. The original Parkinson's training data are also excluded because redistribution terms were not documented in the course folder.

## Reproducibility notes

The original work is preserved under clearly labeled filenames. Portfolio-ready scripts remove machine-specific paths and make parameters explicit. The Parkinson's analysis cannot be rerun without the original feature dataset; see its [data note](machine-learning-parkinsons/data/README.md). Results are reported as coursework findings, not as a validated clinical diagnostic tool.

## Target roles

This portfolio is designed for Healthcare Data Scientist, Population Health Data Scientist, Real-World Evidence Data Scientist, Clinical Data Scientist, and Epidemiologist-Data Scientist opportunities. See [job-market alignment](docs/job-market-alignment.md).

## Contact

Zhuoyun Li  
GitHub: [SuzzyL125](https://github.com/SuzzyL125)
