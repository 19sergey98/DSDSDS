import random
import Utils
import Constants
import math

"""
Набор вспомогательных классов, используемых этой программой.
Здесь описаны классы: Data, Cluster, Row, Column, Point

"""


class Data:
    """ Объекты этого класса представляют собой табличный набор данных.
        Кластеры оперируют объектами типа Data.

    """
    def __init__(self, columns, rows=None):
        self._columns = columns
        if rows is None:
            self._rows = []
            for i, element in enumerate(self._columns[0]): #i - это строка
                rowArray = []
                for j in range (0, len(self._columns)):        #j - это колонка
                    rowArray.append(self._columns[j][i])
                self._rows.append(Row(i, rowArray))
        else:
            self._rows = rows
        self._rowCount = len(self._rows)
        self._columnCount = len(self._columns)
        self._columnNames = []
        for column in self._columns:
            self._columnNames.append(column.getName())

    def __getitem__(self, index):
        return self._rows[index]

    def __setitem__(self, index, value):
        self._rows[index] = value

    def __delitem__(self, index):
        del self._rows[index]

    # len на Data возвращает количество строк
    def __len__(self):
        return len(self._rows)

    def remove(self, item):
        self._rows.remove(item)

    def rowCount(self):
        return self._rowCount

    def getColumns(self):
        return self._columns

    def columnCount(self):
        return self._columnCount

    def getColumnNames(self):
        return self._columnNames

    def getSignificanceFactors(self):
        significancefactors = []
        for column in self._columns:
            if column.checkSignificance(): #TODO сделать нормально - еще на стадии приема данных проставлять 0 в вес незначимых колонока
                significancefactors.append(column.getWeight())
            else:
                significancefactors.append(0)
        return significancefactors

    def getSignificantColumns(self):
        significantcolumns = []
        for column in self._columns:
            if column.checkSignificance():
                significantcolumns.append(column)
        return significantcolumns

    def significantColumnCount(self):
        return len(self.getSignificantColumns())

    def getSignificantColumnNames(self):
        significantColumnNames = []
        for column in self.getSignificantColumns():
            significantColumnNames.append(column.getName())
        return significantColumnNames

    def getNameOfColumn(self, columnindex):
        return self._columnNames[columnindex]

    def getRowsByIndexSet(self, indexSet):
        rows = []
        for i in indexSet:
            rows.append(self._rows[i])
        return rows

    def addRow(self, row):
        self._rows.append(row)
        for i, column in enumerate(self._columns):
            column.append(row[i])

    def replaceData(self, rows):
        for i, row in enumerate(rows):
            self._rows[i] = Row(i, row)
            for j, element in enumerate(row):
                self._columns[j][i] = element

    @staticmethod
    def getIndexSet(rows):
        indexes = set()
        for row in rows:
            indexes.add(row.getIndex())
        return indexes

    @staticmethod
    def getIndexList(rows):
        indexes = []
        for row in rows:
            indexes.append(row.getIndex())
        return indexes

    def getRowByRowOriginalIndex(self, index):
        for row in self._rows:
            if row.getIndex() == index:
                return row
        return None


class GlobalData(Data):
    """ Расширение типа Data, подразумевает хранение всего набора точек, с которыми идет работа.

    """

    def getDummyCluster(self, clusters):

        # под словом dummyCluster имеются в виду все такие точки, которые не входят ни в один кластер
        # программа работает с ними, как с самостоятельным фантомным кластером. Просто так удобнее.
        """ Находит все точки, не принадлежащие ни одному кластеру.

        :param clusters: получает на вход массив всех кластеров
        :return: возвращает объект типа Cluster, представляющий из себя набор точек, не входящих ни в один существующий кластер
        """
        busyIndexes = set()
        allIndexes = set()
        for i in range(0, self.rowCount()):
            allIndexes.add(i)
        for cluster in clusters:
            busyIndexes = busyIndexes | cluster.getIndexSet()
        unbusyIndexes = allIndexes - busyIndexes
        rows = self.getRowsByIndexSet(unbusyIndexes)
        dummyCluster = Cluster(self.buildClusterDataFromRows(rows))
        dummyCluster.setColor(Constants.DEFAULT_POINT_COLOR)
        dummyCluster.setShapeKey('circle')
        dummyCluster.setName('dummyCluster')
        return dummyCluster

    def buildClusterDataFromRows(self, rows):
        indexset = Data.getIndexSet(rows)
        columns = self.buildColumnsFromIndexSet(indexset)
        return Data(columns, rows)

    def buildClusterDataFromIndexSet(self, indexset):
        rows = Data.getRowsByIndexSet(self, indexset)
        columns = self.buildColumnsFromIndexSet(indexset)
        return Data(columns, rows)

    def buildColumnsFromIndexSet(self, indexset):
        newcolumns = []
        for column in self.getColumns():
            newdata = []
            for element in indexset:
                newdata.append(column[element])
            newcolumn = Column(column.getName(), newdata, column.getIndex())
            newcolumns.append(newcolumn)
        return newcolumns


