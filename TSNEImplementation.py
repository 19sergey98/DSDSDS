from PyQt5.QtWidgets import *
from UtilityClasses import Cluster
import Constants
import numpy as np
import pylab
import matplotlib.pyplot as plt
import pyglet
import time
import os
import copy


class TSNEWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__(parent)

        # Глобальные переменные для пошагового исполнения алгоритма.
        # Для того чтобы выполнить шаг нужно помнить состояние достигнутое прыдыдущими шагами.
        # Это состояние хранится в следующих переменных

        self.max_iteration = 1000
        self.perplexity = 30.0
        self.tsne_error = 0
        self.frames_amount = 200
        self.frames_path_prefix = 'tempimages/foo'
        self.frames_list_paths=[]
        self.frames_list=[]

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
        self.perplexityLabel = QLabel("Perplexity")
        self.perplexityEdit = QLineEdit()
        self.max_iterationLabel = QLabel("Число итераций")
        self.max_iterationEdit = QLineEdit()
        self.pics_iterationLabel = QLabel("Количество кадров")
        self.pics_iterationEdit = QLineEdit()
        self.layout.addWidget(self.perplexityLabel)
        self.layout.addWidget(self.perplexityEdit)
        self.layout.addWidget(self.max_iterationLabel)
        self.layout.addWidget(self.max_iterationEdit)

        self.confirmationButton = QPushButton("Выполнить алгоритм")
        self.confirmationButton.clicked.connect(self.performAlgorithm)
        self.layout.addWidget(self.confirmationButton)

        self.setGeometry(100, 100, 200, 200)
        self.setWindowTitle("t-SNE")
        self.show()

    # algorithm
    def performAlgorithm(self):
        if self.prepareData():
            a = []
            # a = np.array(a)
            for i in range(len(self.rowsToClusterize)):
                for j in range(len(self.rowsToClusterize.__getitem__(i))):
                    a.append(self.rowsToClusterize.__getitem__(i).__getitem__(j))

            data_numpy_array = np.array(a)
            data_numpy_array = np.reshape(data_numpy_array, (-1, len(self.rowsToClusterize.__getitem__(0))))
            print(data_numpy_array)
            result = self.tsne(data_numpy_array, 2, len(self.rowsToClusterize.__getitem__(0)), self.perplexity, self.max_iteration, 1)
            print("x=", data_numpy_array)
            print("y=", result)
            print("ошибка= ", self.tsne_error)

            # ОТРИСОВКА АНИМАЦИИ

            animation = pyglet.image.Animation.from_image_sequence(self.frames_list, 0.25, loop=False)
            # Создаем спрайт объект
            animSprite = pyglet.sprite.Sprite(animation)
            # Главное окно Pyglet
            w = animSprite.width
            h = animSprite.height
            win = pyglet.window.Window(width=w, height=h)
            # Устанавливаем булый цвет фона
            pyglet.gl.glClearColor(1, 1, 1, 1)

            @ win.event
            def on_draw():
                win.clear()
                animSprite.draw()
            pyglet.app.run()

           # self.remove_all_frames()


            '''
            for i in range(len(data_numpy_array)):
                for j in range(len(data_numpy_array.__getitem__(i))):
                    print()
            '''

    #def update_frames(dt):
     #   global counter
    #    counter = (counter + dt) % 2

    def prepareData(self):
        """ Подготавилвает данные, нужные для работы алгоритма

        :return: возвращает True если подготовка выполнена успешно и False в противном случае
        """
        try:
            self.perplexity = float(self.perplexityEdit.text())
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("perplexity задан некорректно")
            msg.setWindowTitle("Внимание")
            msg.exec_()
            return False
        try:
            self.max_iteration = int(self.max_iterationEdit.text())
        except ValueError:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText("Число итераций задано некорректно")
            msg.setWindowTitle("Внимание")
            msg.exec_()
            return False
        self.workData = self.parent().globalData
        self.rowsToClusterize = list(self.workData)
        self.resultClusters = []
        self.supposedClusterElems = set()
        return True

    def remove_all_frames(self):
        for i in range(self.frames_amount+1):
            if os.path.exists(self.frames_path_prefix+str(i)+'.png'):
                os.remove(self.frames_path_prefix + str(i) + '.png')
            else:
                print("попытка удалить несуществующий файл: " + self.frames_path_prefix+str(i)+'.png')

