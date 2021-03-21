# Import libraries
from Libraries.Utils import DataHandler
import tensorflow as tf
from tensorflow.keras.models import load_model
import random, os
import pandas as pd

# Check if you have any number of GPUs to run the model calculations 
physical_devices = tf.config.experimental.list_physical_devices('GPU')
for i in range(len(physical_devices)):
    tf.config.experimental.set_memory_growth(physical_devices[i], True)

class StrategyConnectMT5:
    def __init__(self, pair, tf):
        """ 
            This class connects the Python Code to the MT5 Expert Advisor
            It takes the desire pair and time frame and loads the model for that.
            It also initializes the DataHandler Class which has a lot of useful
            functions for implimenting the connection of python and mt5.

            This connection is achieved using multiple shared files system.
            Some files act as data busses, some files can also act as control busses.

            Parameters:
                pair (str): the currency pair you want to trade
                tf (str): the time framea you want to trade on
        """
        self.dataHandler = DataHandler(isMT5=True, verbose=0)
        self.pair = pair
        self.timeFrame = tf
        self.model = load_model("Models/"+self.pair+"_"+self.timeFrame+".h5")
        self.oldStockData = None
        self.stockData = None
    
    def getPrediction(self, stockData):
        """
            Returns model prediction
        """
        return str(random.choices([0,1,2], weights=[0.1, 0.1, 0.9])[0])
    
    def writeTradeToFile(self, direction):
        """
            Write the desired trade to the trade file so it can be ready 
            by companion Expert Advisor on the MT5 platform and executed 
            appropriately.

            Parameters:
                direction (int): 0, 1 or 2 representing the trading direction Up, Down or Hold. 
        """
        path = self.dataHandler.getWriteStrategyPath()  # Gets the path of the write file
        file1 = open(path,"a")  
        file1.write(direction+"\n")
        file1.close()

    def isReady(self):
        """
            This creates the shared files and signifies to the EA that 
            the python code is ready to trade.
        """
        pathReady = self.dataHandler.getReadyPath()             # Shared file path
        stratPath = self.dataHandler.getWriteStrategyPath()     # Shared file path
        paths = [stratPath, pathReady]

        for path in paths:  # Create files
            file1 = open(path,"w+")
            file1.close()

        donepath = self.dataHandler.getDonePath()
        if os.path.exists(donepath): os.remove(donepath)

    def notReady(self):
        """
            This deletes some of the shared files and signifies to the EA that 
            the python code is not ready to trade.
        """
        pathReady = self.dataHandler.getReadyPath()             # Shared file path
        stratPath = self.dataHandler.getWriteStrategyPath()     # Shared file path
        paths = [stratPath, pathReady]

        for path in paths:      # Deletes files
            if os.path.exists(path): os.remove(path)

    def reset(self):
        """
            Deletes all the files, both the control (signal) files and the data files.
            reset at the beggining and end of a run ensure we do not encounter any
            file issues.
        """
        dataPath = self.dataHandler.getMT5DataPath()
        donePath = self.dataHandler.getDonePath()
        stratPath = self.dataHandler.getWriteStrategyPath()
        pathReady = self.dataHandler.getReadyPath()
        paths = [pathReady, dataPath, donePath, stratPath]

        for path in paths:
            try:
                if os.path.exists(path): os.remove(path)
            except:
                print(path)

    def isThreadRunning(self, thread):
        """
            checks if a thread is currently running.

            Parameters:
                thread : The thread class to check status

            Returns:
                (bool): True if its is running and False if it is not running
        """
        if thread != None:
            return thread.running
        return True

    def run(self, thread = None):
        """
            The run function combines all of these previous functions.
            It first resets the shared files then starts a loop that is only
            broken if the EA is removed from the MT5 chart, if the EA completes
            it's backtesting or the thread was stopped from running.

            Parameters:
                thread: This function can be run in a thread, this is the thread it will run in.
        """
        if self.dataHandler.isMT5installed():
            self.dataHandler.createFileFolder()
        else:
            return False

        self.reset()                                                # Reset files
        done = self.dataHandler.isBacktestDone()                    # Get done status of EA
        self.stockData = self.dataHandler.getFullData(self.pair)    # Get the stock data if it is available in shared files
        self.oldStockData = self.stockData                          # Save previous data
        self.isReady()                                              # Signal to EA that the python code is ready
        threadRunning = self.isThreadRunning(thread)                # Check if the thread is still running

        while not done and threadRunning:                           # While EA is not done backtesting and thread is still running
            self.stockData = self.dataHandler.getFullData(self.pair)# Get currency data from mt5
            done = self.dataHandler.isBacktestDone()                # Check if EA is done backtesting
            threadRunning = self.isThreadRunning(thread)            # Check if thread is still running

            if not self.stockData.equals(self.oldStockData):        # If the new data has changed from what it used to be then trade
                self.oldStockData = self.stockData                  # Set old data to new data
                direction = self.getPrediction(self.stockData)      # Get AI prediction
                self.writeTradeToFile(direction)                    # send prediction to MT5 EA

        self.reset() # Reset files
        return True