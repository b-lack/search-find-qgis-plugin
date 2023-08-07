
import os
import json

from qgis.PyQt import QtWidgets, uic
from qgis.PyQt.QtWidgets import QDialog, QListWidgetItem
from PyQt5 import QtCore, QtGui
from qgis.PyQt.QtCore import QSettings

from qgis.core import  QgsMessageLog

from ...utils.utils import Utils

from ..recording.recording import Recording
from ..navigate.selection import Selection


UI_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), 'settings.ui'))

PLUGIN_NAME = "find_location"

class Settings(QtWidgets.QWidget, UI_CLASS):


    def __init__(self, interface, bestCount=5):
        """Constructor."""

        QDialog.__init__(self, interface.mainWindow())
        self.setupUi(self)

        self.interface = interface


        # Degrees
        self.degUnits = [
            {"name": "Degree [°]", "value": "deg"},
            {"name": "Gon [gon]", "value": "gon"},
            {"name": "Radiant [rad]", "value": "rad"}
        ]

        unitSetting = Utils.getSetting('degUnit', 'deg')
        for index, unit in enumerate(self.degUnits):
            self.lfbDegUnit.addItem(unit['name'], unit['value'])
            if unitSetting == unit['value']:
                self.lfbDegUnit.setCurrentIndex(index)

        self.lfbDegUnit.currentIndexChanged.connect(self.degUnitChanged)

        # Meassurements
        self.meassurements = [
            {"name": "10", "value": 10},
            {"name": "20", "value": 20},
            {"name": "50", "value": 50},
            {"name": "100", "value": 100},
            {"name": "500", "value": 500},
            {"name": "1000", "value": 1000}
        ]

        meassurementSetting = Utils.getSetting('meassurementSetting', 100)
        for index, meassurement in enumerate(self.meassurements):
            self.lfbSettingsMeassurements.addItem(meassurement['name'], meassurement['value'])
            if meassurementSetting == meassurement['value']:
                self.lfbSettingsMeassurements.setCurrentIndex(index)

        self.lfbSettingsMeassurements.currentIndexChanged.connect(self.meassurementChanged)
                                

        # Aggregation
        self.aggregationTpes = [
            {"name": "mean", "value": "mean"},
            {"name": "median", "value": "median"}
        ]
        #validator = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]{1,4}"), self)
        #self.lfbSettingsMeassurements.setValidator(validator)

        unitSetting = Utils.getSetting('aggregationType', 'mean')
        for index, aggregation in enumerate(self.aggregationTpes):
            self.lfbSettingsAggregation.addItem(aggregation['name'], aggregation['value'])
            if unitSetting == aggregation['value']:
                self.lfbSettingsAggregation.setCurrentIndex(index)

        self.lfbSettingsAggregation.currentIndexChanged.connect(self.aggregationChanged)

        # bestMeassurementSetting Percent
        self.bestMeassurements = [
            {"name": "100", "value": 100},
            {"name": "90", "value": 90},
            {"name": "80", "value": 80},
            {"name": "70", "value": 70}
        ]

        bestMeassurementSetting = Utils.getSetting('bestMeassurementSetting', 70)
        for index, aggregation in enumerate(self.bestMeassurements):
            self.lfbSettingsPercentBox.addItem(aggregation['name'], aggregation['value'])
            if bestMeassurementSetting == aggregation['value']:
                self.lfbSettingsPercentBox.setCurrentIndex(index)

        self.lfbSettingsPercentBox.currentIndexChanged.connect(self.bestMeassurementsChanged)

        # list widget items
        self.selectedItem = None
        defaultItems = [
            {"name": "PDOP", "value": "pdop", "direction": True},
            {"name": "HDOP", "value": "hdop", "direction": True},
            {"name": "Satellite Count", "value": "satellitesUsed", "direction": False}
        ]

        self.items = json.loads(Utils.getSetting('sortingValues', json.dumps(defaultItems)))

        self.addItemsToList()

        self.lfbGpsInfoSortingList.setSortingEnabled(False)
        self.lfbGpsInfoSortingList.itemSelectionChanged.connect(self.itemSelected)

        self.lfbSortUpBtn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowUp))
        self.lfbSortUpBtn.clicked.connect(self.sortUp)

        self.lfbSortDownBtn.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowDown))
        self.lfbSortDownBtn.clicked.connect(self.sortDown)

        self.lfbSortUpBtn.setEnabled(False)
        self.lfbSortDownBtn.setEnabled(False)

        self.checkButtons()

    def aggregationChanged(self, item):
        saveValue = self.aggregationTpes[item]['value']
        Utils.setSetting('aggregationType', saveValue)

    def degUnitChanged(self, item):
        saveValue = self.degUnits[item]['value']
        Utils.setSetting('degUnit', saveValue)

    def meassurementChanged(self, item):
        saveValue = self.meassurements[item]['value']
        Utils.setSetting('meassurementSetting', saveValue)
    
    def bestMeassurementsChanged(self, item):
        saveValue = self.bestMeassurements[item]['value']
        Utils.setSetting('bestMeassurementSetting', saveValue)

    def checkButtons(self):

        self.selectedItem = self.lfbGpsInfoSortingList.currentItem()
        
        if self.selectedItem == None:
            return
        
        pos = self.findItemPosition(self.selectedItem.text())
        
        if pos == 0:
            self.lfbSortUpBtn.setEnabled(False)
        else:
            self.lfbSortUpBtn.setEnabled(True)
        
        if pos == len(self.items)-1:
            self.lfbSortDownBtn.setEnabled(False)
        else:
            self.lfbSortDownBtn.setEnabled(True)

    def addItemsToList(self):

        self.lfbGpsInfoSortingList.clear()

        for itemText in self.items:
            item = QListWidgetItem(itemText['name'])
            self.lfbGpsInfoSortingList.addItem(item)

        Utils.setSetting('sortingValues', json.dumps(self.items))
        QgsMessageLog.logMessage(json.dumps(self.items),'LFB')

    def itemSelected(self):
        self.lfbSortUpBtn.setEnabled(True)
        self.lfbSortDownBtn.setEnabled(True)
       

        self.selectedItem = self.lfbGpsInfoSortingList.currentItem()

        QgsMessageLog.logMessage(str( self.selectedItem.text() ),'LFB')

        
    def findItemPosition(self, item):
        for index, itemText in enumerate(self.items):
            if itemText['name'] == item:
                return index, itemText
        return -1, None

    def sortUp(self):

        self.selectedItem = self.lfbGpsInfoSortingList.currentItem()

        if self.selectedItem == None:
            return
        
        pos, item = self.findItemPosition(self.selectedItem.text())
                
        newPosition = max(0, pos - 1)
        del self.items[pos]
        self.items.insert(newPosition, item)

        self.addItemsToList()

        self.lfbGpsInfoSortingList.setCurrentRow( newPosition )

        self.checkButtons()
    
    def sortDown(self):

        self.selectedItem = self.lfbGpsInfoSortingList.currentItem()
        
        if self.selectedItem == None:
            return

        pos, item = self.findItemPosition(self.selectedItem.text())
        
        newPosition = min(len(self.items), pos + 1)
        del self.items[pos]
        self.items.insert(newPosition, item)

        self.addItemsToList()

        self.lfbGpsInfoSortingList.setCurrentRow( newPosition )

        self.checkButtons()

