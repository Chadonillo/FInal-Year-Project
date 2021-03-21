# import libraries
import Libraries.ForexMonkey as fm
import numpy as np
from pandas import DataFrame
from sklearn.model_selection import train_test_split
from scipy.signal import argrelextrema
from sklearn.preprocessing import MinMaxScaler
from pickle import dump, load
import os
    
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
            print("Getting Data. This can take up to time on first run.")

        if self.isMT5: StockData = self.dataMonkey.getBackTestData(market)
        else: StockData=self.dataMonkey.getDataCSV(market, timeFrame, False, self.isTickData)

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
        """
            This class adds labels to the inputs (add more explanantion)
        """
        finalArray = np.full(len(df), 2)
        call_Positions = argrelextrema(df.close.values, np.less_equal, order=n)[0]
        put_Positions = argrelextrema(df.close.values, np.greater_equal, order=n)[0]
        for call_Position in call_Positions:
            finalArray[call_Position] = 1
        for put_Position in put_Positions:
            finalArray[put_Position] = 0
        return finalArray

    def addAllTheLabels(self, StockData, n=0):
        """
            This class adds labels to the inputs (add more explanantion)
        """
        if self.verbose:
            print("Adding Labels.")
            
        new_col = self.classifytest(StockData, n)
        StockData.insert(loc=len(StockData.columns), column='Direction', value=new_col)
        return StockData
    
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
    
    def splitDataFrame(self, X, y, testSplit):
        """
            Splits the data set into training and testing dataset for both features and labels.

            Parameters:
                X (array): The features of the data.
                y (array): The labels of the data set.
                testSplit (float): The amount of data you want as training set between 0-1.
        
        """
        return train_test_split(X, y, test_size=testSplit, shuffle=False)
    
    def preprocess_df(self, df, pair, timeFrame, live=False):
        """
            Turns data frame into a two scaled numpy arrays. 
            One array is the features and the other is the labels.

            They are scaled to make learning more efficient for the NN

            Parameters:
                df (DataFrame): the data frame you want to transform
                pair (str): the currency pair of the data
                timeFrame (str): the time frame of the data
                live (bool): if data is live then we only need X values.

                Returns:
                    x (array): features of the data frame
                    y (array): labels of the data set
        """
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
    
    def reshapeData(self, x, y = None, oneHot = True, live=False):
        """
            Reshapes the X and Y data to fit into the NN properly

            Parameters:
                X (array): The features of the data.
                y (array): The labels of the data set.
                oneHot (bool): true if you want one hot encoded y values
                live (bool): If live is true the return only X values

            Return:
                x (array): reshaped array of features
                y (array): reshaped array of labels
        """
        if live:
            x = x.reshape(x.shape[0], x.shape[1], 1)
            return x
        x = x.reshape(x.shape[0], x.shape[1], 1)
        y = y.reshape(y.shape[0])

        if oneHot:
            y = self.oneHotEncode(y)

        return x, y
    
