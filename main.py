# The layout of this GUI was branched from https://github.com/Wanderson-Magalhaes/Toggle_Burguer_Menu_Python_PySide2
# I have modified it to work with PyQt5 rather than PySide2.
# I have also added my own elements to the GUI.

# Import Libraries
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication

# GUI FILE with the UI designed in Qt Designer software
from GUI.ui_main import Ui_MainWindow

# IMPORT FUNCTIONS that connect to application
from GUI.ui_functions import *

#My test
class MainWindow(QMainWindow):
    def __init__(self):
        """
            This class is the main window class which connects together
            the UI created in Qt Designer and all the functionality required 
            for backtesting and live trading
        """
        QMainWindow.__init__(self)  # Main window super class initialized 
        self.ui = Ui_MainWindow()   # Get UI created in QT Designer
        self.ui.setupUi(self)       # Initialize UI
        self.setWindowIcon(QtGui.QIcon('GUI\Favicon\\favicon.ico')) # Add Icon Image to window
        self.setFixedSize(750, 550) # Use a fixed size for UI Window

        # TOGGLE/BURGER MENU
        self.ui.Btn_Toggle.clicked.connect(lambda: UIFunctions.toggleMenu(self, 250, True))
        
        # Connect page 1 button to page 1 content
        self.ui.btn_page_1.clicked.connect(lambda:  UIFunctions.pageSet(self, self.ui.page_1, self.ui.btn_page_1))

        # Connect page 2 button to page 2 content
        self.ui.btn_page_2.clicked.connect(lambda: UIFunctions.pageSet(self, self.ui.page_2, self.ui.btn_page_2))

        # Connect page 3 button to page 3 content
        self.ui.btn_page_3.clicked.connect(lambda: UIFunctions.pageSet(self, self.ui.page_3, self.ui.btn_page_3))


        # Run Button Clicked
        self.ui.runButton.clicked.connect(lambda: UIFunctions.run(self)) # Connect button to run function
        self.threadRunButton = ThreadRunButton(self)    # Create a thread
        self.threadRunButton.finished.connect(lambda: UIFunctions.runIsFinished(self)) # When thread is finished run "runIsFinished" function

        # Stop Button Clicked
        self.ui.stopButton.setVisible(False)    # Set stop button to invisible
        self.ui.stopButton.setEnabled(False)    # Set stop button to disbaled
        self.ui.stopButton.clicked.connect(lambda: UIFunctions.stop(self)) # Connect stop button to the stop function

        self.ui.label_2.setPixmap(QtGui.QPixmap("GUI\Images\logo.png")) # Add image to the UI

        # SHOW ==> MAIN WINDOW
        self.ui.EURUSDradioButton.setChecked(True)
        self.ui.m_1radioButton.setChecked(True)
        UIFunctions.pageSet(self, self.ui.page_1, self.ui.btn_page_1) # Set first page displayed to page 1
        self.show() # Show GUI

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
