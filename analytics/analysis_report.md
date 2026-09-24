# Titanic analytics results

Raw shape: (891, 15)

Raw df.info():
<class 'pandas.DataFrame'>
RangeIndex: 891 entries, 0 to 890
Data columns (total 15 columns):
 #   Column       Non-Null Count  Dtype   
---  ------       --------------  -----   
 0   survived     891 non-null    int64   
 1   pclass       891 non-null    int64   
 2   sex          891 non-null    str     
 3   age          714 non-null    float64 
 4   sibsp        891 non-null    int64   
 5   parch        891 non-null    int64   
 6   fare         891 non-null    float64 
 7   embarked     889 non-null    str     
 8   class        891 non-null    category
 9   who          891 non-null    str     
 10  adult_male   891 non-null    bool    
 11  deck         203 non-null    category
 12  embark_town  889 non-null    str     
 13  alive        891 non-null    str     
 14  alone        891 non-null    bool    
dtypes: bool(2), category(2), float64(2), int64(4), str(5)
memory usage: 80.7 KB


Raw descriptive summary:
          survived      pclass   sex         age       sibsp       parch        fare embarked  class  who adult_male deck  embark_town alive alone
count   891.000000  891.000000   891  714.000000  891.000000  891.000000  891.000000      889    891  891        891  203          889   891   891
unique         NaN         NaN     2         NaN         NaN         NaN         NaN        3      3    3          2    7            3     2     2
top            NaN         NaN  male         NaN         NaN         NaN         NaN        S  Third  man       True    C  Southampton    no  True
freq           NaN         NaN   577         NaN         NaN         NaN         NaN      644    491  537        537   59          644   549   537
mean      0.383838    2.308642   NaN   29.699118    0.523008    0.381594   32.204208      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
std       0.486592    0.836071   NaN   14.526497    1.102743    0.806057   49.693429      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
min       0.000000    1.000000   NaN    0.420000    0.000000    0.000000    0.000000      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
25%       0.000000    2.000000   NaN   20.125000    0.000000    0.000000    7.910400      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
50%       0.000000    3.000000   NaN   28.000000    0.000000    0.000000   14.454200      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
75%       1.000000    3.000000   NaN   38.000000    1.000000    0.000000   31.000000      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN
max       1.000000    3.000000   NaN   80.000000    8.000000    6.000000  512.329200      NaN    NaN  NaN        NaN  NaN          NaN   NaN   NaN

Raw dataframe info:
survived          int64
pclass            int64
sex                 str
age             float64
sibsp             int64
parch             int64
fare            float64
embarked            str
class          category
who                 str
adult_male         bool
deck           category
embark_town         str
alive               str
alone              bool

Missing percentages:
age            19.865320
embarked        0.224467
deck           77.216611
embark_town     0.224467

Cleaning decisions:
age: 19.87% missing; median/mode imputed (5–30%).
embarked: 0.22% missing; dropped affected rows (<5%).
deck: 77.22% missing; retained as explicit Missing category (>30%; avoids unsupported imputation).
embark_town: 0.22% missing; dropped affected rows (<5%).

Clean shape: (889, 15)

age IQR outlier count: 65 (bounds 2.500, 54.500).

fare IQR outlier count: 114 (bounds -26.761, 65.656).

Fare mean=32.097, median=14.454, mode=8.050; ordering mean > median > mode indicates right skew.

Survival by sex: {'male': 0.18890814558058924, 'female': 0.7403846153846154}

Survival by pclass: {'1': 0.6261682242990654, '2': 0.47282608695652173, '3': 0.24236252545824846}

Survival by sex and pclass (boolean masks): {'male, class 1': 0.36885245901639346, 'male, class 2': 0.1574074074074074, 'male, class 3': 0.13544668587896252, 'female, class 1': 0.967391304347826, 'female, class 2': 0.9210526315789473, 'female, class 3': 0.5}

Two strongest absolute off-diagonal correlations: pclass–fare: r=-0.548 (|r|=0.548); sibsp–parch: r=0.415 (|r|=0.415). Interpret cautiously: association is not causation.

Chart interpretations (multivariate_story.png):
1. Survival bars by sex and class show the strongest separation by sex, with class differences visible within groups; this is consistent with the observed group rates.
2. Age boxplots compare survivor distributions within sex; overlap means age alone does not perfectly separate outcomes.
3. The age–fare scatterplot shows substantial overlap, while higher fares and survivor status appear more common together; this is descriptive, not causal.
4. Survival by embarkation town and class varies across groups; class composition may partly explain port-level differences.

Exploratory age/fare standardization (full cleaned EDA data; not used by model):
Before:
            age       fare
mean  29.315152  32.096681
std   12.984932  49.697504
After:
               age          fare
mean  2.797412e-16  1.358743e-16
std   1.000000e+00  1.000000e+00

Stratified split class balance: train={0: 0.617, 1: 0.383}, test={0: 0.618, 1: 0.382}. Stratification preserves outcome proportions in both folds.

Classifier metrics:
         Classifier  Accuracy  Precision  Recall    F1   AUC     Confusion matrix
Logistic Regression     0.809      0.783   0.691 0.734 0.861 [[97, 13], [21, 47]]
      Decision Tree     0.764      0.760   0.559 0.644 0.837 [[98, 12], [30, 38]]
      Random Forest     0.803      0.762   0.706 0.733 0.824 [[95, 15], [20, 48]]

Outcome balance: {0: 549, 1: 340}
Imbalance comparison:
              Variant  Precision  Recall    F1
             baseline      0.783   0.691 0.734
class_weight=balanced      0.718   0.750 0.734
     SMOTE train fold      0.735   0.735 0.735
Choose using the target metric: class weighting/SMOTE can improve minority recall while reducing precision; the table records the observed trade-off.

Random Forest GridSearchCV best params: {'max_depth': None, 'max_features': 0.8, 'n_estimators': 150}; CV F1=0.761; refit training-split OOB score=0.817.

Fare regression: MAE=16.692, RMSE=39.121, R²=0.426, adjusted R²=0.295. Residual plot: inspect for widening spread/banding; residual variance is not perfectly constant across the prediction range, suggesting heteroscedasticity.

Saved/reloaded complete raw-input pipeline: best by F1 then AUC is Logistic Regression; sample raw prediction=0.

Final separated metric groups (classification vs regression):
                   Model  Accuracy Precision    Recall        F1       AUC        MAE       RMSE        R² Adjusted R²
     Logistic Regression  0.808989  0.783333  0.691176  0.734375  0.860963          —          —         —           —
           Decision Tree  0.764045      0.76  0.558824  0.644068  0.837366          —          —         —           —
           Random Forest  0.803371  0.761905  0.705882  0.732824  0.823663          —          —         —           —
Linear Regression (fare)         —         —         —         —         —  16.692401  39.121473  0.426341    0.294878

Deployment recommendation: Deploy Logistic Regression. It achieved F1=0.734 and AUC=0.861 on the held-out stratified set, balancing threshold performance and ranking ability. Its held-out accuracy was 0.809; use the confusion matrix and class-specific precision/recall to set operational thresholds. Keep monitoring because this is a small teaching dataset and its patterns may not transfer to current customers.
