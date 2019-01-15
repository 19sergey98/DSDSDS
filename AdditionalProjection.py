from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import math
from UtilityClasses import Row
import Constants

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class AdditionalProjectionWindow(QMainWindow):

    def __init__(self, parent):
        super().__init__(parent)
        self.menubar = self.menuBar()
        self.optionsMenu = self.menubar.addMenu("Опции")
        self.rotateOption = QAction('Вращать', self)
        self.rotateOption.triggered.connect(self.rotate)
        self.optionsMenu.addAction(self.rotateOption)
        self.data = self.parent().globalData
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.layout = QHBoxLayout(self.centralWidget)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.newData = list(self.data)
        self.figure = Figure()
        self.graphWidget = FigureCanvas(self.figure)
        self.axes = self.figure.add_subplot(111)
        self.layout.addWidget(self.graphWidget)
        self.refreshImage()
        self.setGeometry(100, 100, 500, 500)
        self.show()

    def refreshImage(self):
        self.axes.clear()
        xData = []
        yData = []
        for row in self.newData:
            xData.append(row[0])
            yData.append(row[1])
        self.axes.plot(yData, xData,
                        linestyle="None",
                        marker=Constants.DEFAULT_POINT_SHAPE,
                        color=Constants.DEFAULT_POINT_COLOR,
                        markersize=Constants.DEFAULT_MARKER_SIZE_SMALL)
        self.graphWidget.draw()

    def rotate(self):
        i, j, angle = RotateDialog.defineRotation()
        newData = []
        matrix = self.formMatrix(self.data.columnCount(), angle, i, j)
        for row in self.newData:
            newRow = Row(row.getIndex(), row.matrixMultiply(matrix))
            newData.append(newRow)
        self.newData = newData
        self.refreshImage()

    def formMatrix(self, size, radangle, firstaxis, secondaxis):
        matrix = []
        firstRow = [0] * size
        firstRow[firstaxis] = math.cos(radangle)
        firstRow[secondaxis] = - math.sin(radangle)
        secondRow = [0] * size
        secondRow[firstaxis] = math.sin(radangle)
        secondRow[secondaxis] = math.cos(radangle)
        matrix.append(firstRow)
        matrix.append(secondRow)
        for i in range(size):
            if(i == firstaxis):
                matrix.append(firstRow)
            elif(i == secondaxis):
                matrix.append(secondRow)
            else:
                newRow = [0] * size
                newRow[i] = 1
                matrix.append(newRow)
        return matrix


class RotateDialog(QDialog):

    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout(self)
        self.description1 = QLabel("Задание плоскости вращения")
        self.layout.addWidget(self.description1)
        self.widgetGroup = QWidget()
        self.widgetGroupLayout = QHBoxLayout(self.widgetGroup)
        self.firstlabel = QLabel("X")
        self.firstedit = QLineEdit("1")
        self.secondlabel = QLabel("X")
        self.secondedit = QLineEdit("2")
        self.widgetGroupLayout.addWidget(self.firstlabel)
        self.widgetGroupLayout.addWidget(self.firstedit)
        self.widgetGroupLayout.addWidget(self.secondlabel)
        self.widgetGroupLayout.addWidget(self.secondedit)
        self.layout.addWidget(self.widgetGroup)
        self.description2 = QLabel("Задание угла")
        self.layout.addWidget(self.description2)
        self.angleedit = QLineEdit()
        self.layout.addWidget(self.angleedit)
        self.confirmationButton = QPushButton("Готово")
        self.confirmationButton.clicked.connect(self.accept)
        self.layout.addWidget(self.confirmationButton)
        self.setGeometry(200, 200, 0, 0)
        self.show()

    @staticmethod
    def defineRotation():
        dialog = RotateDialog()
        result = dialog.exec_()
        if result:
            try:
                i = int(dialog.firstedit.text())
                j = int(dialog.secondedit.text())
                angle = int(dialog.angleedit.text())
                return (i - 1, j - 1, angle * 0.0174533)
            except ValueError:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("Указаны некорректные данные")
                msg.setWindowTitle("Внимание")
                msg.exec_()
        return None

