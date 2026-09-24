# Analytics pipeline

Run `python analysis.py` after installing `requirements.txt`. It loads Titanic once via Seaborn, saves the raw CSV fallback immediately, then produces [analysis_report.md](analysis_report.md), `figures/`, and `best_pipeline.joblib`. The report contains exact missing percentages, IQR outlier counts, descriptive statistics, model comparisons, classifier and regression metrics, and the final recommendation. Modeling preprocessing is fitted only on each training split.


Recorded run: stratified test accuracy was 0.809 for Logistic Regression, 0.764 for Decision Tree, and 0.803 for Random Forest. Logistic Regression led by F1 (0.734) and AUC (0.861) and is the report's recommended classifier. Fare regression recorded MAE 16.692, RMSE 39.121, R-squared 0.426, adjusted R-squared 0.295.

## Chart interpretations

- [Correlation heatmap](figures/correlation_heatmap.png): Passenger class and fare have the strongest negative correlation (`r = -0.548`), while sibling/spouse and parent/child counts have a moderate positive correlation (`r = 0.415`). These associations describe this dataset and do not establish causation.
- [ROC curves](figures/roc_curves.png): Logistic Regression has the highest held-out AUC (`0.861`), followed by Decision Tree (`0.837`) and Random Forest (`0.824`). This supports Logistic Regression as the strongest rank-ordering classifier among the three tested models.
- [Fare residuals](figures/fare_residuals.png): Residuals show changing spread and banding across predicted fares rather than a uniform cloud. This suggests heteroscedasticity, so fare predictions are less reliable in some fare ranges.
- [Decision tree](figures/decision_tree.png): The plotted tree makes its classification path interpretable as a sequence of feature splits. Its held-out accuracy (`0.764`) and F1 (`0.644`) are lower than Logistic Regression's, so this tree is useful for explanation but is not the selected model.
