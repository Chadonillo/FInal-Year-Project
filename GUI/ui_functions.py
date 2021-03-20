# The layout of this GUI was branched from https://github.com/Wanderson-Magalhaes/Toggle_Burguer_Menu_Python_PySide2
# I have modified it to work with PyQt5 rather than PySide2.
# I have also added my own elements to the GUI.

# Import Libraries
from PyQt5.QtCore import QPropertyAnimation, QThread, QEasingCurve
from PyQt5.QtGui import QPixmap
from main import MainWindow
from Libraries.ConnectMT5 import StrategyConnectMT5 

class ThreadRunButton(QThread):
    def __init__(self, uiClass):
        """
            The thread for the main run button that connects the AI with MT5

            Parameters: 
                uiClass: the UI given so that we can change the values 
                        of certain labels depending on thread conditions.
        """
        super().__init__()
        self.uiClass = uiClass
        self.running = False

    def run(self):
        """
            Runs the connection between AI and Mt5.
            It also turns the logo green to signify 
            Connection is currently turned on in the app
        """
        self.running = True # Signify that we started running 
        setRadioButtons(self.uiClass , False)
        self.uiClass.ui.label_2.setPixmap(QPixmap("GUI\Images\logoGreen.png"))  # Turn image Green
        pairs = getSelectedPairs(self.uiClass) # Get pairs from radio buttons
        timeFrames = getSelectedTimeFrames(self.uiClass) # get timeframes form radio buttons

        mtStrategy = StrategyConnectMT5(pairs, timeFrames) # Create a connection class
        mtStrategy.run(self)    # Run connection
        self.uiClass.ui.label_2.setPixmap(QPixmap("GUI\Images\logo.png")) # When finished set image back to normal to indicate it is done.
        setRadioButtons(self.uiClass , True)
        self.running = False # Signify that thread has finished running

class UIFunctions(MainWindow):
    """
        Functions that get assigned elements in the UI.
    """
    def toggleMenu(self, maxWidth, enable):
        """
            Toggles the current sidbar with from min to max when run.
        """
        if enable:
            # GET WIDTH
            width = self.ui.frame_left_menu.width()
            maxExtend = maxWidth
            standard = 70

            # SET MAX WIDTH
            if width == 70:
                widthExtended = maxExtend
            else:
                widthExtended = standard

            # ANIMATION
            self.animation = QPropertyAnimation(self.ui.frame_left_menu, b"minimumWidth")
            self.animation.setDuration(400)
            self.animation.setStartValue(width)
            self.animation.setEndValue(widthExtended)
            self.animation.setEasingCurve(QEasingCurve.InOutQuart)
            self.animation.start()

    def pageSet(self, currPage, currButton):
        """
            Sets the current page you are viewing to blue in the side bar.

            Parameters:
                currPage: page you want to change to
                currButton: button you want to implement this change
        """
        standardStyle = """QPushButton {\n
                            color: rgb(255, 255, 255);\n
                            background-color: rgb(35, 35, 35);\n
                            border: 0px solid;\n
                        }\n
                        QPushButton:hover {\n
                            background-color: rgb(85, 170, 255);\n
                        }
                        """
        selectedStyle = """QPushButton {\n
                            color: rgb(255, 255, 255);\n
                            background-color: rgb(85, 170, 255);\n
                            border: 0px solid;\n
                        }\n
                        QPushButton:hover {\n
                            background-color: rgb(85, 170, 255);\n
                        }
                        """
        buttons = [self.ui.btn_page_1, self.ui.btn_page_2, self.ui.btn_page_3]

        self.ui.stackedWidget.setCurrentWidget(currPage)
        for button in buttons:
            if button!=currButton: button.setStyleSheet(standardStyle)
            else: button.setStyleSheet(selectedStyle)

    def run(self):
        """
            Start run thread and make stop button accessible.
        """
        if not self.threadRunButton.isRunning():
            setRadioButtons(self , False)
            self.ui.runButton.setVisible(False)
            self.ui.runButton.setEnabled(False)
            self.ui.stopButton.setVisible(True)
            self.ui.stopButton.setEnabled(True)
            self.threadRunButton.start()

    def runIsFinished(self):
        """
            This sets the enabled button back to be run once run is finished with backtest.
        """
        self.ui.runButton.setVisible(True)
        self.ui.runButton.setEnabled(True)
        self.ui.stopButton.setVisible(False)
        self.ui.stopButton.setEnabled(False)
        setRadioButtons(self , True)

    def stop(self):
        """
            Kills the thread with the run function sets the logo back to normal
        """
        self.threadRunButton.running = False
        setRadioButtons(self , True)
        self.ui.label_2.setPixmap(QPixmap("GUI\Images\logo.png"))

def getSelectedPairs(self):
    """
        Simply returns selected currency Pair
    """
    allPairCheckBox = [self.ui.GBPUSDradioButton, self.ui.AUDCADradioButton, self.ui.EURUSDradioButton, 
                        self.ui.USDCHFradioButton, self.ui.USDJPYradioButton, self.ui.USDCADradioButton]
    selectedPair = None
    for checkbox in allPairCheckBox:
        if checkbox.isChecked():
            selectedPair = checkbox.text()
            break
    return selectedPair

def getSelectedTimeFrames(self):
    """
        Simply returns selected time frame
    """
    allTfCheckBox = [self.ui.m_1radioButton, self.ui.m_5radioButton, self.ui.m_15radioButton, 
                     self.ui.m_30radioButton, self.ui.h_1radioButton, self.ui.d_1radioButton]
    transformation = {'1 Minute': "1Min", '5 Minute': "5Min", '15 Minute': "15Min", '30 Minute': "30Min", '1 Hour': "1H", '1 Day': "1D"}
    selectedTf = None
    for checkbox in allTfCheckBox:
        if checkbox.isChecked():
            selectedTf = transformation[checkbox.text()]
            break
    return selectedTf

def setRadioButtons(self, enabled = False):
    """
        Enables and disable the radio buttons

        Parameters: 
            enabled: true if radio buttons should be enabled.
    """
    allPairCheckBox = [self.ui.GBPUSDradioButton, self.ui.AUDCADradioButton, self.ui.EURUSDradioButton, 
                       self.ui.USDCHFradioButton, self.ui.USDJPYradioButton, self.ui.USDCADradioButton]
    allTfCheckBox = [self.ui.m_1radioButton, self.ui.m_5radioButton, self.ui.m_15radioButton, 
                     self.ui.m_30radioButton, self.ui.h_1radioButton, self.ui.d_1radioButton]

    for pair in allPairCheckBox:
        pair.setEnabled(enabled)
    for tf in allTfCheckBox:
        tf.setEnabled(enabled)