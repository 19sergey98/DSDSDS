from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import Utils
import operator
import numpy as np
from ClusterAdjustments import *
from ScaleAdjustments import *
from UtilityClasses import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class GraphInspectionWindow(QMainWindow):
    """ Окно детального изучения графика.

    """

    clusterAdjustmentWindow = None

    scalingAdjustmentWindow = None

    def __init__(self, parent, axes):
        super().__init__(parent)

        self.menubar = self.menuBar()
        self.parametersMenu = self.menubar.addMenu("Параметры")
        self.scalingOption = QAction('Масштаб', self)
        self.scalingOption.triggered.connect(self.showScalingView)
        self.parametersMenu.addAction(self.scalingOption)

        self._selectionPolygon = []
        self._selectedPoints = []
        self._xData = []
        self._yData = []
        self._axes = axes
        self.setGeometry(100, 100, 1500, 480)
        self.setWindowTitle("Выбранный график")
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QHBoxLayout(self.centralWidget)
        self.layout.setContentsMargins(0,0,0,0)
        self.graphWidget = self.formGraphWidget(self._axes)
        self.layout.addWidget(self.graphWidget)
        self.tabWidget = QTabWidget()
        self.layout.addWidget(self.tabWidget)

        self.figure = Figure()
        self.barWidget = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.refreshBarChart()

        self.figure_manh = Figure()
        self.barWidget_manh = FigureCanvas(self.figure_manh)
        self.axes_manh = self.figure_manh.add_subplot(111)
        self.refreshManhBarChart()

        self.bartabs = QTabWidget()
        self.bartabs.addTab(self.barWidget, "Евклидово расстояние")
        self.bartabs.addTab(self.barWidget_manh, "Манхэттэнское расстояние")
        self.layout.addWidget(self.bartabs)

        self.newClusterView = QWidget()
        self.tabWidget.addTab(self.newClusterView, "Новый кластер")
        self.newClusterViewLayout = QVBoxLayout(self.newClusterView)

        self.tableHeader = QLabel("выделенные точки")
        self.tableHeader.setAlignment(Qt.AlignCenter)
        self.newClusterViewLayout.addWidget(self.tableHeader)
        self.pointsTable = QTableWidget()
        self.pointsTable.setColumnCount(3)
        self.pointsTable.setHorizontalHeaderLabels(["абсцисса", "ордината", ""])
        self.newClusterViewLayout.addWidget(self.pointsTable)
        self.buttonGroup = QWidget()
        self.buttonGroupLayout = QGridLayout(self.buttonGroup)
        self.clearSelectionButton = QPushButton("Очистить выделение")
        self.clearSelectionButton.clicked.connect(self.clearSelection)
        self.createClusterButton = QPushButton("Создать кластер")
        self.createClusterButton.clicked.connect(self.createClusterClicked)
        self.selectionCompleteButton = QPushButton("Завершить выделение")
        self.selectionCompleteButton.clicked.connect(self.selectionCompleted)
        self.buttonGroupLayout.addWidget(self.selectionCompleteButton, 1, 1)
        self.buttonGroupLayout.addWidget(self.clearSelectionButton, 1, 2)
        self.buttonGroupLayout.addWidget(self.createClusterButton, 2, 1, 1, 2)
        self.newClusterViewLayout.addWidget(self.buttonGroup)

        self.existingClusterView = QWidget()
        self.tabWidget.addTab(self.existingClusterView, "Существующий кластер")

        cid1 = self.graphWidget.mpl_connect('motion_notify_event', self.onmousemove)
        cid2 = self.graphWidget.mpl_connect('button_press_event', self.onclick)
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.statusBar().showMessage("Готово")

        self.show()

    def createClusterClicked(self):
        """ Обработчик клика на кнопку "Создать кластер"

        """
        if self._selectedPoints == []:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Кластер не может быть создан")
            msg.setInformativeText("Не выделено ни одной точки")
            msg.setStyleSheet( #TODO разобраться как выровнять кнопку ОК по центру
                'QMessageBox {text-align: center;}\n QPushButton:center{margin: auto;}\n QPushButton:hover{color: #2b5b84;}')
            msg.setWindowTitle("Внимание")
            msg.exec_()
        else:
            indexSet = set()
            for point in self._selectedPoints:
                indexSet.add(point.getIndex())
            cluster = ClusterDialog.newCluster(self.parent().globalData.buildClusterDataFromIndexSet(indexSet))
            if cluster is not None:
                self.parent().addCluster(cluster)
                self.clearSelection()

    def selectionCompleted(self):
        """ Обработчик клика на кнопку "Завершить выделение"

        """
        self._selectedPoints.clear()
        self.pointsTable.setRowCount(0)
        if len(self._selectionPolygon) < 3:
            self.statusBar().showMessage("Область выделения не определена")
        else:
            points = []
            for i in range(0, len(self._xData)):
                point = Point(self._xData[i], self._yData[i], i)
                for cluster in self.parent().clusters:
                    innerClusterData = cluster.getInnerData()
                    if innerClusterData.getRowByRowOriginalIndex(i) is not None and innerClusterData.getRowByRowOriginalIndex(i).isHidden():
                        point.setHidden(True)
                        break
                points.append(point)
            for point in points:
                if Utils.crossingNumberAlgorithm(point, self._selectionPolygon) and not point.isHidden():
                    self._selectedPoints.append(point)
            selectedXData = []
            selectedYData = []
            verticalHeaders = []
            for i, point in enumerate(self._selectedPoints):
                verticalHeaders.append(str(point.getIndex()))
                selectedXData.append(point.getX())
                selectedYData.append(point.getY())
                self.pointsTable.setRowCount(self.pointsTable.rowCount() + 1)
                self.pointsTable.setItem(i, 0, QTableWidgetItem(str(point.getX())))
                self.pointsTable.setItem(i, 1, QTableWidgetItem(str(point.getY())))
                removePointButton = QPushButton("Убрать")
                index = QPersistentModelIndex(self.pointsTable.model().index(i, 2))
                removePointButton.clicked.connect(
                    lambda *args, index=index: self.removePoint(index.row()))
                self.pointsTable.setCellWidget(i, 2, removePointButton)
                self._axes.plot(selectedXData, selectedYData,
                                linestyle = "None",
                                marker = Constants.DEFAULT_SELECTION_SHAPE,
                                color = Constants.DEFAULT_SELECTION_COLOR,
                                markersize = Constants.DEFAULT_SELECTION_POINT_SIZE)
            self.pointsTable.setVerticalHeaderLabels(verticalHeaders)
            Utils.drawPolygon(self._selectionPolygon, self.graphWidget)
            self.refreshBarChart()
            self.refreshManhBarChart()

    def removePoint(self, index):
        """ Удаляет точку из выделения

        :param index: идентификатор точки
        """
        del self._selectedPoints[index]
        self.pointsTable.removeRow(index)
        self.refreshPlot()
        self.refreshBarChart()
        self.refreshManhBarChart()

        selectedXData = [] # TODO избавиться от дублирования кода и сделать функцию drawSelectedPoints.
        # Речь идет о таком же механизме рисования в selectionCompleted
        selectedYData = []
        for i, point in enumerate(self._selectedPoints):
            selectedXData.append(point.getX())
            selectedYData.append(point.getY())
            self._axes.plot(selectedXData, selectedYData,
                            linestyle="None",
                            marker=Constants.DEFAULT_SELECTION_SHAPE,
                            color=Constants.DEFAULT_SELECTION_COLOR,
                            markersize=Constants.DEFAULT_SELECTION_POINT_SIZE)
        Utils.drawPolygon(self._selectionPolygon, self.graphWidget)


    def clearSelection(self):
        """ Обработчик клика на кнопку "Очистать выделение"

        """
        self.refreshPlot()
        self.pointsTable.setRowCount(0)
        self._selectedPoints = []
        self._selectionPolygon = []
        self.graphWidget.draw()

    def refreshPlot(self):
        """ Очищает график и рисует его заново.

        """
        while len(self._axes.lines) > 0: # С удалением в matplotlib большие странности. По какой-то причине
            del self._axes.lines[-1]     # нет нормального способа очистить график (или я чего-то не понял?).
                                         # Но подобные циклы делают дело.
        self._axes.plot(self._xData, self._yData,
                        linestyle = "None",
                        marker = Constants.DEFAULT_POINT_SHAPE,
                        color = Constants.INVISIBLE_COLOR,
                        markersize = Constants.DEFAULT_MARKER_SIZE_SMALL)
        # Рисуем сначала все кластеры последовательно, а потом фантомный кластер состоящий из точек,
        # не принадлежащих ни одному кластеру
        for cluster in self.parent().clusters:
            cluster.draw2DProjection(self._axes, self._axes.scatterMatrixXIndex, self._axes.scatterMatrixYIndex, Constants.DEFAULT_MARKER_SIZE_BIG)
        dummyCluster = self.parent().globalData.getDummyCluster(self.parent().clusters)
        dummyCluster.draw2DProjection(self._axes, self._axes.scatterMatrixXIndex, self._axes.scatterMatrixYIndex, Constants.DEFAULT_MARKER_SIZE_SMALL)

    def tabChanged(self):
        self.clearSelection()

    def onmousemove(self, event):
        """ Обработчик движений мыши. Выводит информацию в статус бар. Назначение скорее косметическое.

        :param event: событие движения мыши
        """
        mousex, mousey = event.xdata, event.ydata
        if (mousex is None) or (mousey is None):
            self.statusBar().showMessage("Указатель вне области графика")
        else:
            self.statusBar().showMessage("координаты: x = {:.07f} y = {:.07f}".format(mousex, mousey))

    def onclick(self, event):
        """ Обработчик клика мыши.

        :param event: событие - клик мыши
        """
        mousex, mousey = event.xdata, event.ydata
        if (mousex != None) and (mousey != None):
            point = Point(mousex, mousey, None)
            self._selectionPolygon.append(point)
            # почему два, а не один? Программирование наугад.
            lineAmount = 2
            # нужно сначала удалить предыдущий рисунок выделения(если он есть). Для этого считаем сколько линий должно быть
            for cluster in self.parent().clusters:
                lineAmount += 1
            # все остальные линии удаляем
            while len(self._axes.lines) > lineAmount:
                del self._axes.lines[-1]
            # рисуем выделение
            Utils.drawBrokenLine(self._selectionPolygon, self.graphWidget)

    def closeEvent(self, event):
        self._selectionPolygon.clear()
        self._selectedPoints.clear()
        event.accept()

    def getSelection(self):
        return self._selectedPoints

    def formGraphWidget(self, axes):
        """ Формируем PyQt виджет представляющий из себя график с точками.
        Виджет копирует график из проекции на которую был клик в родительском окне.
        Для лучшего понимания того, что здесь происходит см. документацию на функцию getSupportiveLine в Utils

        :param axes: график, на который был клик в родительском окне.
        :return: PyQt виджет.
        """
        self._xData = axes.lines[0].get_xdata()
        self._yData = axes.lines[0].get_ydata()
        newFigure = Figure()
        newGraphWidget = FigureCanvas(newFigure)
        self._axes = newFigure.add_subplot(111)
        self._axes.plot(self._xData, self._yData,
                        linestyle = "None",
                        marker = Constants.DEFAULT_POINT_SHAPE,
                        color = Constants.INVISIBLE_COLOR,
                        markersize = Constants.DEFAULT_MARKER_SIZE_SMALL)
        ylabel = axes.title._text[:axes.title._text.find('_')]
        self._axes.set_ylabel(ylabel)
        xlabel = axes.title._text[axes.title._text.find('_') + 1:]
        self._axes.set_xlabel(xlabel)
        self._axes.set_title("зависимость " + ylabel + " от " + xlabel)
        newGraphWidget.setGeometry(0, 0, 480, 480)

        self._axes.scatterMatrixXIndex = axes.scatterMatrixXIndex
        self._axes.scatterMatrixYIndex = axes.scatterMatrixYIndex
        for cluster in self.parent().clusters:
            cluster.draw2DProjection(self._axes, axes.scatterMatrixXIndex, axes.scatterMatrixYIndex, Constants.DEFAULT_MARKER_SIZE_BIG)
        dummyCluster = self.parent().globalData.getDummyCluster(self.parent().clusters)
        dummyCluster.draw2DProjection(self._axes, axes.scatterMatrixXIndex, axes.scatterMatrixYIndex, Constants.DEFAULT_MARKER_SIZE_SMALL)
        newGraphWidget.setToolTip("Кликайте мышью, чтобы выделить точки")

        return newGraphWidget

    def showScalingView(self):
        self.scalingAdjustmentWindow = ScaleAdjustmentsView(self, self._axes)


    # TODO избавиться от всего, что ниже. Сделано очень наспех. Значительное дублирование кода из ClusterPointsAdjustments
    def refreshBarChart(self):
        self.axes.clear()
        xcoords = np.arange(len(self._selectedPoints))
        distances = []
        indexes = self.getIndexList()
        massCenter = self.evaluateSelectionMassCenter()
        significancefactors = self.parent().globalData.getSignificanceFactors()
        for row in self.convertPointsToRows():
            distances.append(row.distanceTo(massCenter, significancefactors))
        sorteddata = self.sortBarData(indexes, distances)
        self.axes.bar(xcoords, sorteddata[1], align="center", tick_label=sorteddata[0])
        if len(self._selectedPoints) > 10:
            for item in self.axes.get_xticklabels():
                item.set_fontsize(10 - len(self._selectedPoints) // 8)
        self.axes.set_title("Расстояния до центра \n масс выделения")
        self.barWidget.draw()

    def refreshManhBarChart(self):
        self.axes_manh.clear()
        xcoords = np.arange(len(self._selectedPoints))
        distances = []
        indexes = self.getIndexList()
        massCenter = self.evaluateSelectionMassCenter()
        significancefactors = self.parent().globalData.getSignificanceFactors()
        for row in self.convertPointsToRows():
            distances.append(row.manhattanDistanceTo(massCenter, significancefactors))
        sorteddata = self.sortBarData(indexes, distances)
        self.axes_manh.bar(xcoords, sorteddata[1], align="center", tick_label=sorteddata[0])
        if len(self._selectedPoints) > 10:
            for item in self.axes_manh.get_xticklabels():
                item.set_fontsize(10 - len(self._selectedPoints) // 8)
        self.axes_manh.set_title("Манхэттенские расстояния до центра \n масс выделения")
        self.barWidget_manh.draw()

    def evaluateSelectionMassCenter(self):
        rows = self.convertPointsToRows()

        rowsAmount = len(rows)
        if rowsAmount > 0:
            massCenterDataArray = [0] * len(rows[0])
            for row in rows:
                for i in range(0, len(row)):
                    massCenterDataArray[i] += row[i]
            massCenterDataArray[:] = [element / rowsAmount for element in massCenterDataArray]
            return Row(None, massCenterDataArray)
        else:
            return None

    def convertPointsToRows(self):
        indexSet = set()
        for point in self._selectedPoints:
            indexSet.add(point.getIndex())
        return self.parent().globalData.getRowsByIndexSet(indexSet)

    def getIndexList(self):
        indexList = []
        for point in self._selectedPoints:
            indexList.append(point.getIndex())
        return indexList

    def sortBarData(self, indexes, distances):
        mappeddata = dict(zip(indexes, distances))
        sorteddata = sorted(mappeddata.items(), key=operator.itemgetter(1))
        sorteddistances = []
        sortedindexes = []
        for element in sorteddata:
            sortedindexes.append(element[0])
            sorteddistances.append(element[1])
        return sortedindexes, sorteddistances
