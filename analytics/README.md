# Analytics pipeline

Run `python analysis.py` after installing `requirements.txt`. It loads Titanic once via Seaborn, saves the raw CSV fallback immediately, then produces `analysis_report.md`, `figures/`, and `best_pipeline.joblib`. The report contains missing percentages and decisions, descriptive statistics, visual interpretations, classifier/regressor metrics, and recommendation. Modeling preprocessing is fitted only on each training split.


Recorded run: stratified test accuracy was 0.809 for Logistic Regression, 0.764 for Decision Tree, and 0.803 for Random Forest. Logistic Regression led by F1 (0.734) and AUC (0.861) and is the report's recommended classifier. Fare regression recorded MAE 16.692, RMSE 39.121, R-squared 0.426, adjusted R-squared 0.295.