class Cluster:
    """ Класс, представляющий из себя кластер. Кластер содержит в качестве данных объект типа Data

    """
    def __init__(self, data):
        self._data = data
        self._name = "nameless cluster"
        colorRange = Constants.DEFAULT_COLOR_SET
        self._color = random.choice(colorRange)
        self._shapeKey = "circle"
        self._hidden = False

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    def __delitem__(self, index):
        del self._data[index]

    def __len__(self):
        return len(self._data)

    def setHidden(self, value):
        self._hidden = value
        for row in self._data:
            row.setHidden(value)

    def isHidden(self):
        return self._hidden

    def getName(self):
        return self._name

    def setName(self, name):
        self._name = name

    def getColor(self):
        return self._color

    def setColor(self, color):
        self._color = color

    def getShapeKey(self):
        return self._shapeKey

    def getShape(self):
        return Utils.getFlippedMarkerDictionary().get(self.getShapeKey())

    def setShapeKey(self, shapeKey):
        self._shapeKey = shapeKey

    def getSize(self):
        return len(self._data)

    def draw2DProjection(self, axes, xindex, yindex, markersize):
        """ Проецирует кластер на плоскость.

        :param axes: элемент библиотеки matplotlib на который происходит проекция
        :param xindex: переменная на оси X
        :param yindex: переменная на оси Y
        :return:
        """
        points = []
        xData = []
        yData = []
        for row in self._data:
            point = row.getProjection(xindex, yindex)
            points.append(point)
            if not point.isHidden():
                xData.append(point.getX())
                yData.append(point.getY())
        axes.plot(xData, yData,
                  linestyle="None",
                  marker=self.getShape(),
                  color=self.getColor(),
                  markersize = markersize)

    def draw2DProjection_by_given_points(self, axes, xindex, yindex, markersize, xD=[], yD=[]):
        """ Проецирует кластер на плоскость.

        :param axes: элемент библиотеки matplotlib на который происходит проекция
        :param xindex: переменная на оси X
        :param yindex: переменная на оси Y
        :return:
        """
        points = []
        xData = xD
        yData = yD

        axes.plot(xData, yData,
                  linestyle="None",
                  marker=self.getShape(),
                  color=self.getColor(),
                  markersize = markersize)

    def evaluateMassCenter(self):
        """ Рассчитывает центр масс кластера

        :return: Объект типа Row, представляющий из себя строку, составленную из координат центра масс
        """
        rowsAmount = len(self._data)
        if rowsAmount > 0:
            massCenterDataArray = [0] * len(self._data[0])
            for row in self._data:
                for i in range(0, len(row)):
                    massCenterDataArray[i] += row[i]
            massCenterDataArray[:] = [element / rowsAmount for element in massCenterDataArray]
            return Row(None, massCenterDataArray)
        else:
            return None

    def addRow(self, row):
        self._data.addRow(row)

    def getIndexSet(self):
        return Data.getIndexSet(self._data)

    def getInnerData(self):
        return self._data

    def remove(self, item):
        self._data.remove(item)


