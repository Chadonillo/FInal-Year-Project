# import libraries
import Libraries.ForexMonkey as fm
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from pickle import dump, load
import pandas as pd
import random, math, os
    
class DataHandler:
    def __init__(self, isMT5=False, isTickData=False, verbose=1):
        """
            This class handles all the data manipulation and file manipulation
            It is used for adding technical indicators to data which are the features of the NN
            It also has helper functions used in running the ConnectMT5 class.
        """
        self.verbose = verbose          # if verbose is true then it will print while executing
        self.dataMonkey = fm.Data()     # Forex monkey class has useful lower level functions
        self.isMT5 = isMT5              # is it an mt5 connection or training the models from csv 
        self.isTickData = isTickData    # is the data required tickdata
    
    ########################################################
    #### HELPER FUNCTION USED FOR PYTHON-MT5 CONNECTION ####
    ########################################################
    def createFileFolder(self):
        """
            Creates shared folder if it does not already exists.
        """
        try:
            directory =self.dataMonkey.mt5Path
            if not os.path.exists(directory):
                os.makedirs(directory)
        except OSError:
            print ('Error: Creating directory. ' +  directory)

    def isMT5installed(self):
        """
            Checks if MT5 has been installed by checking that installation folder exists
        """
        a = self.dataMonkey.mt5Path
        path = a[:a[:a.rfind("\\")].rfind("\\")]
        return os.path.exists(path)

    def getMT5DataPath(self):
        """
            Returns the path of data file.

            Returns: 
                path (str): path to file
        """
        path = self.dataMonkey.mt5Path + 'BackTestData.csv'
        return path
    
    def getWriteStrategyPath(self):
        """
            Returns the path of file that the NN writes its predictions.

            Returns: 
                path (str): path to file
        """
        path = self.dataMonkey.mt5Path + 'Strat.txt'
        return path

    def getDonePath(self):
        """
            Returns the path of done file which lets us know when the MT5 EA is Done.

            Returns: 
                path (str): path to file
        """
        path = self.dataMonkey.mt5Path +'Done.txt'
        return path

    def getReadyPath(self):
        """
            Returns the path of done file which lets us know when the Python Code is Ready to connect.

            Returns: 
                path (str): path to file
        """
        path = self.dataMonkey.mt5Path +'Ready.txt'
        return path

    def isBacktestDone(self):
        """
            This function tells us if the MT5 EA is done running backtest,
            it does this by checking if there is a done file with the number 1.
            if not then its not done

            Returns: 
                (bool): True if backtesting is done, false other wise.
        """
        pathFile = self.getDonePath()
        if os.path.exists(pathFile):
            file1 = open(pathFile,"r")
            read = file1.read()
            if int(read) == 1: return True
        return False

    #####################################################
    #### FUNCTIONS FOR GETTING AND MANIPULATING DATA ####
    #####################################################
    def getFullData(self, market, timeFrame=None):
        """
            Returns the data from either csv file or mt5 and formates it in a
            pandas data frame.
            If it is tick data then it will also need to resample it with open
            high low close values

            Parameters:
                market (str): The currency pair you are trying to read.
                timeFrame (str): The time frame you want to resample your data to.

            Returns: 
                Stockdata (DataFrame): a pandas data frame with the currency pair raw data.
        """
        if self.verbose:
            print("Getting Data.")

        if self.isMT5: StockData = self.dataMonkey.getBackTestData(market)
        else: StockData=self.dataMonkey.getDataCSV(market, timeFrame, False, self.isTickData)

        if self.verbose:
            print("Number of data points:", len(StockData))
        return StockData

    def addAllIndicators(self, StockData):
        """
            This function adds a variety of technical indicators to the data using the
            ForexMonkey Library.
            Parameters:
                StockData (DataFrame): The raw data frame you want to add indicators to.
            Returns:
                StockData (DataFrame): The dataframe with indicators included.
        """
        if self.verbose:
            print("Adding Indicators.")

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

        self.dataMonkey.HT_DCPERIOD(StockData)
        self.dataMonkey.HT_DCPHASE(StockData)
        self.dataMonkey.HT_PHASOR(StockData)
        self.dataMonkey.HT_SINE(StockData)
        self.dataMonkey.HT_TRENDMODE(StockData)
        self.dataMonkey.ATRLabel(StockData)

        self.dataMonkey.candlePatterns(StockData)
        
        ##Get rid of rows that have empty cells 
        StockData.dropna(inplace = True)

    def addLabels(self, df, maxTradeCandles):
        if self.verbose:
            print("Adding Labels.")
        df["Buy_SL"] = df["close"] - df["ATR Label"]*2
        df["Buy_TP"] = df["close"] + df["ATR Label"]*3
        df["Sell_SL"] = df["close"] + df["ATR Label"]*2
        df["Sell_TP"] = df["close"] - df["ATR Label"]*3

        dfLen = len(df)
        labels = []
        acc_dir = []
        highVal = df.high.values
        lowVal = df.low.values
        closeVal = df.close.values
        buySlVal = df["Buy_SL"].values
        sellSlVal = df["Sell_SL"].values
        buyTpVal = df["Buy_TP"].values
        sellTpVal = df["Sell_TP"].values
        for currentCandle in range(dfLen):
            direction = 2
            accDirection = 2
            buySlHit = False
            sellSlHit = False
            for forwardCandle in range(min(currentCandle+1, dfLen-1), min(currentCandle+maxTradeCandles+1, dfLen-1)):
                # Do not take consecutive trades
                if labels[-maxTradeCandles:].count(0) > 0 or labels[-maxTradeCandles:].count(1) > 0:
                    break
                # Both SL have been hit so no valid trade
                if buySlHit and sellSlHit:
                    break
                # Buy SL Hit
                if lowVal[forwardCandle] <= buySlVal[currentCandle]:
                    buySlHit = True
                # Sell SL Hit
                if highVal[forwardCandle] >= sellSlVal[currentCandle]:
                    sellSlHit = True
                # Buy TP Hit
                if highVal[forwardCandle] >= buyTpVal[currentCandle] and not buySlHit:
                    direction = 1
                    break
                # Sell TP Hit
                if lowVal[forwardCandle] <= sellTpVal[currentCandle] and not sellSlHit:
                    direction = 0
                    break

            
            if direction==2:
                futureCandle = currentCandle+maxTradeCandles
                if futureCandle<dfLen:
                    if closeVal[futureCandle] > closeVal[currentCandle]:
                        accDirection = 1
                    elif closeVal[futureCandle] < closeVal[currentCandle]:
                        accDirection = 0
            else:
                accDirection = direction     
            labels.append(direction)
            acc_dir.append(accDirection)


        df.drop(columns=['Buy_SL', 'Buy_TP', 'Sell_SL', 'Sell_TP'], inplace=True)
        df["Actual Direction"] = acc_dir
        df["Direction"] = labels

    def featureSelection(self, df):
        dropCols = ['HT_TRENDMODE', 'open', 'high', 'low', 'BBANDS 5_2', 'close', 'DEMA 14', 'TEMA 14',
                    'BBANDS UB 5_2', 'EMA 14', 'WMA 14', 'BBANDS Lb 5_2', 'TRIMA 14', 'SMA 14', 'MAMA 0.5_0.05',
                    'FAMA 0.5_0.05', 'KAMA 14', 'SAR 0.02_0.2', 'Fast_K']
        df.drop(columns=dropCols, inplace=True)

    def printDirectionAmount(self, stockData):
        """
            Simply prints out the amount of buys, sells and holds in the data set.

            Parameters:
                StockData (DataFrame): The data frame with labels.
        """
        counts = stockData['Direction'].value_counts().to_dict()

        print("Hold Trades: ",counts[2])
        print("Call Trades: ",counts[1])
        print("Put Trades:  ",counts[0])
    
    def splitDataFrame(self, StockData, splitNo):
        if self.verbose:
            print("Splitting Training And Testing Data")

        #split df to test and train data
        times = sorted(StockData.index.values)
        testDays = times[-int(splitNo*len(times))]

        validation_df=StockData[(StockData.index>=testDays)]
        main_df=StockData[(StockData.index<testDays)]
        return main_df, validation_df
    
    def preprocess_df(self, df, pair, timeFrame, lookBack=None, isBool=False, raw=True):
        if lookBack==None:
            scaler = load(open('Scalers/'+pair+'_'+timeFrame+'.pkl', 'rb'))
            x = scaler.transform(df.values)
            return x

        if self.verbose:
            print("Preprocessing your pandas dataframe:")
            print("\tReshapping Data To Numpy Arrays For Model.")
            print("\tScaling dataset.")
        scaler = MinMaxScaler()
        x_data = scaler.fit_transform(df[df.columns[:-2]].values)
        y_data = df[df.columns[-1]].values
        acc_dir = df[df.columns[-2]].values
        dump(scaler, open('Scalers/'+pair+'_'+timeFrame+'.pkl', 'wb'))
        
        if self.verbose:
            print("\tAdding LSTM look back period.")
        sequential_data = []
        dataLen = x_data.shape[0]
        # Loop of the entire data set
        for i in range(dataLen):
            end_ix = i + lookBack
            if end_ix >= dataLen:
                break
            # Append the list with sequencies
            sequential_data.append([x_data[i:end_ix], acc_dir[end_ix], y_data[end_ix]])
        
        
        if self.verbose:
            print("\tOversampling to balance dataset.")
        calls = []
        puts = []
        holds = []
        
        for seq, acc_dir, target in sequential_data:
            if target==1:
                calls.append([seq, acc_dir, target])
            elif target==0:
                puts.append([seq, acc_dir, target])
            elif target==2 and not isBool:
                holds.append([seq, acc_dir, target])
        
        random.shuffle(calls)
        random.shuffle(puts)
        if not isBool:
            random.shuffle(holds)
        
        if not isBool:
            high = max(len(calls), len(puts), len(holds))
        else:
            high = max(len(calls), len(puts))

        if not raw:
            calls = calls*(math.ceil(high/len(calls)))
            puts = puts*(math.ceil(high/len(puts)))
            if not isBool:
                holds = holds*(math.ceil(high/len(holds)))

            calls = calls[:high]
            puts = puts[:high]
            if not isBool:
                holds = holds[:high]
        
        if self.verbose:
            print("\tSaving to numpy arrays. (RAM Intensive)")
        
        if not isBool:
            sequential_data = calls+puts+holds
        else:
            sequential_data = calls+puts
        random.shuffle(sequential_data)
    
        x = []
        y = []
        acc_dirRet = []
        for seq, acc_dir, target in sequential_data:
            x.append(seq)
            acc_dirRet.append(acc_dir)
            y.append(target)

        return np.array(x, dtype=np.float64), np.array(y, dtype=np.uint8), np.array(acc_dirRet, dtype=np.uint8)
    
    def oneHotEncode(self, a):
        """
            Turns a array of labels into a one hot encoded format

            Parameters:
                a (array): array of labels to be encoded
            
            Returns:
                b (array): one hot encoded array of labels
        """
        b = np.zeros((a.size, a.max()+1))
        b[np.arange(a.size),a] = 1
        return b
    
    def getLabelWeights(self, y_val):
        class_weights = {}
        unique, counts = np.unique(y_val, return_counts=True, axis=0)
        factor = 0
        for count in counts:
            factor += (1/count)
        for i in range(len(unique)):
            class_weights[unique[i]] = 1/(factor*counts[i])

        return class_weights