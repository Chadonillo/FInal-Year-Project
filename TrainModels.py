#import libraries
import numpy as np
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # or any {'0', '1', '2'}

##Costume Library to manipulate data and add indicators
from Libraries.Utils import DataHandler
from Libraries.KerasCustom import *

##Artificial Intelligence Library
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, LSTM, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint, ReduceLROnPlateau
from tensorflow.keras.backend import clear_session
import tensorflow as tf


class ForexModels:
    def __init__(self, pair, timeFrame):
        self.dataHandler = DataHandler()
        # Settings
        self.timeFrame = timeFrame
        self.pair = pair          #['GBPUSD','EURUSD','USDCHF','USDJPY']

        self.trade_length = 3
        self.look_back = 96

        self.batch_size = 64
        self.testSplitPCT = 0
        self.epochs = 10

        self.loadModel = False

    def countUnique(self, a, oneHot = True):
        retStr = ""
        unique, counts = np.unique(a, return_counts=True, axis=0)
        for i in range(len(unique)):
            if oneHot:
                retStr += str(np.argmax(unique[i])) +": "+str(counts[i])+ ", "
            else:
                retStr += str(unique[i]) +": "+str(counts[i])+ ", "
        return retStr[:-2]

    def createAIModel(self):
        print("Creating AI Model")
        #Create model structure 
        clear_session()
        #Create sequential model
        model = Sequential()

        #Add layers to model
        model.add(LSTM(100, input_shape=(X_train.shape[1:]), return_sequences=True ))
        model.add(Dropout(0.1))
        model.add(LSTM(30))
        model.add(Dropout(0.1))
        model.add(Dense(3, activation = "softmax"))
        return model

    def compileAndOptimizeModel(self, model, dir_train, dir_test):
        print("Optimize And Compile Model")
        #Optimize (set learning rate) and complie model 
        optimizer= Adam(lr=0.001)
        model.compile(loss='categorical_crossentropy', optimizer=optimizer, metrics=[winMetric(dir_train, dir_test, 0), TradeFrequency(dir_train, dir_test, 0)])
        return model
    
    def createCallBacks(self):
        print("Adding Call Backs")
        #Callback functions 
        path_checkpoint = "Models/"+self.pair+"_"+self.timeFrame+".h5"
        callback_checkpoint = ModelCheckpoint(filepath=path_checkpoint,
                                            monitor='winRatio',
                                            verbose=1,
                                            save_best_only=True,
                                            mode = "max")

        callback_early_stopping = EarlyStopping(monitor='winRatio',
                                                patience=4, verbose=1)

        callback_reduce_lr = ReduceLROnPlateau(monitor='winRatio',
                                            factor=0.1,
                                            min_lr=1e-4,
                                            patience=2,
                                            verbose=1)
        callbacks = [callback_checkpoint, callback_early_stopping, callback_reduce_lr]
        return callbacks

    def trainModel(self, model, train_x, train_y, validation_x=None, validation_y=None, callbacks=None, classWeights=None):
        # Train model
        val = (validation_x, validation_y)
        try:
            if validation_x==None:
                val = None
        except:
            pass
        history = model.fit(
            train_x, train_y,
            batch_size=self.batch_size,
            epochs=self.epochs,
            validation_data=val,
            callbacks=callbacks,
            class_weight = classWeights
        )
        return history, model

    def collectData(self):
        # Get Data And Add Labels
        stockData = self.dataHandler.getFullData(self.pair, self.timeFrame)
        self.dataHandler.addAllIndicators(stockData)
        self.dataHandler.addLabels(stockData, self.trade_length)
        self.dataHandler.featureSelection(stockData)
        self.dataHandler.printDirectionAmount(stockData)

        # Process Data
        if self.testSplitPCT>0:
            df_train, df_test = self.dataHandler.splitDataFrame(stockData, self.testSplitPCT)
            print("Train Start:", df_train.index[0], "Train End:", df_train.index[-1])
            print("Test Start:", df_test.index[0], "Test End:", df_test.index[-1])
            print()
            X_train, y_train, acc_dir_train =  self.dataHandler.preprocess_df(df_train, self.pair, self.timeFrame, self.look_back)
            X_test, y_test, acc_dir_test = self.dataHandler.preprocess_df(df_test, self.pair, self.timeFrame, self.look_back)
            classWeights = self.dataHandler.getLabelWeights(y_train)
            y_train = self.dataHandler.oneHotEncode(y_train)
            y_test = self.dataHandler.oneHotEncode(y_test)
            print()
            print("Class Weights:", classWeights)
            print("X_train:", X_train.shape, " y_train:", y_train.shape, " Class distribution:" , self.countUnique(y_train))
            print("X_test:", X_test.shape, " y_test:", y_test.shape, " Class distribution:" , self.countUnique(y_test))
            
        else:
            df_train = stockData
            print("Train Start:", df_train.index[0], "Train End:", df_train.index[-1])
            print()
            X_train, y_train, acc_dir_train =  self.dataHandler.preprocess_df(df_train, self.pair, self.timeFrame, self.look_back)
            X_test, y_test, acc_dir_test = None, None, None
            classWeights = self.dataHandler.getLabelWeights(y_train)
            y_train = self.dataHandler.oneHotEncode(y_train)
            y_test = None
            print()
            print("Class Weights:", classWeights)
            print("X_train:", X_train.shape, " y_train:", y_train.shape, " Class distribution:" , self.countUnique(y_train))
        
        return X_train, y_train, acc_dir_train, X_test, y_test, acc_dir_test, classWeights

    def runModel(self, X_train, y_train, acc_dir_train, X_test, y_test, acc_dir_test, classWeights):
        # Run Model
        if self.loadModel:
            model = load_model("Models/"+self.pair+"_"+self.timeFrame+".h5", 
                                custom_objects={'winRatio': winMetric(acc_dir_train, acc_dir_test), 'NoTradesInBatch':  TradeFrequency(acc_dir_train, acc_dir_test)})
            modelcallbacks = self.createCallBacks()
            hist, model = self.trainModel(model, X_train, y_train, X_test, y_test, modelcallbacks, classWeights)

        else:
            #SetUp AI Model
            model = self.createAIModel()
            model = self.compileAndOptimizeModel(model, acc_dir_train, acc_dir_test)
            modelcallbacks = self.createCallBacks()

            #Train Model
            hist, model = self.trainModel(model, X_train, y_train, X_test, y_test, modelcallbacks, classWeights)


def assignGPU():
    physical_devices = tf.config.experimental.list_physical_devices('GPU')
    for i in range(len(physical_devices)):
        tf.config.experimental.set_memory_growth(physical_devices[i], True)

if __name__ == "__main__":
    assignGPU()
    forex = ForexModels('GBPUSD', '1H')
    X_train, y_train, acc_dir_train, X_test, y_test, acc_dir_test, classWeights = forex.collectData()
    forex.runModel(X_train, y_train, acc_dir_train, X_test, y_test, acc_dir_test, classWeights)