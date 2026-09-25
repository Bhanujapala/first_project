# Module 2 — Titanic Analytics and Machine Learning

## Overview

This module performs exploratory data analysis, preprocessing, classification, class-imbalance analysis, hyperparameter tuning, and regression using the Titanic dataset.

The Titanic dataset was loaded once using Seaborn and saved as `titanic.csv` so that the modeling notebook could use the committed CSV without loading the raw dataset again.

---

## Part A — Exploratory Data Analysis

### Dataset Profile

The original Titanic dataset contains:

- 891 rows
- 15 columns

Missing values were found in:

| Column | Missing Values | Missing % | Handling |
|---|---:|---:|---|
| age | 177 | 19.87% | Median imputation |
| embarked | 2 | 0.22% | Drop rows |
| deck | 688 | 77.22% | Drop column |
| embark_town | 2 | 0.22% | Drop rows |

After cleaning, the dataset contained 889 rows and 14 columns.

### Univariate Analysis

The fare distribution is right-skewed because:

- Mean = 32.0967
- Median = 14.4542
- Mode = 8.0500

IQR analysis identified 65 age outliers and 114 fare outliers.

### Bivariate Analysis

Survival differed substantially by sex and passenger class. Female passengers had a substantially higher survival rate than male passengers in the cleaned dataset. Survival also varied across passenger classes.

The two strongest absolute correlations among the selected numerical variables were:

- `pclass` and `fare`: -0.5482
- `sibsp` and `parch`: 0.4145

### Multivariate Analysis

Four multivariate visualizations were created to examine survival by class and sex, age by survival status, fare by class and survival, and the relationship between age, fare, and survival.

### Standardization

Age and fare were standardized using z-score standardization for exploratory analysis. After standardization, their means were approximately zero and standard deviations were approximately one. This exploratory standardization was not used as the modeling preprocessing.

---

# Part B — Machine Learning

## Train/Test Split

A stratified 80/20 train/test split was used to preserve the target-class proportions in both datasets.

The target distribution was approximately:

- Class 0: 61.62%
- Class 1: 38.38%

---

## Preprocessing

Preprocessing was fitted only on the training data.

### Numerical features

- pclass
- age
- sibsp
- parch
- fare

Median imputation and StandardScaler were applied.

### Categorical features

- sex
- embarked

Most-frequent imputation and one-hot encoding were applied.

The preprocessing and classifier were combined into Scikit-learn pipelines.

---

## Classification Models

The following classifiers were trained on the same train/test split:

1. Logistic Regression
2. Decision Tree
3. Random Forest

A tuned Random Forest was also created using GridSearchCV.

Evaluation included:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC
- Confusion matrices
- ROC curves

---

## Class Imbalance

Three Logistic Regression approaches were compared:

| Method | Precision | Recall | F1 |
|---|---:|---:|---:|
| Baseline | 0.7931 | 0.6667 | 0.7244 |
| Class Weight Balanced | 0.7297 | 0.7826 | 0.7552 |
| SMOTE | 0.7397 | 0.7826 | 0.7606 |

SMOTE achieved the highest F1-score among the three imbalance approaches while maintaining the same recall as the class-weight-balanced model.

---

## Random Forest Hyperparameter Tuning

GridSearchCV was used to tune:

- `n_estimators`
- `max_depth`
- `max_features`

The search used 5-fold cross-validation and optimized F1-score.

The tuned Random Forest achieved:

| Metric | Value |
|---|---:|
| Accuracy | 0.8156 |
| Precision | 0.8750 |
| Recall | 0.6087 |
| F1 | 0.7179 |
| AUC | 0.8431 |
| OOB Score | 0.8272 |

---

## Regression

A multivariate Linear Regression model was used to predict `fare`.

| Metric | Value |
|---|---:|
| MAE | 19.8301 |
| RMSE | 30.7541 |
| R² | 0.3888 |
| Adjusted R² | 0.3711 |

The residual plot showed a changing spread of residuals as predicted fare increased, providing visual evidence of heteroscedasticity.

---

## Final Classification Comparison

The original Random Forest achieved the highest F1-score among the evaluated classifiers at 0.7442. Logistic Regression achieved the highest ROC-AUC at 0.8437. The tuned Random Forest achieved high precision of 0.8750 and an AUC of 0.8431, but its recall and F1-score were lower than those of the original Random Forest.

Based on the combined precision, recall, and F1 results from this test set, the original Random Forest was selected as the deployment classifier.

---

## Saved Model

The complete Random Forest pipeline was saved as:

```text
models/best_titanic_classifier.joblib

analytics/
├── 01_eda.ipynb
├── 02_modeling.ipynb
├── README.md
├── titanic.csv
├── charts/
└── models/
    └── best_titanic_classifier.joblib

    
### Step 2 — Save it

Press:

**Ctrl + S**

### Step 3 — Verify

Run:

```powershell
dir analytics\README.md

