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

sqlalchemyconn = create_engine('mysql+pymysql://%s:%s@%s:%s/%s' % (dbuser, dbpasswd, dbhost, dbport, dbdb),pool_size=20, max_overflow=0)
sql = '''select * from trends
            where itemid=30183'''
result = pd.read_sql(sql, db)
X = result['value_avg'].values
dataX, datay =],,# size = len(X)
time_step = 24
ratio = 0.7
lr = 0.0006
for i in range(size-time_step-1):
    x = X[i:i+time_step,#     y = X[i+time_step,#     dataX.append(x.tolist())
    datay.append(y.tolist())
dataX = np.array(dataX).reshape(len(dataX), time_step, 1)
datay = np.array(datay).reshape(len(datay),1)
trainX = dataX[0:int(size*ratio),# trainy = datay[0:int(size*ratio),# testX = dataX[int(size*ratio):,# testy = datay[int(size*ratio):,#
model = Sequential()
model.add(LSTM(200, batch_input_shape=(None, time_step, 1)))
model.add(Dense(1))
model.add(Activation("linear"))
optimizer = Adam(lr=lr)
model.compile(loss="mean_squared_error", optimizer=optimizer)
early_stopping = EarlyStopping(monitor='val_loss', mode='auto', patience=20)
model.fit(trainX, trainy, batch_size=300, epochs=100, validation_split=0.1, callbacks=[early_stopping])
predicted = model.predict(testX)

# predicted =[0.891662  ,0.8933019, 0.89795214, 0.8936984 ,0.90159744,0.8977718 ,0.90419424,0.90183467,0.85212874,0.7705383 ,0.68444294,0.6459833 ,0.6625579 ,0.6992105 ,0.7443561 ,0.7893541 ,0.8299893 ,0.8662427 ,0.89471656,0.91704404,0.93407136,0.9455268 ,0.95480716,0.9617768 ,0.96699554,0.9692212 ,0.9718188 ,0.97399133,0.9740444 ,0.97525215,0.9650322 ,0.91603416,0.85346144,0.7637882 ,0.6716738 ,0.6437498 ,0.6581894 ,0.6951244 ,0.74095553,0.7866493 ,0.82792026,0.8664616 ,0.8956368 ,0.9182112 ,0.9352721 ,0.9479656 ,0.95727456,0.9640373 ,0.9689142 ,0.97242516,0.97493726,0.9750056 ,0.97606075,0.9753807 ,0.89693034,0.79124415,0.6852666 ,0.58714724,0.5002104 ,0.42800453,0.37888083,0.37441877,0.42701936,0.5039305 ,0.58818924,0.66752326,0.7350183 ,0.7877455 ,0.8281553 ,0.8529657 ,0.8745676 ,0.895899  ,0.9140577 ,0.9208599 ,0.9223546 ,0.9243609 ,0.9248373 ,0.9252455 ,0.93245625,0.93892163,0.94668555,0.9522113 ,0.9566027 ,0.96172917,0.96627206,0.9700152 ,0.97291356,0.9752131, 0.97700477,0.98169833,0.9832587 ,0.98403037,0.9842683 ,0.98424464,0.98405206,0.9837891 ,0.98353386,0.9833489 ,0.9832009 ,0.9830702 ,0.9829762 ,0.98290634,0.94143915,0.8494325 ,0.74668777,0.64297605,0.5481481 ,0.4857732 ,0.50140995,0.55373466,0.6189082 ,0.68627447,0.74789965,0.802238  ,0.8444475 ,0.8781917 ]
# testy =[0.88, 0.9308, 0.8425, 0.9833, 0.8467, 0.9658, 0.8633, 0.3992, 0.15, 0.14  ,0.5908,0.98  ,0.9867,1.    ,1.    ,1.    ,1.0175,1.    ,1.    ,1.    ,0.9867,1.    ,1.    ,1.    ,0.9833,1.    ,1.    ,0.9833,1.    ,0.8858,0.5117,0.4275,0.1467,0.1117,0.7175,0.9275,0.9825,1.    ,1.    ,1.    ,1.035 ,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,0.9825,1.    ,0.9833,0.2008,0.0342,0.0517,0.0483,0.035 ,0.0525,0.1575,0.4875,0.9033,0.9692,1.    ,1.    ,0.9825,0.9558,0.9517,0.895 ,0.9517,1.    ,1.    ,0.9175,0.9067,0.9383,0.93  ,0.9342,1.    ,0.9825,1.    ,0.9825,0.9825,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,1.0333,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,1.    ,0.5833,0.13  ,0.0833,0.035 ,0.03  ,0.2442,0.8867,0.9833,0.9825,1.    ,1.    ,1.0158,0.9867,0.9967,0.9825]
plt.figure()
plt.plot(predicted, color='r', label='predicted_data')
plt.plot(testy, color='b', label='real_data')
plt.legend()
plt.show()
plt.savefig("kk.png")
