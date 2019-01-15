from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

import numpy as np
import operator
import Utils
from UtilityClasses import Data

class ClusterPointsView(QMainWindow):
    """ В этом окне можно видеть таблицу со списком точек, входящих в кластер. Точки можно удалять и добавлять.

    """

    def __init__(self, parent, cluster):
        super().__init__(parent)
        self.cluster = cluster
        self.columnCount = self.parent().globalData.columnCount()
        self.centralWidget = QWidget()
        self.layout = QHBoxLayout(self.centralWidget)
        self.setCentralWidget(self.centralWidget)
        self.tabletabs = QTabWidget()
        self.tabletabs.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.clusterPointsTable = QTableWidget();
        self.clusterPointsTable.resizeColumnsToContents()
        self.tabletabs.addTab(self.clusterPointsTable, "Удаление точек")
        self.unbusyPointsTable = QTableWidget()
        self.tabletabs.addTab(self.unbusyPointsTable, "Добавление точек")
        self.layout.addWidget(self.tabletabs)

        self.figure = Figure()
        self.barWidget = FigureCanvas(self.figure)
        self.barWidget.mpl_connect('button_press_event', self.onclickonbar)
        self.axes = self.figure.add_subplot(111)
        self.refreshBarChart()

        self.figure_manh = Figure()
        self.barWidget_manh = FigureCanvas(self.figure_manh)
        self.barWidget.mpl_connect('button_press_event', self.onclickonbarmanh)
        self.axes_manh = self.figure_manh.add_subplot(111)
        self.refreshManhBarChart()

        self.bartabs = QTabWidget()
        self.bartabs.addTab(self.barWidget, "Евклидово расстояние")
        self.bartabs.addTab(self.barWidget_manh, "Манхэттэнское расстояние")
        self.bartabs.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)


        self.layout.addWidget(self.bartabs)
        self.refreshUnbusyPointsTable()
        self.refreshClusterPointsTable()
        self.resize(1000, 500)
        self.setWindowTitle("Точки кластера: " + cluster.getName())
        self.show()

    def refreshBarChart(self):
        self.axes.clear()
        xcoords = np.arange(self.cluster.getSize())
        distances = []
        indexes = Data.getIndexList(self.cluster)
        massCenter = self.cluster.evaluateMassCenter()
        significancefactors = self.parent().globalData.getSignificanceFactors()
        for row in self.cluster:
            distances.append(row.distanceTo(massCenter, significancefactors))
        sorteddata = self.sortBarData(indexes, distances)
        self.axes.bar(xcoords, sorteddata[1], align="center", tick_label=sorteddata[0])
        if self.cluster.getSize() > 10:
            for item in self.axes.get_xticklabels():
                item.set_fontsize(10 - self.cluster.getSize() // 8)
        self.axes.set_title("Расстояния до центра \n масс кластера")
        self.barWidget.draw()

    def refreshManhBarChart(self):
        self.axes_manh.clear()
        xcoords = np.arange(self.cluster.getSize())
        distances = []
        indexes = Data.getIndexList(self.cluster)
        massCenter = self.cluster.evaluateMassCenter()
        significancefactors = self.parent().globalData.getSignificanceFactors()
        for row in self.cluster:
            distances.append(row.manhattanDistanceTo(massCenter, significancefactors))
        sorteddata = self.sortBarData(indexes, distances)
        self.axes_manh.bar(xcoords, sorteddata[1], align="center", tick_label=sorteddata[0])
        if self.cluster.getSize() > 10:
            for item in self.axes_manh.get_xticklabels():
                item.set_fontsize(10 - self.cluster.getSize() // 8)
        self.axes_manh.set_title("Манхэттенские расстояния до центра \n масс кластера")
        self.barWidget_manh.draw()


    def refreshClusterPointsTable(self): 
        self.clusterPointsTable.setRowCount(0)
        Utils.fillTableWithCluster(self.clusterPointsTable, self.cluster)
        self.clusterPointsTable.setColumnCount(self.columnCount + 1)
        self.clusterPointsTable.setHorizontalHeaderItem(self.columnCount, QTableWidgetItem(" "))
        for i, row in enumerate(self.cluster):
            removePointButton = QPushButton("Исключить")
            self.clusterPointsTable.setCellWidget(i, self.columnCount, removePointButton)
            index = QPersistentModelIndex(self.clusterPointsTable.model().index(i, 0))
            removePointButton.clicked.connect(
                lambda *args, index=index: self.removePointFromCluster(index.row()))

    def refreshUnbusyPointsTable(self):
        self.unbusyPointsTable.setColumnCount(self.columnCount + 1)
        self.unbusyPointsTable.setRowCount(0)
        busyIndexes = self.cluster.getIndexSet()
        indexes = []
        for rowNum, row in enumerate(self.parent().globalData):
            if row.getIndex() not in busyIndexes:
                self.unbusyPointsTable.setRowCount(self.unbusyPointsTable.rowCount() + 1)
                indexes.append(row.getIndex())
                for columnIndex in range(0, self.columnCount):
                    self.unbusyPointsTable.setItem(self.unbusyPointsTable.rowCount() - 1, columnIndex,
                                                    QTableWidgetItem(str(row[columnIndex])))
                addPointButton = QPushButton("Добавить")
                a = self.unbusyPointsTable.rowCount()
                b = self.columnCount
                self.unbusyPointsTable.setCellWidget(self.unbusyPointsTable.rowCount() - 1, self.columnCount, addPointButton)
                addPointButton.clicked.connect(
                    lambda *args, row=row: self.addPointToCluster(row))
        self.unbusyPointsTable.setVerticalHeaderLabels(list(map(str, indexes)))

    def removePointFromCluster(self, index):
        del self.cluster[index]
        self.refreshBarChart()
        self.refreshManhBarChart()
        self.refreshClusterPointsTable()
        self.refreshUnbusyPointsTable()

    def addPointToCluster(self, row):
        self.cluster.addRow(row)
        self.refreshBarChart()
        self.refreshManhBarChart()
        self.refreshClusterPointsTable()
        self.refreshUnbusyPointsTable()

    def sortBarData(self, indexes, distances):
        mappeddata = dict(zip(indexes, distances))
        sorteddata = sorted(mappeddata.items(), key=operator.itemgetter(1))
        sorteddistances = []
        sortedindexes = []
        for element in sorteddata:
            sortedindexes.append(element[0])
            sorteddistances.append(element[1])
        return sortedindexes, sorteddistances

    def onclickonbar(self, event):
        mousex, mousey = event.xdata, event.ydata
        if (mousex != None) and (mousey != None):
            massCenter = self.cluster.evaluateMassCenter()
            significancefactors = self.parent().globalData.getSignificanceFactors()
            for element in self.cluster:
                if element.distanceTo(massCenter, significancefactors) > mousey:
                    self.cluster.remove(element)
            self.refreshBarChart()

    def onclickonbarmanh(self, event):
        pass

    def closeEvent(self, event):
        self.parent().refreshCanvas()
        self.parent().refreshClusterTable()
        event.accept()

