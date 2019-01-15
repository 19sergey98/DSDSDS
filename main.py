
import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from MainInterface import MainWindow

sys._excepthook = sys.excepthook

def my_exception_hook(exctype, value, traceback):
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Warning)
    msg.setText(str(value))
    msg.setInformativeText(str(traceback))
    msg.setWindowTitle(str(exctype))
    msg.exec_()
    # Print the error and traceback
    print(exctype, value, traceback)
    # Call the normal Exception hook after
    sys._excepthook(exctype, value, traceback)
    sys.exit(1)


""" Это точка старта программы. 
В идее проблемы с выводом питоновских исключений. 
Поэтому поток вывода исключений вручную явно перенаправлен в консоль. my_exception_hook нужен для этого
Помимо консоли, исключения в каком-то виде еще и показываются интерфейсом в QMessageBox

"""
if __name__ == '__main__':
    sys.excepthook = my_exception_hook
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())


