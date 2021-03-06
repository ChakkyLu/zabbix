#!/usr/bin/env python3

import pymysql
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from keras import Sequential
from keras.callbacks import EarlyStopping
from keras.engine.saving import model_from_json
from keras.layers import LSTM, Dense, Activation, Dropout
from keras.optimizers import Adam
import matplotlib.pyplot as plt
from xgboost.sklearn import XGBRegressor
import xgboost as xgb
import sys
import datetime
import os
from keras import layers
import sys
from sklearn.preprocessing import MinMaxScaler



class forecastModel():

    def __init__(self, time_step=24, time_ser=12, ratio=0.7, modelType=2):
        self.config = {
            'dbhost': "jnc-zabbix.cotpwdfxy0tl.rds.cn-northwest-1.amazonaws.com.cn",
            'dbport': 3306,
            'dbuser': "jnczabbix",
            'dbpasswd': "W2df6s9&GA^iVKCI",
            'dbdb': "zabbix"
        }
        self.ratio = 0.7
        self.time_step = time_step
        self.time_ser = time_ser
        self.modelType = modelType

    def initDB(self):
        db = pymysql.connect(host=self.config['dbhost'],
                           port=self.config['dbport'],
                           user=self.config['dbuser'],
                           passwd=self.config['dbpasswd'],
                           db=self.config['dbdb'])
        return db

    def modelXGB(self, trainX, trainy):
        model = xgb.XGBRegressor(booster= 'gblinear', objective='reg:linear', min_child_weight=3, colsample_bytree=0.3, learning_rate=0.05,
                                     max_depth=5, alpha=5, n_estimators=1000, subsample=0.8, cv=3)

        model.fit(trainX, trainy)
        return model

    def modelLSTM(self, trainX, trainy, time_step):
        lr = 0.0006
        model = Sequential()
        model.add(LSTM(200, batch_input_shape=(None, time_step+1, 1)))
        model.add(Dense(1))
        model.add(Activation("linear"))
        optimizer = Adam(lr=lr)
        model.compile(loss="mean_squared_error", optimizer=optimizer)
        early_stopping = EarlyStopping(monitor='val_loss', mode='auto', patience=20)
        model.fit(trainX, trainy, batch_size=16, epochs=10, validation_split=0.1, callbacks=[early_stopping])
        return model

    def trainModel(self):
        db = self.initDB()
        sql = '''select * from trends
                where itemid=%s''' % self.itemid
        result = pd.read_sql(sql, db)

        result['Datetime'] = pd.to_datetime(result['clock'], unit='s')
        result['value_avg'] = result['value_avg'] / 100

        for h_shift in range(self.time_ser, self.time_ser + self.time_step):
            result['target_' + str(h_shift)] = result["value_avg"].shift(h_shift)

        result = result.dropna().reset_index(drop=True)
        result['Hour'] = result['Datetime'].dt.hour
        trainCol = list(result.columns.values)
        trainCol.remove("itemid")
        trainCol.remove("clock")
        trainCol.remove("value_min")
        trainCol.remove("value_max")
        trainCol.remove("value_avg")
        trainCol.remove("num")
        trainCol.remove("Datetime")

        dataX = result[trainCol].values
        datay = result["value_avg"].values
        size = len(result)


        if self.modelType == 1:
            dataX = dataX.reshape(size, self.time_step+1, 1)
            datay = np.array(datay).reshape(len(datay),1)

        trainX = dataX[0:int(size*self.ratio)]
        trainy = datay[0:int(size*self.ratio)]
        testX = dataX[int(size*self.ratio):]
        testy = datay[int(size*self.ratio):]

        print("TrainData Size: %d" % size)

        if size:
            if self.modelType == 1:
                model = self.modelLSTM(trainX, trainy, self.time_step)
            if self.modelType == 2:
                model = self.modelXGB(trainX, trainy)

            self.model = model

        db.close()

    def predict(self):
        if self.model:
            db = self.initDB()
            sql = '''select * from trends
                    where itemid=%s order by clock desc limit %d''' % (self.itemid, self.time_step)
            result = pd.read_sql(sql, db)
            if len(result)>0:
                result['Datetime'] = pd.to_datetime(result['clock'], unit='s')
                result['Hour'] = result['Datetime'].dt.hour
                result['value_avg'] = result['value_avg'] / 100
                dataX = list(result["value_avg"].values)[::-1]
                dataX.append(result.iloc[-1]['Hour']+self.time_ser)
                if self.modelType == 1:
                    dataX = np.array(dataX).reshape(1,self.time_step+1,1)
                print(dataX)
                print(self.itemid)
                forecastValue = self.model.predict(dataX)
                # print(forecastValue)
                return forecastValue
            db.close()
        return None


