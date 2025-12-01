# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'resultinterface.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QDialog, QFrame,
    QLabel, QPushButton, QSizePolicy, QWidget)

from qcustomplot import QCustomPlot

class Ui_ResultInterface(object):
    def setupUi(self, ResultInterface):
        if not ResultInterface.objectName():
            ResultInterface.setObjectName(u"ResultInterface")
        ResultInterface.resize(650, 500)
        ResultInterface.setMaximumSize(QSize(16777215, 16777215))
        self.customPlot = QCustomPlot(ResultInterface)
        self.customPlot.setObjectName(u"customPlot")
        self.customPlot.setGeometry(QRect(20, 20, 601, 251))
        self.voltage_button = QPushButton(ResultInterface)
        self.voltage_button.setObjectName(u"voltage_button")
        self.voltage_button.setGeometry(QRect(40, 340, 89, 25))
        self.label = QLabel(ResultInterface)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(40, 290, 161, 41))
        font = QFont()
        font.setPointSize(13)
        self.label.setFont(font)
        self.line = QFrame(ResultInterface)
        self.line.setObjectName(u"line")
        self.line.setGeometry(QRect(210, 280, 20, 211))
        self.line.setFrameShape(QFrame.Shape.VLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)
        self.label_2 = QLabel(ResultInterface)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setGeometry(QRect(230, 280, 241, 41))
        font1 = QFont()
        font1.setPointSize(12)
        self.label_2.setFont(font1)
        self.file_path_label = QLabel(ResultInterface)
        self.file_path_label.setObjectName(u"file_path_label")
        self.file_path_label.setGeometry(QRect(230, 330, 381, 21))
        self.choose_file_button = QPushButton(ResultInterface)
        self.choose_file_button.setObjectName(u"choose_file_button")
        self.choose_file_button.setGeometry(QRect(470, 290, 89, 25))
        self.label_3 = QLabel(ResultInterface)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(230, 370, 421, 17))
        self.label_4 = QLabel(ResultInterface)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(230, 400, 31, 17))
        self.label_5 = QLabel(ResultInterface)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setGeometry(QRect(230, 440, 31, 17))
        self.view_another_button = QPushButton(ResultInterface)
        self.view_another_button.setObjectName(u"view_another_button")
        self.view_another_button.setEnabled(False)
        self.view_another_button.setGeometry(QRect(470, 440, 89, 25))
        self.comboBox_x = QComboBox(ResultInterface)
        self.comboBox_x.setObjectName(u"comboBox_x")
        self.comboBox_x.setGeometry(QRect(250, 400, 161, 25))
        self.comboBox_y = QComboBox(ResultInterface)
        self.comboBox_y.setObjectName(u"comboBox_y")
        self.comboBox_y.setGeometry(QRect(250, 440, 161, 25))

        self.retranslateUi(ResultInterface)

        QMetaObject.connectSlotsByName(ResultInterface)
    # setupUi

    def retranslateUi(self, ResultInterface):
        ResultInterface.setWindowTitle(QCoreApplication.translate("ResultInterface", u"Dialog", None))
        self.voltage_button.setText(QCoreApplication.translate("ResultInterface", u"View", None))
        self.label.setText(QCoreApplication.translate("ResultInterface", u"Voltage-time plot", None))
        self.label_2.setText(QCoreApplication.translate("ResultInterface", u"View other results", None))
        self.file_path_label.setText(QCoreApplication.translate("ResultInterface", u"File path...", None))
        self.choose_file_button.setText(QCoreApplication.translate("ResultInterface", u"Choose", None))
        self.label_3.setText(QCoreApplication.translate("ResultInterface", u"Choose two columns  data you want to use as x and y", None))
        self.label_4.setText(QCoreApplication.translate("ResultInterface", u"X", None))
        self.label_5.setText(QCoreApplication.translate("ResultInterface", u"Y", None))
        self.view_another_button.setText(QCoreApplication.translate("ResultInterface", u"View", None))
    # retranslateUi

