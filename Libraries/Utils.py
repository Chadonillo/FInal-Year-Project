import Libraries.ForexMonkey as fm
import numpy as np
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from scipy.signal import argrelextrema
from sklearn.preprocessing import MinMaxScaler
from pickle import dump, load
    
class DataHandler:
    def __init__(self, isMT5=False, isTickData=False, verbose=1):
        self.verbose = verbose
        self.dataMonkey = fm.Data()
        self.isMT5 = isMT5
        self.isTickData = isTickData
        
    def getFullData(self, market, timeFrame=None):
        if self.verbose:
            print("Getting Data. This can take up to time on first run.")

        if self.isMT5: StockData = self.dataMonkey.getBackTestData(market)
        else: StockData=self.dataMonkey.getDataCSV(market, timeFrame, False, self.isTickData)

        if not StockData.equals(DataFrame([])):
            StockData["Range"] = (StockData["high"] - StockData["low"])
            StockData=StockData.iloc[-int(len(StockData)/1):]
        return StockData
        

    def getMT5DataPath(self):
        path = self.dataMonkey.mt5Path + 'BackTestData.csv'
        return path
    
    def getWriteStrategyPath(self):
        path = self.dataMonkey.mt5Path + 'Strat.txt'
        return path

    def getDonePath(self):
        path = self.dataMonkey.mt5Path +'Done.txt'
        return path

    def getReadyPath(self):
        path = self.dataMonkey.mt5Path +'Ready.txt'
        return path

    def isBacktestDone(self):
        try:
            pathFile = self.getDonePath()
            file1 = open(pathFile,"r")
            read = file1.read()
            if int(read) == 1: return True
            else: return False
        except:
            return False
            
    def addAllIndicators(self, StockData):
        if self.verbose:
            print("Adding Indicators. This can take up to 10 minutes.")

        self.dataMonkey.BBANDS(StockData)
        self.dataMonkey.DEMA(StockData)
        self.dataMonkey.EMA(StockData)
        self.dataMonkey.KAMA(StockData)
        self.dataMonkey.MAMA(StockData)
        self.dataMonkey.SAR(StockData)
        self.dataMonkey.SMA(StockData)
        self.dataMonkey.TEMA(StockData)
        self.dataMonkey.TRIMA(StockData)
        self.dataMonkey.WMA(StockData)
        self.dataMonkey.ADXR(StockData)
        self.dataMonkey.AROONOSC(StockData)
        self.dataMonkey.BOP(StockData)
        self.dataMonkey.CCI(StockData)
        self.dataMonkey.CMO(StockData)
        self.dataMonkey.DX(StockData)
        self.dataMonkey.MACD(StockData)
        self.dataMonkey.MINUS_DI(StockData)
        self.dataMonkey.MINUS_DM(StockData)
        self.dataMonkey.MOM(StockData)
        self.dataMonkey.PLUS_DI(StockData)
        self.dataMonkey.PLUS_DM(StockData)
        self.dataMonkey.PPO(StockData)
        self.dataMonkey.ROC(StockData)
        self.dataMonkey.RSI(StockData)
        self.dataMonkey.STOCH(StockData)
        self.dataMonkey.STOCHRSI(StockData)
        self.dataMonkey.ULTOSC(StockData)
        self.dataMonkey.WILLR(StockData)
        
        ##Get rid of rows that have empty cells 
        StockData.dropna(inplace = True)

        return StockData

    def classifytest(self, df, n):
        finalArray = np.full(len(df), 2)
        call_Positions = argrelextrema(df.close.values, np.less_equal, order=n)[0]
        put_Positions = argrelextrema(df.close.values, np.greater_equal, order=n)[0]
        for call_Position in call_Positions:
            finalArray[call_Position] = 1
        for put_Position in put_Positions:
            finalArray[put_Position] = 0
        return finalArray

    def addAllTheLabels(self, StockData, n=0):
        if self.verbose:
            print("Adding Labels.")
            
        new_col = self.classifytest(StockData, n)
        StockData.insert(loc=len(StockData.columns), column='Direction', value=new_col)
        return StockData
    
    def printDirectionAmount(self, stockData):
        counts = stockData['Direction'].value_counts().to_dict()
        print("Hold Trades: ",counts[2])
        print("Call Trades: ",counts[1])
        print("Put Trades:  ",counts[0])
    
    def splitDataFrame(self, X, y, testSplit):
        return train_test_split(X, y, test_size=testSplit, shuffle=False)
    
    def preprocess_df(self, df, pair, timeFrame, live=False):
        if live:
            x = df
            scaler = load(open('Scalers/'+pair+'_'+timeFrame+'.pkl', 'rb'))
            x = scaler.transform(x)
            return x
    
        x = df[df.columns[:-1]]
        y = df[df.columns[-1:]]

        # define scaler
        scaler = MinMaxScaler()
        # fit scaler on the training dataset
        scaler.fit(x)
        # transform the training dataset
        x = scaler.transform(x)
        dump(scaler, open('Scalers/'+pair+'_'+timeFrame+'.pkl', 'wb'))
        return x, y.values
    
    def oneHotEncode(self, a):
        b = np.zeros((a.size, a.max()+1))
        b[np.arange(a.size),a] = 1
        return b
    
    def reshapeData(self, x, y = None, oneHot = True, live=False):
        if live:
            x = x.reshape(x.shape[0], x.shape[1], 1)
            return x
        x = x.reshape(x.shape[0], x.shape[1], 1)
        y = y.reshape(y.shape[0])

        if oneHot:
            y = self.oneHotEncode(y)

        return x, y
    