def modelXGB(trainX, trainy):
    model = xgb.XGBRegressor(booster= 'gblinear', objective='reg:linear', min_child_weight=3, colsample_bytree=0.3, learning_rate=0.05,
                                 max_depth=2, alpha=5, n_estimators=1000, subsample=0.8, cv=3)

    model.fit(trainX, trainy)
    return model

def modelLSTM(trainX, trainy, time_step):
    lr = 0.0005
    model = Sequential()

    model.add(LSTM(200, batch_input_shape=(None, time_step, 1)))
    model.add(Dense(1))
    model.add(Activation("linear"))
    optimizer = Adam(lr=lr)
    model.compile(loss="mean_squared_error", optimizer=optimizer)
    early_stopping = EarlyStopping(monitor='val_loss', mode='auto', patience=20)
    lstm2 = model.fit(trainX, trainy, batch_size=16, epochs=10, validation_split=0.1, callbacks=[early_stopping])

    return model

def getHostList(key, modelType, name):
    fm = forecastModel(modelType=modelType)
    db = fm.initDB()
    sql = '''
        select t1.itemid, t1.name, t1.hostid, t2.host from items t1,
        hosts t2 where t1.name like '%%%s%%' and t1.hostid = t2.hostid
        ''' % (key)
    result = pd.read_sql(sql, db)
    itemsid = list(result['itemid'].values)
    hosts = list(result['host'].values)

    for itemid, host in zip(itemsid,  hosts):
        print(host, itemid)
        fm.model = None
        fm.itemid = itemid
        fm.host = host
        try:
            fm.trainModel()
            forecastValue = fm.predict()
            if forecastValue:
                forecastValue = forecastValue[0][0]
                print("Host: %s, forecastValue: %s" % (host, str(forecastValue)))
                print("zabbix_sender -z 172.32.5.147 -s '%s' -k forecast.%s -o %s" % (host, name, str(forecastValue*100)))
                os.system("zabbix_sender -z 172.32.5.147 -s '%s' -k forecast.%s -o %s" % (host, name, str(forecastValue*100)))
        except:
            pass


def main(key, modelType, name):
    getHostList(key, modelType, name)


def singleModel():

    # dbhost = "jnc-zabbix.cotpwdfxy0tl.rds.cn-northwest-1.amazonaws.com.cn"
    # dbport = 3306
    # dbuser = "jnczabbix"
    # dbpasswd = "W2df6s9&GA^iVKCI"
    # dbdb = "zabbix"
    #
    # db = pymysql.connect(host=dbhost,
    #                    port=dbport,
    #                    user=dbuser,
    #                    passwd=dbpasswd,
    #                    db=dbdb)
    #
    # itemid = 30221
    # sql = '''select * from trends
    #         where itemid=%s''' % itemid
    #
    # result = pd.read_sql(sql, db)
    # result['Datetime'] = pd.to_datetime(result['clock'], unit='s')
    #
    #
    # result.to_csv('/tmp/result.csv')

    result = pd.read_csv("result.csv")
    result = result[['Datetime', 'itemid', 'clock', 'value_min', 'value_max', 'value_avg', 'num']]
    result['Datetime'] = pd.to_datetime(result['Datetime'])
    result['value_avg'] = result['value_avg'] / 100

    time_step = 48
    time_ser = 12
    ratio = 0.7

    for h_shift in range(time_ser, time_ser + time_step):
        result['target_' + str(h_shift)] = result["value_avg"].shift(h_shift)

    result = result.dropna().reset_index(drop=True)
    # result['Hour'] = result['Datetime'].dt.hour
    trainCol = list(result.columns.values)
    trainCol.remove("itemid")
    trainCol.remove("clock")
    trainCol.remove("value_min")
    trainCol.remove("value_max")
    trainCol.remove("value_avg")
    trainCol.remove("num")
    trainCol.remove("Datetime")

    dataX = result[trainCol].values
    datay = result["value_avg"].values
    size = len(result)

    modelType = 1

    if modelType == 1:
        dataX = dataX.reshape(size, time_step, 1)
        datay = np.array(datay).reshape(len(datay),1)

    # if modelType == 2:
    #     pass

    trainX = dataX[0:int(size*ratio)]
    trainy = datay[0:int(size*ratio)]
    testX = dataX[int(size*ratio):]
    testy = datay[int(size*ratio):]

    if modelType == 1:
        model = modelLSTM(trainX, trainy, time_step)
    if modelType == 2:
        model = modelXGB(trainX, trainy)

    predicted = model.predict(trainX)

    print(predicted)
    # for i in range(size-time_step-1):
    #     x = X[i:i+time_step]
    #     y = X[i+time_step+time_ser]
    #     dataX.append(x.tolist())
    #     datay.append(y.tolist())

    plt.figure()
    plt.plot(predicted, color='r', label='predicted_data')
    plt.plot(trainy, color='b', label='real_data')
    plt.legend()
    plt.show()
    # plt.savefig("result2.png")
    plt.savefig("result.png")




