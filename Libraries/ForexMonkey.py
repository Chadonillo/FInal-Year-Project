##Import libraries
import pandas as pd
import talib
import os
from pathlib import Path


class Data:
    def __init__(self):
        self.rawTickData = {}
        self.mt5Path = str(Path.home())+"\AppData\Roaming\MetaQuotes\Terminal\Common\Files\\"
    
    def getDataCSV(self, ForexPair, timeFrame, volume_in=False, tickData = False): #TF is either 1H or 1M
        path = 'Data/'
        if tickData: path +='Tick/'
        else: path +='Minute/'
            
        if ForexPair not in self.rawTickData.keys():
            data = pd.read_csv(path+ForexPair+'.csv', index_col=['DateTime'], parse_dates=['DateTime']) 
            self.rawTickData[ForexPair] = data
        else:
            data = self.rawTickData[ForexPair]

        ##Resample data
        if tickData:
            data = data.resample(timeFrame).agg({'Bid': 'ohlc', 'Volume': 'sum'})
            data.columns = data.columns.droplevel()
            data.columns= data.columns.str.lower()
        else:
            data.columns= data.columns.str.lower()
            data = data.resample(timeFrame).agg({'open': 'first','high': 'max','low': 'min',
                                                 'close': 'last', 'volume': 'sum'})
        data = data.dropna()
        ## Rename Columns
        if volume_in==False:
            data = data.loc[:,['open','high', 'low', 'close']]
        return data
      
    def getBackTestData(self, ForexPair, volume_in=False):
        csvFileName = 'BackTestData.csv'
        path = self.mt5Path + 'BackTestData.csv'
        try:
            if os.path.exists(path):
                data = pd.read_csv(path, sep='\t', encoding='utf-16', index_col=['DateTime'], parse_dates=['DateTime'])
                return data
        except:
            pass
        return pd.DataFrame([])
        
    
    def BBANDS(self, data, value=5, deviation=2):
        n = ['BBANDS UB '+str(value)+'_'+str(deviation), 'BBANDS '+str(value)+'_'+str(deviation), 'BBANDS Lb '+str(value)+'_'+str(deviation)]
        data[n[0]], data[n[1]], data[n[2]] = talib.BBANDS(data.close.values, timeperiod=value, nbdevup=deviation, nbdevdn=deviation, matype=0)
    
    def DEMA(self, data, value=14):
        data['DEMA '+str(value)] = talib.DEMA(data.close.values, timeperiod=value)
    
    def EMA(self, data, value=14):
        data['EMA '+str(value)] = talib.EMA(data.close.values, timeperiod=value)
    
    def HT_TRENDLINE(self, data, value=14):
        data['HT_TRENDLINE'] = talib.HT_TRENDLINE(data.close.values)
        
    def KAMA(self, data, value=14):
        data['KAMA '+str(value)] = talib.KAMA(data.close.values, timeperiod=value)
        
    def MAMA(self, data, fast=0.5, slow=0.05):
        n = ['MAMA '+str(fast)+'_'+str(slow), 'FAMA '+str(fast)+'_'+str(slow)]
        data[n[0]], data[n[1]] = talib.MAMA(data.close.values, fastlimit=fast, slowlimit=slow)
        
    def SAR (self, data, step=0.02, maximum=0.2):
        data['SAR '+str(step)+'_'+str(maximum)] = talib.SAR(data.high.values, data.low.values, acceleration=step, maximum=maximum)
    
    def SMA(self, data, value=14):
        data['SMA '+str(value)] = talib.SMA(data.close.values, timeperiod=value)
    
    def TEMA(self, data, value=14):
        data['TEMA '+str(value)] = talib.TEMA(data.close.values, timeperiod=value)
    
    def TRIMA(self, data, value=14):
        data['TRIMA '+str(value)] = talib.TRIMA(data.close.values, timeperiod=value)
    
    def WMA(self, data, value=14):
        data['WMA '+str(value)] = talib.WMA(data.close.values, timeperiod=value)
    
    def ADXR(self, data, value=14):
         data['ADXR '+str(value)] = talib.ADXR(data.high.values, data.low.values, data.close.values, timeperiod=value)
            
    def APO(self, data, fast=12, slow=26):
        data['APO '+str(fast)+'_'+str(slow)] = talib.APO(data.close.values, fastperiod=fast, slowperiod=slow, matype=0)   
    
    def AROONOSC(self, data, value=14):
        data['AROONOSC '+str(value)] = talib.AROONOSC(data.high.values, data.low.values, timeperiod=value)
    
    def BOP(self, data):
        data['BOP'] = talib.BOP(data.open.values, data.high.values, data.low.values, data.close.values)
        
    def CCI(self, data, value=14):
        data['CCI '+str(value)] = talib.CCI(data.high.values, data.low.values, data.close.values, timeperiod=value)
    
    def CMO(self, data, value=14):
        data['CMO '+str(value)] = talib.CMO(data.close.values, timeperiod=value)
        
    def DX(self, data, value=14):
         data['DX '+str(value)] = talib.DX(data.high.values, data.low.values, data.close.values, timeperiod=value)
    
    def MACD(self, data, fast=12, slow=26, signal=9):
        a = str(fast)+'_'+str(slow)+'_'+str(signal)
        n = ['MACD '+a, 'MACD Signal '+a, 'MACD Hist'+a]
        data[n[0]], data[n[1]], data[n[2]] = talib.MACD(data.close.values, fastperiod=fast, slowperiod=slow, signalperiod=signal)
    
    def MINUS_DI(self, data, value=14):
        data['MINUS_DI '+str(value)] = talib.MINUS_DI(data.high.values, data.low.values, data.close.values, timeperiod=value)
        
    def MINUS_DM(self, data, value=14):
        data['MINUS_DM '+str(value)] = talib.MINUS_DM(data.high.values, data.low.values, timeperiod=value)
    
    def MOM(self, data, value=10):
        data['MOM '+str(value)] = talib.MOM(data.close.values, timeperiod=value)
    
    def PLUS_DI(self, data, value=14):
        data['PLUS_DI '+str(value)] = talib.PLUS_DI(data.high.values, data.low.values, data.close.values, timeperiod=value)
        
    def PLUS_DM(self, data, value=14):
        data['PLUS_DM '+str(value)] = talib.PLUS_DM(data.high.values, data.low.values, timeperiod=value)
        
    def PPO(self, data, fast=12, slow=26):
        data['PPO '+str(fast)+'_'+str(slow)] = talib.PPO(data.close.values, fastperiod=fast, slowperiod=slow, matype=0)   
    
    def ROC(self, data, value=1):
        data['ROC '+str(value)] = talib.ROC(data.close.values, value)
        
    def RSI(self, data, value=14):
        data['RSI '+str(value)] = talib.RSI(data.close.values, value)
    
    def STOCH(self, data, fastk=5, slowk=3, slowd=3):
        n = ['Slow_K', 'Slow_D']
        data[n[0]], data[n[1]] = talib.STOCH(data.high.values, data.low.values, data.close.values, fastk_period=fastk, slowk_period=slowk, slowk_matype=0, slowd_period=slowd, slowd_matype=0)
    
    def STOCHRSI(self, data, value=14, fastk=5, fastd=3):
        n = ['Fast_K', 'Fast_D']
        data[n[0]], data[n[1]] = talib.STOCHRSI(data.close.values, timeperiod=value, fastk_period=fastk, fastd_period=fastd, fastd_matype=0)
    
    def ULTOSC(self, data, value1=7, value2=14, value3=28):
        a = str(value1)+'_'+str(value2)+'_'+str(value3)
        data['ULTOSC '+a] = talib.ULTOSC(data.high.values, data.low.values, data.close.values, timeperiod1=value1, timeperiod2=value2, timeperiod3=value3)
        
    def WILLR(self, data, value=14):
        data['WILLR '+str(value)] = talib.WILLR(data.high.values, data.low.values, data.close.values, timeperiod=value)
