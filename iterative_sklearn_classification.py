import json
import math
import pprint
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model import *
from sklearn.preprocessing import *
from sklearn.experimental import enable_hist_gradient_boosting
from sklearn.model_selection import *
from sklearn.kernel_ridge import *
from sklearn.svm import *
from sklearn.neighbors import *
from sklearn.gaussian_process import *
from sklearn.cross_decomposition import *
from sklearn.naive_bayes import *
from sklearn.tree import *
from sklearn.experimental import *
from sklearn.ensemble import *
from sklearn.metrics import *
from sklearn. preprocessing import *

forex = pd.read_csv('prep_forex.csv', header=[0,1], index_col=0)
index = pd.read_csv('prep_index.csv', header=[0,1,2], index_col=0)

forex_pairs = list(set([x[1] for x in forex.columns if x[0] == 'Close']))
index_pairs = list(set([(x[1], x[2]) for x in index.columns if x[0] == 'Close']))

# reg_models = [LinearRegression, Ridge, RidgeCV, Lasso, LassoCV, LassoLarsCV, LassoLarsIC, MultiTaskLasso,
#               ElasticNet, ElasticNetCV, MultiTaskElasticNet, MultiTaskElasticNetCV, LassoLars,
#               OrthogonalMatchingPursuit, BayesianRidge, ARDRegression,
#               SGDRegressor, PassiveAggressiveRegressor, HuberRegressor, RANSACRegressor, TheilSenRegressor,
#               KernelRidge, SVR, NuSVR, KNeighborsRegressor, RadiusNeighborsRegressor,
#               GaussianProcessRegressor, PLSRegression, DecisionTreeRegressor,
#               BaggingRegressor, AdaBoostRegressor, ExtraTreesRegressor, GradientBoostingRegressor,
#               RandomForestRegressor, HistGradientBoostingRegressor]

cls_models = [RidgeClassifier, LogisticRegression,  LogisticRegression, LogisticRegressionCV,
              SGDClassifier, Perceptron, PassiveAggressiveClassifier, SVC, NuSVC, LinearSVC,
              KNeighborsClassifier, NearestCentroid, GaussianProcessClassifier,
              GaussianNB, MultinomialNB, ComplementNB, BernoulliNB, CategoricalNB,
              DecisionTreeClassifier, BaggingClassifier, AdaBoostClassifier, ExtraTreesClassifier,
              GradientBoostingClassifier, RandomForestClassifier, HistGradientBoostingClassifier]


time_split_ratio = [(0.2, 0.5), (0.3, 0.33), (0.4, 0.25), (0.5, 0.2), (0.6, 0.166), (0.7, 0.14), (0.8, 0.125), (0.9, 0.11), (1, 0.1)]
metric = 'Close'
metrics = ['Open', 'Close', 'Low', 'High']
target = [metric+'_Ret']
forex_features = ['Intraday_HL', 'Intraday_OC', 'Prev_close_open'] + [y+x for x in ['_Ret', '_Ret_MA_3', '_Ret_MA_15', '_Ret_MA_45', '_MTD', '_YTD'] for y in metrics]
index_features = ['Intraday_HL', 'Intraday_OC', 'Prev_close_open'] + [y+x for x in ['_Ret', '_Ret_MA_3', '_Ret_MA_15', '_Ret_MA_45', '_MTD', '_YTD'] for y in (metrics + ['Volume'])]
n_bins = 5
scalers = [Binarizer, KBinsDiscretizer]

def plot_results(y_true, y_pred, model):
    plot_df = pd.concat([y_true.reset_index(drop=True), pd.DataFrame(y_pred)], axis=1, ignore_index=True)
    plt.figure()
    plt.plot(plot_df)
    plt.title(model().__class__.__name__)

def run_sklearn_model(model, train, test, features, target):
    try:
        X_train, y_train = train
        X_test, y_test = test
    except:
        pass
    reg = model()#max_iter=1000, tol=1e-3)
    reg.fit(X_train, y_train)
    try:
        pprint.pprint(dict(zip(X_train.columns.values,reg.feature_importances_)))
    except:
        pass
    y_pred = reg.predict(X_test)
    try:
        return({"F1" :f1_score(y_test, y_pred, average='weighted'),
            "Precision": precision_score(y_test, y_pred, average='weighted'),
            "Recall": recall_score(y_test, y_pred, average='weighted'),
            "AUC": roc_auc_score(y_test, reg.fit(X_train, y_train).decision_function(X_test), multi_class='ovr')})
    except:
        return({"F1" :f1_score(y_test, y_pred, average='weighted'),
            "Precision": precision_score(y_test, y_pred, average='weighted'),
            "Recall": recall_score(y_test, y_pred, average='weighted')})
    #     y_pred = ([x[0] for x in y_pred])
    #     for i in range(len(y_pred)):
    #         if(np.isnan(y_pred[i])):
    #             y_pred[i] = 0
    #     return({"F1" :f1_score(y_test, y_pred, average='weighted'),
    #         "Precision": precision_score(y_test, y_pred),
    #         "Recall": recall_score(y_test, y_pred),
    #         "AUC": roc_auc_score(y_test, reg.fit(X_train, y_train).decision_function(X_test))})
    # print("MSE: ", mean_squared_error(y_test, y_pred))
    # print("R2: ", r2_score(y_test, y_pred))
    # plot_results(y_test, y_pred, model)