if __name__ == "__main__":
    key = 'CPU utilization'
    modelType = int(sys.argv[1])
    key = sys.argv[2] + " " + sys.argv[3]
    # itemid = sys.argv[2]
    main(key, modelType, sys.argv[2])
    # singleModel()

#
#     dbhost = "jnc-zabbix.cotpwdfxy0tl.rds.cn-northwest-1.amazonaws.com.cn"
#     dbport = 3306
#     dbuser = "jnczabbix"
#     dbpasswd = "W2df6s9&GA^iVKCI"
#     dbdb = "zabbix"
#
#     db = pymysql.connect(host=dbhost,
#                        port=dbport,
#                        user=dbuser,
#                        passwd=dbpasswd,
#                        db=dbdb)
#
#     itemid = 43740
#     sql = '''select * from trends
#             where itemid=%s''' % itemid
# # 43740
# # 34978
#     result = pd.read_sql(sql, db)
#     result['Datetime'] = pd.to_datetime(result['clock'], unit='s')
#
#     result.to_csv('/tmp/result.csv')
#
#     time_step = 24
#     time_ser = 12
#     ratio = 0.7
#
#
#     for h_shift in range(time_ser, time_ser + time_step):
#         result['target_' + str(h_shift)] = result["value_avg"].shift(h_shift)
#
#     result = result.dropna().reset_index(drop=True)
#     result['Hour'] = result['Datetime'].dt.hour
#     trainCol = list(result.columns.values)
#     trainCol.remove("itemid")
#     trainCol.remove("clock")
#     trainCol.remove("value_min")
#     trainCol.remove("value_max")
#     trainCol.remove("value_avg")
#     trainCol.remove("num")
#     trainCol.remove("Datetime")
#
#     dataX = result[trainCol].values
#     datay = result["value_avg"].values
#     size = len(result)
#
#     modelType = 1
#
#     if modelType == 1:
#         dataX = dataX.reshape(size, time_step+1, 1)
#         datay = np.array(datay).reshape(len(datay),1)
#
#     # if modelType == 2:
#     #     pass
#
#     trainX = dataX[0:int(size*ratio)]
#     trainy = datay[0:int(size*ratio)]
#     testX = dataX[int(size*ratio):]
#     testy = datay[int(size*ratio):]
#
#     if modelType == 1:
#         model = modelLSTM(trainX, trainy, time_step)
#     if modelType == 2:
#         model = modelXGB(trainX, trainy)
#
#     predicted = model.predict(testX)
#
#     # for i in range(size-time_step-1):
#     #     x = X[i:i+time_step]
#     #     y = X[i+time_step+time_ser]
#     #     dataX.append(x.tolist())
#     #     datay.append(y.tolist())
#
#     plt.figure()
#     plt.plot(predicted, color='r', label='predicted_data')
#     plt.plot(testy, color='b', label='real_data')
#     plt.legend()
#     plt.show()
#     plt.savefig("kk.png")
