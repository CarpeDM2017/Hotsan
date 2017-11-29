#! hotsan2.7/bin/activate

"""
Bayesian optimization of the hyperparameters of HotSan,
the algorithm for automated trading of cryptocurrencies.

list of hyperparameters =======================

    hyperparameters optimized by script

    window     : window size of forecast
    window_std : window size of standard deviation data
    n_batch    : number of batches for training DNN
                 bigger the number, smaller the window for lookback
    n_model    : number of models for ensemble training
    n_dense1   : number of additional dense layers before GRU in DNN
    n_dense2   : number of additional dense layers after GRU in DNN
    n_gru      : number of additional GRU layers in DNN

    hyperparameters excluded from optimization

    csv_path   : csv file obtained from Google BigQuery
    max_epoch  : the maximum number of epochs if fails to stop early
    patience   : the maximum number of ignoring the increment of validation loss
    validation : training-test ratio for validation in DNN
    n_bayes    : number of trials for bayesian optimization

    verbose    : if True, print the training procedure
                 if False, print the optimization procedure
===============================================

"""
import numpy as np
import pandas as pd
import sys
from datetime import datetime

from keras.models import Sequential
from keras.layers import Dense, Activation, GRU
from keras.callbacks import EarlyStopping
from progressbar import ProgressBar
from bayes_opt import BayesianOptimization

csv_path = 'query_20170913.csv'
version = '20170914'

# predefined hyperparameters excluded from optimization
max_epoch = 100
patience = 5
validation = 0.33
n_bayes = 100
verbose = False


def main():
    """
    the call procedure of the script
    gp_params  : input for the scikit-learn Gaussian process regression
    params : hyperparameters for Bayesian optimization

    main() is called when initialized
    main -> BayesianOptimization -> hotsan -> read_data -> scaler -> loss
        -> BayesianOptimization -> hotsan -> ...

    """
    print("")
    print("Bayesian optimization for HotSan v" + version)
    print("")
    gp_params = {'alpha' : 1e-5}
    params = {'window' : (1, 60), 'window_std' : (1, 60), 'n_batch' : (10, 100), 'n_model' : (1,5), 'n_dense1' : (0,10), 'n_dense2' : (0,10), 'n_gru' : (0,5) }
    bayes = BayesianOptimization(hotsan, params, verbose=1-verbose)
    bayes.maximize(init_points=1, n_iter=n_bayes, **gp_params)
    print("")
    print('Results')
    print("")
    print(bayes.res['max'])

    return

def loss() :
    """
    Not implemented

    """
    # TODO
    pass

def scaler(df, window) :
    """
    Rescales data into range [0,1],
    where the GRU layer works best

    :param df: DataFrame object from read_data
    :param window: window size of forecast
    :return: rescaled data and the minmax scales from original data

    """
    try :
        assert isinstance(df, pd.DataFrame), "Must pass DataFrame as argument"
        assert len(df)!=0, "Moving std too large"
        window = int(window)

        data = np.array(df.iloc[:-(len(df) % window)])
        data = np.array(np.split(data, len(data) / window))
        scale_max = np.amax(data, axis=1)
        scale_min = np.amin(data, axis=1)
        data = (data - scale_min[:, None, :]) / (scale_max[:, None, :] - scale_min[:, None, :] + 1e-4)  # error term added to prevent zero-division
    except AssertionError : raise
    return data, scale_max, scale_min


