"""One-load Titanic EDA and leakage-safe classification/regression workflow."""
from pathlib import Path
import os
import io
from contextlib import redirect_stdout
import warnings
import joblib
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression, LinearRegression
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, roc_auc_score, roc_curve, mean_absolute_error, mean_squared_error, r2_score)
from imblearn.over_sampling import SMOTE

warnings.filterwarnings("ignore")
ROOT = Path(__file__).resolve().parent
FIG = ROOT / "figures"
FIG.mkdir(exist_ok=True)

def savefig(name):
    plt.tight_layout(); plt.savefig(FIG / name, dpi=130); plt.close()

def main():
    # The only network/cache loader call in this module. The raw offline copy is committed.
    os.environ.setdefault("SEABORN_DATA", str(ROOT / "seaborn_cache"))
    df = sns.load_dataset("titanic")
    df.to_csv(ROOT / "titanic.csv", index=False)
    info_buffer=io.StringIO()
    with redirect_stdout(info_buffer): df.info()
    report = [f"Raw shape: {df.shape}", "Raw df.info():\n" + info_buffer.getvalue(), "Raw descriptive summary:\n" + df.describe(include="all").to_string()]
    report += ["Raw dataframe info:\n" + df.dtypes.to_string(), "Missing percentages:\n" + (100*df.isna().mean()).loc[lambda x:x.gt(0)].to_string()]
    # EDA cleaning: <5% drop rows, 5–30% median/mode impute, >30% keep explicit missing category.
    clean = df.copy()
    rates = clean.isna().mean()*100
    strategies=[]
    for col in clean.columns:
        pct=rates[col]
        if pct == 0: continue
        if pct < 5:
            clean=clean.loc[clean[col].notna()].copy(); strategies.append(f"{col}: {pct:.2f}% missing; dropped affected rows (<5%).")
        elif pct <= 30:
            if pd.api.types.is_numeric_dtype(clean[col]): clean[col]=clean[col].fillna(clean[col].median())
            else: clean[col]=clean[col].fillna(clean[col].mode().iloc[0])
            strategies.append(f"{col}: {pct:.2f}% missing; median/mode imputed (5–30%).")
        else:
            if isinstance(clean[col].dtype, pd.CategoricalDtype):
                clean[col] = clean[col].cat.add_categories(["Missing"])
            clean[col]=clean[col].fillna("Missing")
            strategies.append(f"{col}: {pct:.2f}% missing; retained as explicit Missing category (>30%; avoids unsupported imputation).")
    report += ["Cleaning decisions:\n"+"\n".join(strategies), f"Clean shape: {clean.shape}"]
    # Univariate views and IQR counts.
    for col in ["age","fare"]:
        fig,ax=plt.subplots(1,2,figsize=(10,3.5)); sns.histplot(clean[col],kde=True,ax=ax[0]); ax[0].set_title(f"{col.title()} distribution"); sns.boxplot(x=clean[col],ax=ax[1]); ax[1].set_title(f"{col.title()} boxplot"); savefig(f"univariate_{col}.png")
        q1,q3=clean[col].quantile([.25,.75]); iqr=q3-q1; n=int(((clean[col]<q1-1.5*iqr)|(clean[col]>q3+1.5*iqr)).sum())
        report.append(f"{col} IQR outlier count: {n} (bounds {q1-1.5*iqr:.3f}, {q3+1.5*iqr:.3f}).")
    mean,median,mode=clean.fare.mean(),clean.fare.median(),clean.fare.mode().iloc[0]
    report.append(f"Fare mean={mean:.3f}, median={median:.3f}, mode={mode:.3f}; ordering mean > median > mode indicates right skew.")
    # Bivariate group rates computed with explicit boolean masks.
    by_sex={str(v):float(clean.loc[clean.sex.eq(v),'survived'].mean()) for v in clean.sex.dropna().unique()}
    by_class={str(v):float(clean.loc[clean.pclass.eq(v),'survived'].mean()) for v in sorted(clean.pclass.dropna().unique())}
    by_both={f"{s}, class {c}":float(clean.loc[(clean.sex.eq(s)) & (clean.pclass.eq(c)),'survived'].mean()) for s in clean.sex.dropna().unique() for c in sorted(clean.pclass.dropna().unique())}
    report += [f"Survival by sex: {by_sex}",f"Survival by pclass: {by_class}",f"Survival by sex and pclass (boolean masks): {by_both}"]
    corr_cols=["survived","pclass","age","sibsp","parch","fare"]
    corr=clean[corr_cols].corr(); plt.figure(figsize=(7,5)); sns.heatmap(corr,annot=True,cmap="coolwarm",center=0,fmt=".2f"); plt.title("Six-feature correlation matrix"); savefig("correlation_heatmap.png")
    pairs=[(abs(corr.loc[a,b]),a,b,float(corr.loc[a,b])) for i,a in enumerate(corr_cols) for b in corr_cols[i+1:]]
    strongest=sorted(pairs,reverse=True)[:2]
    report.append("Two strongest absolute off-diagonal correlations: "+"; ".join(f"{a}–{b}: r={v:.3f} (|r|={m:.3f})" for m,a,b,v in strongest)+". Interpret cautiously: association is not causation.")
    # Four multivariate story charts with 2–4 sentence interpretations.
    fig,ax=plt.subplots(2,2,figsize=(12,9))
    sns.barplot(data=clean,x="sex",y="survived",hue="pclass",errorbar=None,ax=ax[0,0]); ax[0,0].set_title("Survival by sex and class")
    sns.boxplot(data=clean,x="survived",y="age",hue="sex",ax=ax[0,1]); ax[0,1].set_title("Age by survival and sex")
    sns.scatterplot(data=clean,x="age",y="fare",hue="survived",style="sex",alpha=.65,ax=ax[1,0]); ax[1,0].set_title("Fare and age by survival")
    sns.barplot(data=clean,x="embark_town",y="survived",hue="pclass",errorbar=None,ax=ax[1,1]); ax[1,1].set_title("Survival by embarkation and class"); savefig("multivariate_story.png")
    report.append("Chart interpretations (multivariate_story.png):\n1. Survival bars by sex and class show the strongest separation by sex, with class differences visible within groups; this is consistent with the observed group rates.\n2. Age boxplots compare survivor distributions within sex; overlap means age alone does not perfectly separate outcomes.\n3. The age–fare scatterplot shows substantial overlap, while higher fares and survivor status appear more common together; this is descriptive, not causal.\n4. Survival by embarkation town and class varies across groups; class composition may partly explain port-level differences.")
    # Required exploratory full-clean-data z scores, kept separate from modeling.
    standardized=clean[["age","fare"]].copy(); before=standardized.agg(["mean","std"])
    z=(standardized-standardized.mean())/standardized.std(ddof=1)
    report.append("Exploratory age/fare standardization (full cleaned EDA data; not used by model):\nBefore:\n"+before.to_string()+"\nAfter:\n"+z.agg(["mean","std"]).to_string())
    # Classification split first, then train-fold-fitted preprocessing only.
    target=clean.survived.astype(int)
    features=clean[["pclass","sex","age","sibsp","parch","fare","embarked"]]
    Xtr,Xte,ytr,yte=train_test_split(features,target,test_size=.2,random_state=42,stratify=target)
    report.append(f"Stratified split class balance: train={ytr.value_counts(normalize=True).sort_index().round(3).to_dict()}, test={yte.value_counts(normalize=True).sort_index().round(3).to_dict()}. Stratification preserves outcome proportions in both folds.")
    nums=["pclass","age","sibsp","parch","fare"]; cats=["sex","embarked"]
    prep=ColumnTransformer([("num",Pipeline([("imputer",SimpleImputer(strategy="median")),("scale",StandardScaler())]),nums),
        ("cat",Pipeline([("imputer",SimpleImputer(strategy="most_frequent")),("onehot",OneHotEncoder(handle_unknown="ignore"))]),cats)])
    models={"Logistic Regression":LogisticRegression(max_iter=2000,random_state=42),"Decision Tree":DecisionTreeClassifier(max_depth=5,random_state=42),"Random Forest":RandomForestClassifier(n_estimators=300,random_state=42,n_jobs=-1)}
    rows=[]; curves=[]; fitted={}
    for name,est in models.items():
        pipe=Pipeline([("preprocess",prep),("model",est)]); pipe.fit(Xtr,ytr); fitted[name]=pipe
        pred=pipe.predict(Xte); score=pipe.predict_proba(Xte)[:,1]
        cm=confusion_matrix(yte,pred); auc=roc_auc_score(yte,score)
        rows.append({"Classifier":name,"Accuracy":accuracy_score(yte,pred),"Precision":precision_score(yte,pred,zero_division=0),"Recall":recall_score(yte,pred,zero_division=0),"F1":f1_score(yte,pred,zero_division=0),"AUC":auc,"Confusion matrix":str(cm.tolist())})
        fpr,tpr,_=roc_curve(yte,score); curves.append((name,fpr,tpr,auc))
    metrics=pd.DataFrame(rows); report.append("Classifier metrics:\n"+metrics.to_string(index=False,float_format=lambda x:f"{x:.3f}"))
    plt.figure(figsize=(6,5))
    for name,fpr,tpr,auc in curves: plt.plot(fpr,tpr,label=f"{name} (AUC {auc:.3f})")
    plt.plot([0,1],[0,1],"k--"); plt.xlabel("False positive rate"); plt.ylabel("True positive rate"); plt.legend(); plt.title("Classifier ROC curves"); savefig("roc_curves.png")
    # Labeled decision tree view.
    tree=fitted["Decision Tree"]; feature_names=tree.named_steps["preprocess"].get_feature_names_out()
    plt.figure(figsize=(20,10)); plot_tree(tree.named_steps["model"],feature_names=feature_names,class_names=["Not survived","Survived"],filled=True,rounded=True,max_depth=3,fontsize=7); savefig("decision_tree.png")
    # Imbalance three-way comparison; resampling is restricted to Xtr after train-only transform.
    base=Pipeline([("preprocess",prep),("model",LogisticRegression(max_iter=2000,random_state=42))]).fit(Xtr,ytr)
    balanced=Pipeline([("preprocess",prep),("model",LogisticRegression(max_iter=2000,class_weight="balanced",random_state=42))]).fit(Xtr,ytr)
    train_transform=prep.fit(Xtr).transform(Xtr); test_transform=prep.transform(Xte)
    smx,smy=SMOTE(random_state=42).fit_resample(train_transform,ytr)
    sm_model=LogisticRegression(max_iter=2000,random_state=42).fit(smx,smy)
    imb=[]
    for label,model,xx in [("baseline",base,Xte),("class_weight=balanced",balanced,Xte),("SMOTE train fold",sm_model,test_transform)]:
        pp=model.predict(xx); imb.append({"Variant":label,"Precision":precision_score(yte,pp,zero_division=0),"Recall":recall_score(yte,pp,zero_division=0),"F1":f1_score(yte,pp,zero_division=0)})
    report.append(f"Outcome balance: {target.value_counts().to_dict()}\nImbalance comparison:\n{pd.DataFrame(imb).to_string(index=False,float_format=lambda x:f'{x:.3f}')}\nChoose using the target metric: class weighting/SMOTE can improve minority recall while reducing precision; the table records the observed trade-off.")
    # Random forest tuning with OOB enabled on best estimator construction.
    rf_pipe=Pipeline([("preprocess",prep),("model",RandomForestClassifier(random_state=42,n_jobs=-1,oob_score=True))])
    grid=GridSearchCV(rf_pipe,
        {"model__n_estimators":[150,300],"model__max_depth":[None,8,14],"model__max_features":["sqrt",0.8]},cv=5,scoring="f1",n_jobs=-1)
    grid.fit(Xtr,ytr); best_params={k.replace("model__",""):v for k,v in grid.best_params_.items()}
    tuned=grid.best_estimator_
    report.append(f"Random Forest GridSearchCV best params: {best_params}; CV F1={grid.best_score_:.3f}; refit training-split OOB score={tuned.named_steps['model'].oob_score_:.3f}.")
    # Predict fare from remaining available features; own train-only preprocessing.
    reg_features=clean.drop(columns=["fare"]); fare_target=clean.fare
    rXtr,rXte,rytr,ryte=train_test_split(reg_features,fare_target,test_size=.2,random_state=42)
    rnums=reg_features.select_dtypes(include=np.number).columns.tolist(); rcats=[c for c in reg_features.columns if c not in rnums]
    rprep=ColumnTransformer([("num",Pipeline([("imp",SimpleImputer(strategy="median")),("scale",StandardScaler())]),rnums),
       ("cat",Pipeline([("imp",SimpleImputer(strategy="most_frequent")),("oh",OneHotEncoder(handle_unknown="ignore"))]),rcats)])
    reg=Pipeline([("preprocess",rprep),("model",LinearRegression())]).fit(rXtr,rytr); rpred=reg.predict(rXte)
    mae=mean_absolute_error(ryte,rpred); rmse=float(np.sqrt(mean_squared_error(ryte,rpred))); r2=r2_score(ryte,rpred); n=len(ryte); p=reg.named_steps["preprocess"].transform(rXte).shape[1]; adj=1-(1-r2)*(n-1)/(n-p-1) if n>p+1 else float("nan")
    residuals=ryte-rpred; plt.figure(figsize=(6,4)); sns.scatterplot(x=rpred,y=residuals,alpha=.65); plt.axhline(0,color="red",linestyle="--"); plt.xlabel("Predicted fare"); plt.ylabel("Residual"); plt.title("Fare regression residuals"); savefig("fare_residuals.png")
    report.append(f"Fare regression: MAE={mae:.3f}, RMSE={rmse:.3f}, R²={r2:.3f}, adjusted R²={adj:.3f}. Residual plot: inspect for widening spread/banding; residual variance is not perfectly constant across the prediction range, suggesting heteroscedasticity.")
    # Store best classifier complete pipeline for raw features and demonstrate reload.
    best_name=metrics.sort_values(["F1","AUC"],ascending=False).iloc[0]["Classifier"]
    joblib.dump(fitted[best_name],ROOT/"best_pipeline.joblib")
    loaded=joblib.load(ROOT/"best_pipeline.joblib"); sample=features.iloc[[0]]
    report.append(f"Saved/reloaded complete raw-input pipeline: best by F1 then AUC is {best_name}; sample raw prediction={int(loaded.predict(sample)[0])}.")
    # Final table keeps metric groups separate.
    reg_row={"Model":"Linear Regression (fare)","Accuracy":"—","Precision":"—","Recall":"—","F1":"—","AUC":"—","MAE":mae,"RMSE":rmse,"R²":r2,"Adjusted R²":adj}
    final=metrics.drop(columns="Confusion matrix").rename(columns={"Classifier":"Model"}); final[["MAE","RMSE","R²","Adjusted R²"]]="—"; final=pd.concat([final,pd.DataFrame([reg_row])],ignore_index=True)
    report.append("Final separated metric groups (classification vs regression):\n"+final.to_string(index=False))
    rec=metrics.set_index("Classifier")
    report.append(f"Deployment recommendation: Deploy {best_name}. It achieved F1={rec.loc[best_name,'F1']:.3f} and AUC={rec.loc[best_name,'AUC']:.3f} on the held-out stratified set, balancing threshold performance and ranking ability. Its held-out accuracy was {rec.loc[best_name,'Accuracy']:.3f}; use the confusion matrix and class-specific precision/recall to set operational thresholds. Keep monitoring because this is a small teaching dataset and its patterns may not transfer to current customers.")
    (ROOT/"analysis_report.md").write_text("# Titanic analytics results\n\n"+"\n\n".join(report)+"\n",encoding="utf-8")
    print("Wrote analytics artifacts to",ROOT)

if __name__=="__main__": main()
