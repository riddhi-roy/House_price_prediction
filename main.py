import pandas as pd
import numpy as np
import os
import joblib

from sklearn.model_selection import StratifiedShuffleSplit
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler,OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import root_mean_squared_error
from sklearn.model_selection import cross_val_score



MODEL_FILE="model.pkl"
PIPELINE_FILE = "pipeline.pkl"

def build_pipeline(num_attribs,cat_attribs):
    #  for numerical columns 
    num_pipeline = Pipeline([
    ("imputer",SimpleImputer(strategy="median")),
    ("scaler",StandardScaler())
    ])

    #for categorical columns
    cat_pipeline=Pipeline([
    ("onehot",OneHotEncoder(handle_unknown="ignore"))
    ])


    #construct the full pipeline 
    full_pipeline = ColumnTransformer([
    ("num",num_pipeline,num_attribs),
    ("cat",cat_pipeline,cat_attribs)
    ])

    return full_pipeline


if not os.path.exists(MODEL_FILE):
    #TRAINING PHASE
    housing = pd.read_csv("housing.csv")
    #Create stratified test set
    housing['income_cat'] = pd.cut(housing["median_income"],bins=[0.0,1.5,3.0,4.5,6.0,np.inf],labels=[1,2,3,4,5])


    split = StratifiedShuffleSplit(n_splits=1,test_size=0.2,random_state=42)

    for train_index,test_index in split.split(housing,housing['income_cat']):
        df=housing.loc[test_index].drop("income_cat",axis=1)
        df.to_csv("input.csv",index=False)
        housing=housing.loc[train_index].drop("income_cat",axis=1)#we will work on this data

    
    
    housing_labels = housing["median_house_value"].copy()
    housing_features = housing.drop("median_house_value",axis=1)     

    num_attribs=housing_features.drop("ocean_proximity",axis=1).columns.tolist()
    cat_attribs=["ocean_proximity"] 

    pipeline=build_pipeline(num_attribs,cat_attribs)
    housing_prepared = pipeline.fit_transform(housing_features)
    
    model = RandomForestRegressor(random_state=42)
    model.fit(housing_prepared,housing_labels)

    #save model and pipeline 
    joblib.dump(model,MODEL_FILE)
    joblib.dump(pipeline,PIPELINE_FILE)
    print("Model is trained.Congrats ")

else:
    model=joblib.load(MODEL_FILE)
    pipeline=joblib.load(PIPELINE_FILE)

    input_data=pd.read_csv("input.csv")
    transformed_input = pipeline.transform(input_data)
    predictions=model.predict(transformed_input)
    input_data["median_house_value"]=predictions

    input_data.to_csv("output.csv",index=False)
    print("Inference complete. Results saved to output.csv")
