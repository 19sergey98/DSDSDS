
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *



class DataPreviewWindow(QDialog):

    def __init__(self, data):
        super().__init__()
        self.processedData = data

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.buttonGroup = QTableWidget()
        self.buttonGroup.horizontalHeader().setVisible(False)
        self.buttonGroup.verticalHeader().setVisible(False)
        self.buttonGroup.setShowGrid(False)
        self.buttonGroup.setContentsMargins(0,0,0,0)
        self.adjustmentscompleted = QPushButton("Готово")
        self.adjustmentscompleted.clicked.connect(self.accept)
        self.cancelbutton = QPushButton("Отмена")
        self.cancelbutton.clicked.connect(self.reject)
        self.normalisebutton = QPushButton("Нормализовать")
        self.normalisebutton.clicked.connect(self.normalisePressed)
        self.normalisebutton.setEnabled(False) # TODO Временно убрал нормализацию
        self.buttonGroup.setColumnCount(1)
        self.buttonGroup.setRowCount(3)
        self.buttonGroup.setCellWidget(0, 0, self.adjustmentscompleted)
        self.buttonGroup.setCellWidget(1, 0, self.cancelbutton)
        self.buttonGroup.setCellWidget(2, 0, self.normalisebutton)
        self.buttonGroup.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Expanding)


        self.dataPreviewTable = QTableWidget()
        self.dataPreviewTable.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.layout.addWidget(self.buttonGroup, 2)
        self.layout.addWidget(self.dataPreviewTable, 11)
        self.initdatapreview()
        self.setWindowTitle("Предпросмотр данных")
        if data.columnCount() > 10:
            self.resize(680, 40*10 + 60)
        else:
            self.resize(680, 40*data.columnCount() + 60)
        self.show()

    def initdatapreview(self):
        self.dataPreviewTable.setRowCount(0)
        self.dataPreviewTable.setColumnCount(5)
        self.dataPreviewTable.setRowCount(self.processedData.columnCount())
        self.dataPreviewTable.setHorizontalHeaderLabels(["Колонка", "Среднее\nзначение","Среднеквадратичное\nотклонение",
                                                         "Весовой\n коэффициент", "Включить в\nрассмотрение?"
                                                         ])
        columnheaders = self.processedData.getColumnNames()
        for i, column in enumerate(self.processedData.getColumns()):
            self.dataPreviewTable.setItem(i, 0, QTableWidgetItem(columnheaders[i]))
            self.dataPreviewTable.setItem(i, 1, QTableWidgetItem(str(column.getAverageValue())))
            self.dataPreviewTable.setItem(i, 2, QTableWidgetItem(str(column.getStandartDeviation())))

            weighteditor = QLineEdit(str(column.getWeight()))
            weighteditor.editingFinished.connect(lambda column=column, weighteditor=weighteditor: self.adjustweight(column, weighteditor))
            self.dataPreviewTable.setCellWidget(i, 3, weighteditor)
            checkboxcontainer = QWidget()
            checkboxcontainer.setStyleSheet("background-color:#cccccc;")
            containerlayout = QVBoxLayout(checkboxcontainer)
            containerlayout.setAlignment(Qt.AlignCenter)
            checkbox = QCheckBox("Да")
            containerlayout.addWidget(checkbox)
            self.dataPreviewTable.setCellWidget(i, 4, checkboxcontainer)
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda event, column=column, checkbox=checkbox: self.checkboxstatechanged(column, checkbox))
        self.dataPreviewTable.resizeColumnsToContents()

    def checkboxstatechanged(self, column, checkbox):
        if checkbox.isChecked():
            checkbox.setText("Да")
            column.setSignificance(True)
        else:
            checkbox.setText("Нет")
            column.setSignificance(False)

    def adjustweight(self, column, lineedit):
        try:
            value = int(lineedit.text())
            column.setWeight(value)
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Весовой коэффициент задан некорректно")
            msg.setWindowTitle("Внимание")
            msg.exec_()
            lineedit.setText("1")

    def normalisePressed(self):
        rows = list(self.processedData)
        arrayOfArrays = []
        for row in rows:
            arrayOfArrays.append(list(row))
        # normalisedArrayOfArrays = normalize(arrayOfArrays, norm = 'l2').tolist()
        # self.processedData.replaceData(normalisedArrayOfArrays)
        self.initdatapreview() # TODO почему таблица не обновляется?

    @staticmethod
    def preprocessData(data):
        dialog = DataPreviewWindow(data)
        result = dialog.exec_()
        if result:
            return dialog.processedData
        return None



