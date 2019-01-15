from PyQt5.QtWidgets import *
from UtilityClasses import Cluster
import Constants


class DBScanWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)

        # Глобальные переменные для пошагового исполнения алгоритма.
        # Для того чтобы выполнить шаг нужно помнить состояние достигнутое прыдыдущими шагами.
        # Это состояние хранится в следующих переменных
        self.workData = self.parent().globalData
        self.rowsToClusterize = list(self.workData)
        self.rowsToConsider = list(self.workData)
        self.resultClusters = []
        self.supposedClusterElems = set()
        self.stepIterator = 0
        self.clusterIterator = 0
        self.neighborsCurrent = set()
        self.neighborsToConsider = set()
        self.neighborsConsidered = set()
        self.cluster = None
        self.prevClusterSize = 0
        self.currClusterSize = 0

        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QVBoxLayout(self.centralWidget)
        self.vicinityLabel = QLabel("Радиус окрестности")
        self.vicinityEdit = QLineEdit()
        self.checkforamountLabel = QLabel("Число соседей")
        self.checkforamountEdit = QLineEdit()
        self.layout.addWidget(self.vicinityLabel)
        self.layout.addWidget(self.vicinityEdit)
        self.layout.addWidget(self.checkforamountLabel)
        self.layout.addWidget(self.checkforamountEdit)

        self.confirmationButton = QPushButton("Выполнить алгоритм")
        self.confirmationButton.clicked.connect(self.performAlgorithm)
        self.layout.addWidget(self.confirmationButton)

        self.exstepbystepButton = QPushButton("Выполнить пошагово")
        self.exstepbystepButton.clicked.connect(self.exstepbystep)
        self.layout.addWidget(self.exstepbystepButton)

        self.buttongroup = QWidget()
        self.buttongrouplayout = QHBoxLayout(self.buttongroup)
        self.nextstepButton = QPushButton("След Шаг")
        self.nextstepButton.clicked.connect(self.stepAndVisualize)
        self.nextstepButton.setEnabled(False)
        self.continueButton = QPushButton("Завершить")
        self.continueButton.setEnabled(False)
        self.buttongrouplayout.addWidget(self.nextstepButton)
        self.buttongrouplayout.addWidget(self.continueButton)
        self.layout.addWidget(self.buttongroup)

        self.multiplestepsbutton = QPushButton("Выполнить N шагов")
        self.multiplestepsbutton.clicked.connect(self.takemultiplesteps)
        self.multiplestepsbutton.setEnabled(False)
        self.label = QLabel("N = ")
        self.lineedit = QLineEdit()
        self.lineedit.setPlaceholderText("N")
        self.widgetgroup = QWidget()
        self.widgetgrouplayout = QHBoxLayout(self.widgetgroup)
        self.widgetgroup.setEnabled(False)
        self.widgetgrouplayout.addWidget(self.label)
        self.widgetgrouplayout.addWidget(self.lineedit)
        self.layout.addWidget(self.multiplestepsbutton)
        self.layout.addWidget(self.widgetgroup)

        self.setGeometry(100, 100, 200, 200)
        self.setWindowTitle("DBScan")
        self.show()

    def performAlgorithm(self):
        if self.prepareData():
            print(*self.rowsToClusterize)
            iterCounter = 0
            while len(self.rowsToClusterize) > 0:
                iterCounter += 1
                self.supposedClusterElems = set()
                prevIterSize = 0
                self.supposedClusterElems.add(self.rowsToClusterize[0])
                while prevIterSize < len(self.supposedClusterElems):
                    prevIterSize = len(self.supposedClusterElems)
                    clusterExtension = set()
                    for item in self.supposedClusterElems:
                        neighbors = self.findNeighbors(item, self.radius)
                        for item in neighbors:
                            if self.isElemSuitable(item, self.radius, self.neighborsamount):
                                clusterExtension.add(item)
                    self.supposedClusterElems.update(clusterExtension)
                cluster = Cluster(self.workData.buildClusterDataFromRows(list(self.supposedClusterElems)))
                cluster.setColor(Constants.EXTENDED_COLOR_SET[(iterCounter-1) % len(Constants.EXTENDED_COLOR_SET)])
                cluster.setName("dbscan" + str(iterCounter))
                self.resultClusters.append(cluster)
                # строки полученного кластера удаляем из исходного набора
                for item in self.supposedClusterElems:
                    self.rowsToClusterize.remove(item)
                    self.rowsToConsider.remove(item)
            self.parent().addClusters(self.resultClusters)

    def performStep(self):
        if self.cluster is None:
            if len(self.rowsToClusterize) is 0:
                self.close()
            else:
                self.clusterIterator += 1
                self.staterow = self.rowsToClusterize[0]
                self.neighborsConsidered.add(self.staterow)
                self.neighborsCurrent = self.findNeighbors(self.staterow, self.radius)
                self.neighborsToConsider = set(self.neighborsCurrent)
                self.cluster = Cluster(self.workData.buildClusterDataFromRows([self.staterow]))
                self.cluster.setName("dbscan" + str(self.clusterIterator))
                self.cluster.setColor(Constants.EXTENDED_COLOR_SET[(self.clusterIterator-1) % len(Constants.EXTENDED_COLOR_SET)])
                self.rowsToClusterize.remove(self.staterow)
                self.parent().addCluster(self.cluster)
                self.currClusterSize = 1
                self.prevClusterSize = 0
        else:
            if len(self.neighborsToConsider) is not 0:
                self.staterow = self.neighborsToConsider.pop()
                self.neighborsConsidered.add(self.staterow)
                if self.isElemSuitable(self.staterow, self.radius, self.neighborsamount):
                    self.cluster.addRow(self.staterow)
                    if self.staterow in self.rowsToClusterize:
                        self.rowsToClusterize.remove(self.staterow)
            else:
                self.prevClusterSize = self.currClusterSize
                self.currClusterSize = len(self.cluster)
                if self.currClusterSize != self.prevClusterSize:
                    for elem in self.neighborsCurrent:
                        self.neighborsToConsider.update(self.findNeighbors(elem, self.radius))
                    self.neighborsToConsider = self.neighborsToConsider - self.neighborsConsidered
                    self.neighborsCurrent = set(self.neighborsToConsider)
                else:
                    for elem in self.cluster:
                        self.rowsToConsider.remove(elem)
                        self.cluster = None

    def isElemSuitable(self, sourcerow, radius, amount):
        neighbors = self.findNeighbors(sourcerow, radius)
        if len(neighbors) >= amount:
            return True
        else:
            return False

    def findNeighbors(self, sourcerow, radius):
        significancefactors = self.parent().globalData.getSignificanceFactors()
        neighbors = set()
        rowsToIterateOver = set(self.rowsToConsider) - set([sourcerow])
        for row in rowsToIterateOver:
            if sourcerow.distanceTo(row, significancefactors) < radius:
                neighbors.add(row)
        return neighbors

    def visualize(self, sourcerow, radius):
        self.parent().sphere = (sourcerow, radius)
        self.parent().refreshCanvas()

    def stepAndVisualize(self):
        self.performStep()
        self.visualize(self.staterow, self.radius)

    def takemultiplesteps(self):
        try:
            amount = int(self.lineedit.text())
            for i in range(0, amount):
                self.performStep()
            self.visualize(self.staterow, self.radius)
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Число шагов задано некорректно")
            msg.setWindowTitle("Внимание")
            msg.exec_()

    def exstepbystep(self):
        if self.prepareData():
            self.confirmationButton.setEnabled(False)
            self.continueButton.setEnabled(True)
            self.nextstepButton.setEnabled(True)
            self.checkforamountEdit.setEnabled(False)
            self.vicinityEdit.setEnabled(False)
            self.exstepbystepButton.setEnabled(False)
            self.multiplestepsbutton.setEnabled(True)
            self.widgetgroup.setEnabled(True)
            self.stepAndVisualize()

    def prepareData(self):
        """ Подготавилвает данные, нужные для работы алгоритма

        :return: возвращает True если подготовка выполнена успешно и False в противном случае
        """
        try:
            self.radius = float(self.vicinityEdit.text())
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Радиус задан некорректно")
            msg.setWindowTitle("Внимание")
            msg.exec_()
            return False
        try:
            self.neighborsamount = int(self.checkforamountEdit.text())
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Число соседей задано некорректно")
            msg.setWindowTitle("Внимание")
            msg.exec_()
            return False
        self.workData = self.parent().globalData
        self.rowsToClusterize = list(self.workData)
        self.resultClusters = []
        self.supposedClusterElems = set()
        return True

    def closeEvent(self, event):
        self.parent().sphere = None
        self.parent().circle = None
        self.parent().refreshCanvas()
        self.parent().refreshClusterTable()
        event.accept()