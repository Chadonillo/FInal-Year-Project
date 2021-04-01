##Import libraries
import pandas as pd
import talib
import os
from pathlib import Path
from itertools import compress
from Libraries.CandleRanking import candle_rankings
import numpy as np

class Data:
    def __init__(self):
        self.rawTickData = {}
        self.mt5Path = str(Path.home())+"\AppData\Roaming\MetaQuotes\Terminal\Common\Files\\"
    
    def getDataCSV(self, ForexPair, timeFrame, volume_in=False, tickData = False): #TF is either 1H or 1M
        path = '../Data/'
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
        data['HT_TRENDLINE '+str(value)] = talib.HT_TRENDLINE(data.close.values)
        
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

    def HT_DCPERIOD(self, data):
        data['HT_DCPERIOD'] = talib.HT_DCPERIOD(data.close.values)

    def HT_DCPHASE(self, data):
        data['HT_DCPHASE'] = talib.HT_DCPHASE(data.close.values)
    
    def HT_PHASOR(self, data):
        n = ['HT_PHASOR_inPhase', 'HT_PHASOR_quadrature']
        data[n[0]], data[n[1]] = talib.HT_PHASOR (data.close.values)
    
    def HT_SINE(self, data):
        n = ['HT_SINE', 'HT_SINE_lead']
        data[n[0]], data[n[1]] = talib.HT_SINE  (data.close.values)
    
    def HT_TRENDMODE(self, data):
        data['HT_TRENDMODE'] = talib.HT_TRENDMODE(data.close.values)

    def ATR(self, data, value=14):
        data['ATR '+str(value)] = talib.ATR(data.high.values, data.low.values, data.close.values, timeperiod=value)

    def ATRLabel(self, data):
        data['ATR Label'] = talib.ATR(data.high.values, data.low.values, data.close.values, timeperiod=20)

    ## This function was taken from https://github.com/CanerIrfanoglu/medium/blob/master/candle_stick_recognition/identify_candlestick.py
    ## Heavy it was also heavily modified to increase its efficiency and running time on large datasets.
    ## The previous version took 5 hours to run on 6,666,612 data points,
    ## This version takes 217 seconds to do the same thing.
    def candlePatterns(self, df):
        """
        Recognizes candlestick patterns and appends 2 additional columns to df;
        1st - Best Performance candlestick pattern matched by www.thepatternsite.com
        2nd - # of matched patterns
        """
        candle_names = talib.get_function_groups()['Pattern Recognition']

        # patterns not found in the patternsite.com
        exclude_items = ('CDLCOUNTERATTACK', 'CDLLONGLINE', 'CDLSHORTLINE', 'CDLSTALLEDPATTERN', 'CDLKICKINGBYLENGTH')
        candle_names = [candle for candle in candle_names if candle not in exclude_items]

        # create columns for each candle
        patternDF = pd.DataFrame(index=df.index)
        for candle in candle_names:
            patternDF[candle] = getattr(talib, candle)(df.open.values, df.high.values, df.low.values, df.close.values)
        
        #df['pattern_name'] = patternDF.apply (lambda row: singleColumn(row, patternDF.columns), axis=1)
        df["pattern_name_encoded"] = patternDF.apply (lambda row: singleColumn(row, patternDF.columns,True), axis=1)

def singleColumn(row, column_names, isNumber=False):
    indexesNonZeroColumns = np.flatnonzero(row.values)
    nonZeroColumns = column_names[indexesNonZeroColumns]
    if len(nonZeroColumns) == 0:
        if isNumber: return 0
        return "NO_PATTERN"
    # single pattern found
    elif len(nonZeroColumns) == 1:
        nameOfPattern = nonZeroColumns[0]
        if row[nameOfPattern] > 0:      # bull pattern 100 or 200
            if isNumber: return indexesNonZeroColumns[0]+1
            return nameOfPattern + '_Bull'
        else:                           # bear pattern -100 or -200
            if isNumber: return indexesNonZeroColumns[0]+2
            return nameOfPattern + '_Bear'

    # multiple patterns matched -- select best performance
    else:
        # filter out pattern names from bool list of values
        container = []
        containerIndex = []
        i=0
        for pattern in nonZeroColumns:
            if row[pattern] > 0:
                containerIndex.append(indexesNonZeroColumns[i]+1)
                container.append(pattern + '_Bull')
            else:
                containerIndex.append(indexesNonZeroColumns[i]+2)
                container.append(pattern + '_Bear')
            i+=1
        rank_list = [candle_rankings[p] for p in container]
        if len(rank_list) == len(container):
            rank_index_best = rank_list.index(min(rank_list))
            if isNumber: return containerIndex[rank_index_best]
            return container[rank_index_best]
    print("Failed")
    if isNumber: -1
    return 'FAILED'