# реализация алгоритма t-sne
    @staticmethod
    def  Hbeta(D=np.array([]), beta=1.0):
        """
            Compute the perplexity and the P-row for a specific value of the
            precision of a Gaussian distribution.
        """
        # Compute P-row and corresponding perplexity
        P = np.exp(-D.copy() * beta)
        sumP = sum(P)
        H = np.log(sumP) + beta * np.sum(D * P) / sumP
        P = P / sumP
        return H, P

    @staticmethod
    def x2p(X=np.array([]), tol=1e-5, perplexity=30.0):
        """
            Performs a binary search to get P-values in such a way that each
            conditional Gaussian has the same perplexity.
        """

        # Initialize some variables
        print("Computing pairwise distances...")
        (n, d) = X.shape
        sum_X = np.sum(np.square(X), 1)
        D = np.add(np.add(-2 * np.dot(X, X.T), sum_X).T, sum_X)
        P = np.zeros((n, n))
        beta = np.ones((n, 1))
        logU = np.log(perplexity)

        # Loop over all datapoints
        for i in range(n):

            # Print progress
            if i % 500 == 0:
                print("Computing P-values for point %d of %d..." % (i, n))

            # Compute the Gaussian kernel and entropy for the current precision
            betamin = -np.inf
            betamax = np.inf
            Di = D[i, np.concatenate((np.r_[0:i], np.r_[i + 1:n]))]
            (H, thisP) = TSNEWindow.Hbeta(Di, beta[i])

            # Evaluate whether the perplexity is within tolerance
            Hdiff = H - logU
            tries = 0
            while np.abs(Hdiff) > tol and tries < 50:

                # If not, increase or decrease precision
                if Hdiff > 0:
                    betamin = beta[i].copy()
                    if betamax == np.inf or betamax == -np.inf:
                        beta[i] = beta[i] * 2.
                    else:
                        beta[i] = (beta[i] + betamax) / 2.
                else:
                    betamax = beta[i].copy()
                    if betamin == np.inf or betamin == -np.inf:
                        beta[i] = beta[i] / 2.
                    else:
                        beta[i] = (beta[i] + betamin) / 2.

                # Recompute the values
                (H, thisP) = TSNEWindow.Hbeta(Di, beta[i])
                Hdiff = H - logU
                tries += 1

            # Set the final row of P
            P[i, np.concatenate((np.r_[0:i], np.r_[i + 1:n]))] = thisP

        # Return final P-matrix
        print("Mean value of sigma: %f" % np.mean(np.sqrt(1 / beta)))
        return P

    @staticmethod
    def pca(X=np.array([]), no_dims=50):
        """
            Runs PCA on the NxD array X in order to reduce its dimensionality to
            no_dims dimensions.
        """

        print("Preprocessing the data using PCA...")
        (n, d) = X.shape
        X = X - np.tile(np.mean(X, 0), (n, 1))
        (l, M) = np.linalg.eig(np.dot(X.T, X))
        Y = np.dot(X, M[:, 0:no_dims])
        return Y

    def tsne(self, X=np.array([]), no_dims=2, initial_dims=50, perplexity=30.0, max_iteration=1000, draw_image=0):
        """
            Runs t-SNE on the dataset in the NxD array X to reduce its
            dimensionality to no_dims dimensions. The syntaxis of the function is
            `Y = tsne.tsne(X, no_dims, perplexity), where X is an NxD NumPy array.
        """
        # индекс для сохранения изображений
        current_index = 0
        shift = self.max_iteration // self.frames_amount

        # Check inputs
        if isinstance(no_dims, float):
            print("Error: array X should have type float.")
            return -1
        if round(no_dims) != no_dims:
            print("Error: number of dimensions should be an integer.")
            return -1

        # Initialize variables
        X = TSNEWindow.pca(X, initial_dims).real
        (n, d) = X.shape
        max_iter = max_iteration
        initial_momentum = 0.5
        final_momentum = 0.8
        eta = 500
        min_gain = 0.01
        Y = np.random.randn(n, no_dims)
        dY = np.zeros((n, no_dims))
        iY = np.zeros((n, no_dims))
        gains = np.ones((n, no_dims))

        # Compute P-values
        P = TSNEWindow.x2p(X, 1e-5, perplexity)
        P = P + np.transpose(P)
        P = P / np.sum(P)
        P = P * 4.  # early exaggeration
        P = np.maximum(P, 1e-12)

        # Подкотовка изображений

        # Run iterations
        for iter in range(max_iter):

            # Compute pairwise affinities
            sum_Y = np.sum(np.square(Y), 1)
            num = -2. * np.dot(Y, Y.T)
            num = 1. / (1. + np.add(np.add(num, sum_Y).T, sum_Y))
            num[range(n), range(n)] = 0.
            Q = num / np.sum(num)
            Q = np.maximum(Q, 1e-12)

            # Compute gradient
            PQ = P - Q
            for i in range(n):
                dY[i, :] = np.sum(np.tile(PQ[:, i] * num[:, i], (no_dims, 1)).T * (Y[i, :] - Y), 0)

            # Perform the update
            if iter < 20:
                momentum = initial_momentum
            else:
                momentum = final_momentum
            gains = (gains + 0.2) * ((dY > 0.) != (iY > 0.)) + \
                    (gains * 0.8) * ((dY > 0.) == (iY > 0.))
            gains[gains < min_gain] = min_gain
            iY = momentum * iY - eta * (gains * dY)
            Y = Y + iY
            Y = Y - np.tile(np.mean(Y, 0), (n, 1))

            # Compute current value of cost function
            if (iter + 1) % 10 == 0:
                C = np.sum(P * np.log(P / Q))
                print("Iteration %d: error is %f" % (iter + 1, C))
                self.tsne_error = C # error saving
            # Stop lying about P-values
            if iter == 100:
                P = P / 4.

            # сохраняем рисунки для анимации
            if draw_image != 0:
                if iter % shift == 0:
                    pylab.scatter(Y[:, 0], Y[:, 1], c='r')
                #
                    pylab.savefig(self.frames_path_prefix+str(current_index)+'.png')
                    pylab.gcf().clear()  # очистка плота

                    # добавляем текушее изображение в последовательность кадров
                    current_img = pyglet.image.load(self.frames_path_prefix+str(current_index)+'.png')
                    self.frames_list.append(current_img)

                    # удаляем изображение сразу
                    if os.path.exists(self.frames_path_prefix+str(current_index)+'.png'):
                        os.remove(self.frames_path_prefix+str(current_index)+'.png')

                    #self.frames_list_paths.append(self.frames_path_prefix+str(current_index)+'.png')
                    #print("сохранено изображение номер"+str(current_index))
                    current_index += 1

        # Return solution
        return Y

