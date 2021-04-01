#import libraries
import numpy as np
from numpy import set_printoptions
##Costume Library to manipulate data and add indicators
from Libraries.Utils import DataHandler
import pandas as pd
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.utils import class_weight


# import warnings filter
from warnings import simplefilter
# ignore all future warnings
simplefilter(action='ignore', category=FutureWarning)

class FS:
    def __init__(self, timeFrame, pair):
        self.dataHandler = DataHandler()
        ##Settings
        self.timeFrame = timeFrame
        self.pair = pair
        self.trade_length = 3
    
    def collectForexData(self):
        df = self.dataHandler.getFullData(self.pair, self.timeFrame)
        self.dataHandler.addAllIndicators(df)
        self.dataHandler.addLabels(df, self.trade_length)
        self.dataHandler.printDirectionAmount(df)
        return df
    
    def getFeatureScore(self, df):
        x = df[df.columns[:-2]].values
        y = df[df.columns[-1:]].values
        y = y.reshape(y.shape[0])

        fNames = df.columns[:-1].values.astype('U')
        class_weights = dict(zip([0,1,2], class_weight.compute_class_weight('balanced', np.unique(y), y)))

        print("Running Extra Tree Classifier... (can take some time)")
        set_printoptions(precision=6, suppress=True)
        model = ExtraTreesClassifier(class_weight=class_weights)
        model.fit(x, y)
        scores = model.feature_importances_
        featureScoresTrees = {A: B for A, B in zip(fNames, scores)}
        featureScoresTrees = {k: v for k, v in sorted(featureScoresTrees.items(), key=lambda item: item[1], reverse=True)}
        dfScores = pd.DataFrame(list(featureScoresTrees.items()), columns=["Indicator", "Score"])
        dfScores.set_index('Indicator', inplace=True)

        return dfScores

if __name__ == "__main__":
    featureSelection = FS("5Min", "GBPUSD")
    stockData = featureSelection.collectForexData()
    scores = featureSelection.getFeatureScore(stockData)
    print(scores)