def read_data(window, window_std, n_batch) :
    """
    Convert csv data into numpy array with the desired dimensions
    (n_batch, window * number of explanatory variables)

    Explanatory variables  :  average price per minute
                              average volume per minute
                              moving std of average price for given size of window_std

    :param window: window size of forecast
    :param window_std: window size of standard deviation data
    :param n_batch: number of batches for training DNN
    :return: a tuple for training and another tuple for validation

    """
    try :
        assert csv_path is not None, "Must pass file path as argument"
        window_std = int(window_std)
        n_batch = int(n_batch)

        f = pd.read_csv(csv_path)
        idx_tmp = f['date'].astype(str) + " " + f['hour'].astype(str) + ":" + f['minute'].astype(str)   # minute-interval
        fmt = '%Y-%m-%d %H:%M'
        idx_tmp = idx_tmp.apply(lambda x : datetime.strptime(x, fmt))
        f['index'] = idx_tmp

        start = idx_tmp.iloc[0]
        end = idx_tmp.iloc[-1]
        idx = pd.date_range(start, end, freq='1min')
        coin = f['coin'].unique().astype(str)

        lst = []
        for i in range(len(coin)):
            lst.append(f.loc[f['coin'] == coin[i]][['volume', 'avg_price', 'index']])
            lst[-1].index = lst[-1]['index']
            lst[-1] = lst[-1][['volume', 'avg_price']]
            lst[-1].columns = [coin[i] + '_volume', coin[i] + '_price']     # price, volume
            lst[-1][coin[i] + '_std'] = lst[-1][coin[i] + '_price']
        df = pd.concat(lst, axis=1)
        df = df.reindex(idx)
        df.iloc[:, ::3] = df.iloc[:, ::3].fillna(0)     # volume filled with 0
        df.iloc[:, 1::3] = df.iloc[:, 1::3].fillna(method='ffill')      # price filled with forward-fill
        for i in range(len(coin)):
            df.iloc[:, 2 + 3 * i] = df.iloc[:, 1 + 3 * i].rolling(window=window_std).std()      # moving std of price
        df.dropna(inplace=True)

        data = scaler(df, window)[0]
        assert n_batch < len(data), "The number of batches is bigger than data"
        X, Y = [], []
        for i in range(n_batch):
            X.append(data[i:-n_batch + i])
            Y.append(data[-n_batch + i])
        X = np.array(X)
        Y = np.array(Y)[:, :, 1::3]
        X = X.reshape((n_batch, X.shape[1], X.shape[2] * X.shape[3]))
        Y = Y.reshape((n_batch, Y.shape[1] * Y.shape[2]))

        test = int(n_batch * validation)
        trainX, trainY = X[:-test], Y[:-test]
        testX, testY = X[-test:], Y[-test:]
    except AssertionError : raise
    return (trainX, trainY), (testX, testY)


def hotsan(window, window_std, n_batch, n_model, n_dense1, n_dense2, n_gru) :
    """
    DNN with Dense layers and GRU
    Dense -> Hard_sigmoid -> GRU -> Dense -> Linear
    input dimension : (n_batch, window * number of explanatory variables)
    output dimension : (n_batch, window * number of coins)

    :param window: window size of forecast
    :param window_std: window size of standard deviation data
    :param n_batch: number of batches for training DNN
    :param n_model: number of models for ensemble training
    :param n_dense1: number of additional dense layers before GRU in DNN
    :param n_dense2: number of additional dense layers after GRU in DNN
    :param n_gru: number of additional GRU layers in DNN
    :param verbose: toggle option whether to print training procedures or the optimization procedure
    :return: the objective function to maximize (minimize) defined by the loss() function

    """
    try :
        train, test = read_data(window, window_std, n_batch)
        n_model = int(n_model)
        n_dense1 = int(n_dense1)
        n_dense2 = int(n_dense2)
        n_gru = int(n_gru)

        EarlyStopping(patience=patience)
        models = []
        for i in range(n_model) :
            if verbose :
                print("")
                print("Model No. " + str(i+1) + "/" + str(n_model))
                print("")
            models.append(Sequential())
            models[i].add(Dense(train[0].shape[-1], batch_input_shape=(1, train[0].shape[1], train[0].shape[2])))
            for d1 in range(n_dense1) :
                models[i].add(Dense(train[0].shape[-1]))
            models[i].add(Activation('hard_sigmoid'))
            for g in range(n_gru) :
                models[i].add(GRU(train[0].shape[-1], return_sequences=True))
            models[i].add(GRU(train[0].shape[-1]))
            for d2 in range(n_dense2) :
                models[i].add(Dense(train[0].shape[-1]))
            models[i].add(Dense(train[1].shape[-1], activation='linear'))
            models[i].compile(optimizer='adam', loss='mse')

            local_min = np.inf
            overfit = 0
            for j in range(max_epoch) :
                history = models[i].fit(train[0], train[1], epochs=1, batch_size=1, verbose=verbose, validation_split=validation)
                if local_min > history.history['val_loss'][-1] :
                    local_min = history.history['val_loss'][-1]
                    overfit = 0
                else : overfit += 1
                if overfit > patience : break       # training stops early when val_loss does not decrease for a given period

        if verbose :
            print("")
            print("Ensemble")
            print("")
            bar = ProgressBar(max_value=len(test[0])*n_model)
        ensemble = []
        for i in range(len(test[0])) :
            tmp = 0
            for j in range(n_model) :
                tmp += np.array(models[j].predict(test[0][i].reshape((1, test[0].shape[1], test[0].shape[2]))))
                if verbose : bar.update(i*n_model+j+1)
            tmp /= n_model      # ensemble by simple average
            ensemble.append(tmp)
        ensemble = np.array(ensemble)

    # TODO
        loss = np.mean((ensemble - test[1])**2)     # Not Implemented
    except : loss = 1

    return -loss


if __name__ == '__main__' :
    main()
