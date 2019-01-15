from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class ScaleAdjustmentsView(QMainWindow):
    """ Это окно для смены масштаба рассматриваемого графика.

    """

    def __init__(self, parent, axes):
        super().__init__(parent)
        self.axes = axes
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralLayout = QVBoxLayout(self.centralWidget)

        self.xgroup = QGroupBox("Ось X")
        self.xgroupLayout = QGridLayout(self.xgroup)
        self.xstartlabel = QLabel("Начало оси:")
        self.xendlabel = QLabel("Конец оси:")
        self.xstartfield = QLineEdit(str(self.axes.get_xlim()[0]))
        self.xendfield = QLineEdit(str(self.axes.get_xlim()[1]))
        self.xgroupLayout.addWidget(self.xstartlabel, 1, 1)
        self.xgroupLayout.addWidget(self.xendlabel, 2, 1)
        self.xgroupLayout.addWidget(self.xstartfield, 1, 2)
        self.xgroupLayout.addWidget(self.xendfield, 2, 2)
        self.centralLayout.addWidget(self.xgroup)

        self.ygroup = QGroupBox("Ось Y")
        self.ygroupLayout = QGridLayout(self.ygroup)
        self.ystartlabel = QLabel("Начало оси:")
        self.yendlabel = QLabel("Конец оси:")
        self.ystartfield = QLineEdit(str(self.axes.get_ylim()[0]))
        self.yendfield = QLineEdit(str(self.axes.get_ylim()[1]))
        self.ygroupLayout.addWidget(self.ystartlabel, 1, 1)
        self.ygroupLayout.addWidget(self.yendlabel, 2, 1)
        self.ygroupLayout.addWidget(self.ystartfield, 1, 2)
        self.ygroupLayout.addWidget(self.yendfield, 2, 2)
        self.centralLayout.addWidget(self.ygroup)

        self.buttongroup = QWidget()
        self.buttonlayout = QHBoxLayout(self.buttongroup)
        self.okbutton = QPushButton("Готово")
        self.okbutton.clicked.connect(self.okbuttonclicked)
        self.cancelbutton = QPushButton("Отмена")
        self.cancelbutton.clicked.connect(self.cancelbuttonclicked)
        self.buttonlayout.addWidget(self.okbutton)
        self.buttonlayout.addWidget(self.cancelbutton)
        self.centralLayout.addWidget(self.buttongroup)

        self.resetbutton = QPushButton("Установить масштаб по умолчанию")
        self.resetbutton.clicked.connect(self.resetscaling)
        self.centralLayout.addWidget(self.resetbutton)

        self.setWindowTitle("Масштабирование")
        self.show()

    def cancelbuttonclicked(self):
        self.close()

    def okbuttonclicked(self):
        try:
            xstart = float(self.xstartfield.text())
            xend = float(self.xendfield.text())
            ystart = float(self.ystartfield.text())
            yend = float(self.yendfield.text())
            self.axes.set_xlim([xstart, xend])
            self.axes.set_ylim([ystart, yend])
            self.parent().graphWidget.draw()
            self.close()
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Ошибка")
            msg.setInformativeText("Допускаются только числовые значения")
            msg.setWindowTitle("Внимание")
            msg.exec_()

    def resetscaling(self):
        self.axes.relim()
        self.axes.autoscale()
        self.parent().graphWidget.draw()
        self.close()










