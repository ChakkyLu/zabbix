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
            where itemid=34978'''
result = pd.read_sql(sql, db)
X = result['value_avg'].values
dataX, datay = [], []
size = len(X)
time_step = 24
ratio = 0.7
lr = 0.0006
for i in range(size-time_step-1):
    x = X[i:i+time_step]
    y = X[i+time_step]
    dataX.append(x.tolist())
    datay.append(y.tolist())
dataX = np.array(dataX).reshape(len(dataX), time_step, 1)
datay = np.array(datay).reshape(len(datay),1)
trainX = dataX[0:int(size*ratio)]
trainy = datay[0:int(size*ratio)]
testX = dataX[int(size*ratio):]
testy = datay[int(size*ratio):]

model = Sequential()
model.add(LSTM(200, batch_input_shape=(None, time_step, 1)))
model.add(Dense(1))
model.add(Activation("linear"))
optimizer = Adam(lr=lr)
model.compile(loss="mean_squared_error", optimizer=optimizer)
early_stopping = EarlyStopping(monitor='val_loss', mode='auto', patience=20)
model.fit(trainX, trainy, batch_size=300, epochs=self.epoch, validation_split=0.1, callbacks=[early_stopping])
predicted = model.predict(testX)

plt.figure()
plt.plot(predicted, color='r', label='predicted_data')
plt.plot(testy, color='b', label='real_data')
plt.legend()
plt.show()