class Row:
    """ Класс представляет из себя строку данных, интерпретируемую как многомерная точка.
    Это удобнее чем просто массив, так как этот класс можно расширять по своему усмотрению.

    """
    def __init__(self, index, dataArray):
        """ Конструктор класса

        :param index: каждая строка имеет свой уникальный идентификатор - порядковый номер.
        Этот идентификатор очень важен для работы программы
        :param dataArray: массив данных
        """
        self._index = index
        self._dataArray = dataArray
        self._hidden = False

    def __getitem__(self, index):
        return self._dataArray[index]

    def __setitem__(self, index, value):
        self._dataArray[index] = value

    def __delitem__(self, index):
        del self._dataArray[index]

    def __len__(self):
        if self._dataArray is not None:
            return len(self._dataArray)
        else:
            return None

    def getIndex(self):
        return self._index

    def setIndex(self, index):
        self.index = index

    def setDataArray(self, dataArray):
        self._dataArray = dataArray

    def setHidden(self, value):
        self._hidden = value

    def isHidden(self):
        return self._hidden

    def getProjection(self, i, j):
        """ Двумерная проекция строки по координатам c индексами i и j

        :param i: координата точки на оси X
        :param j: координата точки на оси Y
        :return: объект типа Point, представляющий из себя точку на плоскости.
        """
        x = self._dataArray[i]
        y = self._dataArray[j]
        point = Point(x, y, self._index)
        point.setHidden(self._hidden) # если колонка является скрытой, то и ее проекция тоже будет скрытой
        return point

    def distanceTo(self, anotherRow, significancefactors):
        """ Рассчитывает евклидово расстояние между этой многомерной точкой и какой-то другой.
        Учитывает коэффициенты значимости!

        :param anotherRow: другая многомерная точка
        :param significancefactors: массив с коэффициентами значимости
        :return: возвращает число - расстояние
        """
        sumOfSquares = 0
        for i, element in enumerate(self._dataArray):
            sumOfSquares += (element - anotherRow[i]) * (element - anotherRow[i]) * \
                            significancefactors[i] * significancefactors[i]
        return math.sqrt(sumOfSquares)

    def manhattanDistanceTo(self, anotherRow, significancefactors):
        """Рассчитывает манхэттенское расстояние между этой многомерной точкой и какой-то другой.
        Учитывает коэффициенты значимости!

        :param anotherRow: другая многомерная точка
        :param significancefactors: массив с коэффициентами значимости
        :return: возвращает число - расстояние
        """
        sum = 0
        for i, element in enumerate(self._dataArray):
            sum += abs((element - anotherRow[i]) * significancefactors[i])
        return sum

    def matrixMultiply(self, matrix):
        rowToReturn = []
        for matrixRow in matrix:
            newElement = 0
            for i, element in enumerate(matrixRow):
                newElement += element * self._dataArray[i]
            rowToReturn.append(newElement)
        return rowToReturn #TODO возвращать объект типа Row вместо просто массива


class Column:
    """ Класс представляет из себя колонку данных.
    Это удобнее чем просто массив, так как этот класс можно расширять по своему усмотрению.

    """
    def __init__(self, name, data, index):
        """ Конструктор класса

        :param name: имя переменной (колонки)
        :param data: массив данных
        :param index: номер колонки
        """

        # _weight - весовой коэффициент или коэффициент значимости. Влияет на значомость этой колонки, при рассчетах расстояний.
        # Вес колонки задается при открытии файла в окне предобработки данных.
        self._name = name
        self._data = data
        self._index = index
        self._isSignificant = True
        self._weight = 1

    def __getitem__(self, index):
        return self._data[index]

    def __setitem__(self, index, value):
        self._data[index] = value

    def __delitem__(self, index):
        del self._data[index]

    def __len__(self):
        return len(self._data)

    def getName(self):
        return self._name

    def getIndex(self):
        return self._index

    def setSignificance(self, boolvalue):
        self._isSignificant = boolvalue

    def checkSignificance(self):
        return self._isSignificant

    def getAverageValue(self):
        if len(self._data) !=0:
            return sum(self._data)/len(self._data)
        else:
            return 0

    def getStandartDeviation(self):
        averagevalue = self.getAverageValue()
        standartdeviation = 0
        for element in self._data:
            standartdeviation += (averagevalue - element) * (averagevalue - element)
        standartdeviation = math.sqrt(standartdeviation / len(self._data))
        return standartdeviation

    def setWeight(self, value):
        self._weight = value

    def getWeight(self):
        return self._weight

    def append(self, value):
        self._data.append(value)


class Point:
    """ Простой класс, представляющий из себя двумерную точку на плоскости.

    """
    def __init__(self, x, y, index):
        self._x = x
        self._y = y
        self._index = index
        self._hidden = False

    def __len__(self):
        return 2

    def getX(self):
        return self._x

    def getY(self):
        return self._y

    def getIndex(self):
        return self._index

    def setHidden(self, value):
        self._hidden = value

    def isHidden(self):
        return self._hidden



