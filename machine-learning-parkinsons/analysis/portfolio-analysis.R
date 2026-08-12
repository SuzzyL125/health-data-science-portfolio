#!/usr/bin/env Rscript

# Portfolio-ready outline adapted from graduate coursework.
# The original training data are not distributed with this repository.

required_packages <- c("caret", "Boruta", "glmnet", "randomForest", "kernlab", "pROC")
missing_packages <- required_packages[!vapply(required_packages, requireNamespace, logical(1), quietly = TRUE)]
if (length(missing_packages) > 0) {
  stop("Install required packages: ", paste(missing_packages, collapse = ", "))
}

set.seed(1976)
data_path <- file.path("data", "parkinsons_voice_features.csv")
if (!file.exists(data_path)) {
  stop("Training data not found. See data/README.md for the expected file and schema.")
}

voice <- read.csv(data_path, check.names = FALSE)
stopifnot(all(c("id", "class") %in% names(voice)))
voice$class <- factor(voice$class, levels = c(0, 1), labels = c("Healthy", "PD"))

# Participant-level folds avoid placing recordings from the same participant
# in both training and validation partitions.
participant_outcome <- aggregate(class ~ id, voice, function(x) names(which.max(table(x))))
participant_outcome$class <- factor(participant_outcome$class, levels = c("Healthy", "PD"))
participant_folds <- caret::createFolds(participant_outcome$class, k = 10, returnTrain = TRUE)
index <- lapply(participant_folds, function(rows) which(voice$id %in% participant_outcome$id[rows]))
index_out <- lapply(index, function(rows) setdiff(seq_len(nrow(voice)), rows))

control <- caret::trainControl(
  method = "cv",
  number = 10,
  index = index,
  indexOut = index_out,
  classProbs = TRUE,
  summaryFunction = caret::twoClassSummary,
  savePredictions = "final"
)

predictors <- setdiff(names(voice), c("id", "class"))

# Important: for unbiased performance estimation, feature selection should be
# nested within resampling. This standalone Boruta fit is retained for feature
# exploration, not final validation.
boruta_fit <- Boruta::Boruta(
  x = voice[predictors],
  y = voice$class,
  maxRuns = 1000,
  doTrace = 1
)
selected <- Boruta::getSelectedAttributes(boruta_fit, withTentative = FALSE)
model_data <- voice[c("class", selected)]

models <- list(
  lasso = caret::train(
    class ~ ., data = model_data, method = "glmnet", metric = "ROC",
    trControl = control,
    tuneGrid = expand.grid(alpha = 1, lambda = 10^seq(-5, 1, length.out = 40))
  ),
  knn = caret::train(
    class ~ ., data = model_data, method = "knn", metric = "ROC",
    preProcess = c("center", "scale"), tuneLength = 15, trControl = control
  ),
  svm_radial = caret::train(
    class ~ ., data = model_data, method = "svmRadial", metric = "ROC",
    preProcess = c("center", "scale"), tuneLength = 15, trControl = control
  ),
  random_forest = caret::train(
    class ~ ., data = model_data, method = "rf", metric = "ROC",
    tuneLength = 8, trControl = control
  )
)

comparison <- do.call(
  rbind,
  lapply(names(models), function(name) {
    best <- models[[name]]$results[which.max(models[[name]]$results$ROC), ]
    data.frame(model = name, ROC = best$ROC, sensitivity = best$Sens, specificity = best$Spec)
  })
)
comparison <- comparison[order(comparison$ROC, decreasing = TRUE), ]
print(comparison, row.names = FALSE)
