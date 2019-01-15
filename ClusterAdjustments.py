from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from UtilityClasses import Cluster, GlobalData
import Utils

class ClusterDialog(QDialog):
    """ В этом окне можно менять имя кластера, цвет и форму его маркера

    """

    def __init__(self, cluster):
        super().__init__()
        self.cluster = cluster
        self.layout = QVBoxLayout(self)
        self.clusterNameLine = QLineEdit()
        self.clusterNameLine.setPlaceholderText("Задать имя кластера")
        self.layout.addWidget(self.clusterNameLine)
        self.colorGroup = QGroupBox("Цвет маркера")
        self.colorGroupLayout = QHBoxLayout(self.colorGroup)
        self.chooseColorButton = QPushButton("Изменить цвет")
        self.chooseColorButton.clicked.connect(self.onColorChosen)
        self.colorLabel = QLabel(self.cluster.getColor())
        self.colorLabel.setStyleSheet('background-color: %s; border: 1px solid black; border-radius: 10px;' % self.cluster.getColor() )
        self.colorGroupLayout.addWidget(self.chooseColorButton)
        self.colorGroupLayout.addWidget(self.colorLabel)
        self.colorGroupLayout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.colorGroup)
        self.shapeChoiceGroup = QGroupBox("Форма маркера")
        self.shapeChoiceGroupLayout = QHBoxLayout(self.shapeChoiceGroup)
        self.shapeChoiceGroupLayout.setContentsMargins(0, 0, 0, 0)
        self.shapeChoice = QComboBox()
        self.shapeChoice.addItems(Utils.getFlippedMarkerDictionary().keys())
        self.shapeChoice.setCurrentIndex(self.shapeChoice.findText(self.cluster.getShapeKey()))
        self.shapeChoice.currentIndexChanged.connect(self.onShapeChanged)
        self.figure = Figure()
        self.graph = FigureCanvas(self.figure)
        self.graph.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
        self.axes = self.figure.add_subplot(111)
        self.axes.axis("off")
        self.markerSize = 8
        self.axes.plot([1], [1], linestyle = "None", marker = "o", color = self.cluster.getColor(), markersize = self.markerSize)
        self.graph.draw()
        self.shapeChoiceGroupLayout.addWidget(self.shapeChoice)
        self.shapeChoiceGroupLayout.addWidget(self.graph)
        self.layout.addWidget(self.shapeChoiceGroup)
        self.buttonGroup = QWidget()
        self.buttonGroupLayout = QHBoxLayout(self.buttonGroup)
        self.clusterCompleteButton = QPushButton("Готово")
        self.clusterCompleteButton.clicked.connect(self.accept)
        self.cancelButton = QPushButton("Отменить")
        self.cancelButton.clicked.connect(self.reject)
        self.buttonGroupLayout.addWidget(self.clusterCompleteButton)
        self.buttonGroupLayout.addWidget(self.cancelButton)
        self.layout.addWidget(self.buttonGroup)
        self.resize(250, 150)
        self.setMinimumWidth(250)
        self.setWindowTitle("Кластер")
        self.show()

    @classmethod
    def fromData(cls, data):
        cluster = Cluster(data)
        dialog = cls(cluster)
        return dialog

    @staticmethod
    def newCluster(data):
        dialog = ClusterDialog.fromData(data)
        result = dialog.exec_()
        if result:
            return dialog.clusterCompleted()
        return None

    @staticmethod
    def adjustCluster(cluster):
        dialog = ClusterDialog(cluster)
        result = dialog.exec_()
        if result:
            return dialog.clusterCompleted()
        return None

    def clusterCompleted(self):
        if len(self.clusterNameLine.text()) != 0:
            self.cluster.setName(self.clusterNameLine.text())
        return self.cluster

    def onColorChosen(self):
        color = QColorDialog.getColor()
        self.cluster.setColor(color.name())
        self.colorLabel.setText(color.name())
        self.colorLabel.setStyleSheet(
            'background-color: %s; border: 1px solid black; border-radius: 10px;' % color.name())
        self.onShapeChanged()

    def onShapeChanged(self):
        shapeKey = self.shapeChoice.currentText()
        self.cluster.setShapeKey(shapeKey)
        self.axes.cla()
        self.axes.axis("off")
        shapeValue = Utils.getFlippedMarkerDictionary().get(self.cluster.getShapeKey())
        self.axes.plot([1], [1], linestyle="None", marker=shapeValue, color=self.cluster.getColor(), markersize = self.markerSize)
        self.graph.draw()