def split_scale(X, y, scaler, shuffle=False, poly=False, transf_features_also=False, test_size=0.1):
    X_train, X_test, y_train, y_test = train_test_split(X, y, shuffle=shuffle, test_size=test_size)
    if(poly):
        X_train = PolynomialFeatures(2).fit_transform(X_train)
        X_test = PolynomialFeatures(2).fit_transform(X_test)
    if (scaler == scalers[-1]):
        scaler_X = scaler(n_bins=n_bins, encode='ordinal', strategy='uniform')
    else:
        scaler_X = scaler()
    scaler_X = scaler_X.fit(X_train)
    if(transf_features_also):
        X_train = scaler_X.transform(X_train)
        X_test = scaler_X.transform(X_test)
    if (scaler == scalers[-1]):
        scaler_y = scaler(n_bins=n_bins, encode='ordinal', strategy='uniform')
    else:
        scaler_y = scaler()
    scaler_y = scaler_y.fit(y_train)
    y_train = scaler_y.transform(y_train)
    y_test = scaler_y.transform(y_test)
    return(X_train, X_test, y_train, y_test)


def do_forex(cur, model, transf = None, shuffle=False, poly=False, transf_features_also=False, split_ratio = (1,0.1) ):
    forex_cols = [x for x in forex.columns if x[1] == cur]
    forex_temp = forex[:split_ratio[0]*forex.count]
    X = forex_temp[[col for col in forex_cols if col[0] in forex_features + ['Time features']]][:-1]
    y = forex_temp[[col for col in forex_cols if col[0] in target]].shift(-1)[:-1]
    X = X.dropna(how='any')
    y = y[y.index.isin(X.index)]
    X_train, X_test, y_train, y_test = split_scale(X, y, transf, shuffle, poly, transf_features_also, split_ratio[1])
    res = run_sklearn_model(model, (X_train, y_train), (X_test, y_test), forex_features, target)
    return(res)

def do_index(cur, model, transf = None, shuffle=False, poly=False, transf_features_also=False, split_ratio = (1,0.1) ):
    index_cols = [x for x in index.columns if x[1] == cur[0] and x[2] == cur[1]]
    index_temp = index[:split_ratio[0] * index.count]
    X = index_temp[[col for col in index_cols if col[0] in index_features + ['Time features']]][:-1]
    y = index_temp[[col for col in index_cols if col[0] in target]].shift(-1)[:-1]
    X = X.dropna(how='any')
    y = y[y.index.isin(X.index)]
    X_train, X_test, y_train, y_test = split_scale(X, y, transf, shuffle, poly, transf_features_also, split_ratio[1])
    res = run_sklearn_model(model, (X_train, y_train), (X_test, y_test), index_features, target)
    return(res)

def iterate_markets():
    reg_res = []
    for f_m in (forex_pairs+index_pairs):
        print(f_m)
        for model in cls_models:
            for scaler in scalers:
                for shuffle in [True, False]:
                    for poly in [True, False]:
                        for transf_features_also in [True, False]:
                            for spilt_ratio in time_split_ratio:
                                try:
                                    if (f_m in forex_pairs):
                                        res = do_forex(f_m, model, scaler, shuffle, poly, transf_features_also,
                                                       spilt_ratio)
                                    else:
                                        res = do_index(f_m, model, scaler, shuffle, poly, transf_features_also,
                                                       spilt_ratio)
                                except:
                                    # res = do_forex(f_m, model, scaler, shuffle, poly, transf_features_also)
                                    continue
                                res['Pair'] = f_m
                                res['Transformation'] = scaler().__class__.__name__ if scaler is not None else None
                                res['Shuffle'] = shuffle
                                res['Model'] = model().__class__.__name__
                                res['Poly'] = poly
                                res['Features transformed'] = transf_features_also
                                res['Number of years'] = split_ratio[0]
                                res['split ratio'] = split_ratio[1]~
                                print(res)
                                reg_res.append(res)
    return(reg_res)

res = iterate_markets()

res_df = pd.DataFrame(res, columns= ['Pair', 'Model', 'Transformation', 'Shuffle', 'Poly', 'Features transformed', 'F1', 'Precision', 'Recall', 'AUC'])
# print(res_df)
res_df.to_csv("sk_classification.csv")
# do_stuff(["HKD", "Hang Seng"], LinearRegression)
