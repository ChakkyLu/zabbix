import pymysql
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from keras import Sequential
from keras.callbacks import EarlyStopping
from keras.engine.saving import model_from_json
from keras.layers import LSTM, Dense, Activation
from keras.optimizers import Adam
import matplotlib.pyplot as plt
from xgboost.sklearn import XGBRegressor
import xgboost as xgb
import sys


def modelXGB(trainX, trainy):
    model = xgb.XGBRegressor(booster= 'gblinear', objective='reg:linear', min_child_weight=3, colsample_bytree=0.3, learning_rate=0.05,
                                 max_depth=5, alpha=5, n_estimators=1000, subsample=0.8, cv=3)

    model.fit(trainX, trainy)
    return model

def modelLSTM(trainX, trainy, time_step):
    lr = 0.0006
    model = Sequential()
    model.add(LSTM(200, batch_input_shape=(None, time_step, 1)))
    model.add(Dense(1))
    model.add(Activation("linear"))
    optimizer = Adam(lr=lr)
    model.compile(loss="mean_squared_error", optimizer=optimizer)
    early_stopping = EarlyStopping(monitor='val_loss', mode='auto', patience=20)
    model.fit(trainX, trainy, batch_size=16, epochs=20, validation_split=0.1, callbacks=[early_stopping])
    return model



if __name__ == "__main__":
    modelType = int(sys.argv[1])

    dbhost = "jnc-zabbix.cotpwdfxy0tl.rds.cn-northwest-1.amazonaws.com.cn"
    dbport = 3306
    dbuser = "jnczabbix"
    dbpasswd = "W2df6s9&GA^iVKCI"
    dbdb = "zabbix"

    db = pymysql.connect(host=dbhost,
                       port=dbport,
                       user=dbuser,
                       passwd=dbpasswd,
                       db=dbdb)

    sql = '''select * from trends
            where itemid=34978'''


    result = pd.read_sql(sql, db)
    time_step = 24
    time_ser = 12
    ratio = 0.7


    for h_shift in range(time_ser, time_ser + time_step):
        result['target_' + str(h_shift)] = result["value_avg"].shift(h_shift)

    result = result.dropna().reset_index(drop=True)
    trainCol = list(result.columns.values)
    trainCol.remove("itemid")
    trainCol.remove("clock")
    trainCol.remove("value_min")
    trainCol.remove("value_max")
    trainCol.remove("value_avg")

    dataX = result[trainCol].values
    datay = result["value_avg"].values

    if modelType == 1:
        dataX = np.array(dataX).reshape(len(dataX), time_step, 1)
        datay = np.array(datay).reshape(len(datay),1)

    if modelType == 2:
        pass

    trainX = dataX[0:int(size*ratio)]
    trainy = datay[0:int(size*ratio)]
    testX = dataX[int(size*ratio):]
    testy = datay[int(size*ratio):]

    if modelType == 1:
        model = modelLSTM(trainX, trainy, time_step)
    if modelType == 2:
        model = modelXGB(trainX, trainy)

    predicted = model.predict(testX)

    # for i in range(size-time_step-1):
    #     x = X[i:i+time_step]
    #     y = X[i+time_step+time_ser]
    #     dataX.append(x.tolist())
    #     datay.append(y.tolist())

    plt.figure()
    plt.plot(predicted, color='r', label='predicted_data')
    plt.plot(testy, color='b', label='real_data')
    plt.legend()
    plt.show()
    plt.savefig("kk.png")
