# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QLabel, QLineEdit,
    QMainWindow, QMenuBar, QPushButton, QRadioButton,
    QSizePolicy, QStatusBar, QTabWidget, QTextBrowser,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(800, 640)
        MainWindow.setMinimumSize(QSize(800, 640))
        MainWindow.setMaximumSize(QSize(800, 640))
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.intro_browser = QTextBrowser(self.centralwidget)
        self.intro_browser.setObjectName(u"intro_browser")
        self.intro_browser.setGeometry(QRect(150, 0, 651, 191))
        self.intro_browser.setOpenExternalLinks(False)
        self.label_pic_vertical = QLabel(self.centralwidget)
        self.label_pic_vertical.setObjectName(u"label_pic_vertical")
        self.label_pic_vertical.setGeometry(QRect(0, 0, 151, 601))
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tabWidget.setGeometry(QRect(150, 200, 651, 390))
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.label_5 = QLabel(self.tab)
        self.label_5.setObjectName(u"label_5")
        self.label_5.setEnabled(True)
        self.label_5.setGeometry(QRect(10, 30, 221, 17))
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.label_5.setFont(font)
        self.label = QLabel(self.tab)
        self.label.setObjectName(u"label")
        self.label.setGeometry(QRect(10, 210, 291, 17))
        self.carbon_button = QRadioButton(self.tab)
        self.carbon_button.setObjectName(u"carbon_button")
        self.carbon_button.setGeometry(QRect(10, 240, 211, 23))
        self.line_5 = QFrame(self.tab)
        self.line_5.setObjectName(u"line_5")
        self.line_5.setGeometry(QRect(10, 190, 171, 20))
        self.line_5.setFrameShape(QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_path_label = QLabel(self.tab)
        self.main_path_label.setObjectName(u"main_path_label")
        self.main_path_label.setGeometry(QRect(10, 70, 351, 21))
        self.main_next_button = QPushButton(self.tab)
        self.main_next_button.setObjectName(u"main_next_button")
        self.main_next_button.setEnabled(False)
        self.main_next_button.setGeometry(QRect(540, 330, 89, 25))
        self.halfCell_button = QRadioButton(self.tab)
        self.halfCell_button.setObjectName(u"halfCell_button")
        self.halfCell_button.setGeometry(QRect(230, 240, 201, 23))
        self.label_3 = QLabel(self.tab)
        self.label_3.setObjectName(u"label_3")
        self.label_3.setGeometry(QRect(10, 120, 191, 17))
        self.main_path_button = QPushButton(self.tab)
        self.main_path_button.setObjectName(u"main_path_button")
        self.main_path_button.setGeometry(QRect(380, 70, 89, 25))
        self.pro_name_editline = QLineEdit(self.tab)
        self.pro_name_editline.setObjectName(u"pro_name_editline")
        self.pro_name_editline.setGeometry(QRect(10, 150, 113, 25))
        self.line_4 = QFrame(self.tab)
        self.line_4.setObjectName(u"line_4")
        self.line_4.setGeometry(QRect(10, 100, 171, 20))
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)
        self.main_name_hint = QPushButton(self.tab)
        self.main_name_hint.setObjectName(u"main_name_hint")
        self.main_name_hint.setGeometry(QRect(210, 120, 25, 25))
        self.fullCell_button = QRadioButton(self.tab)
        self.fullCell_button.setObjectName(u"fullCell_button")
        self.fullCell_button.setGeometry(QRect(230, 290, 201, 23))
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.label_6 = QLabel(self.tab_2)
        self.label_6.setObjectName(u"label_6")
        self.label_6.setEnabled(True)
        self.label_6.setGeometry(QRect(10, 30, 241, 17))
        self.label_6.setFont(font)
        self.label_4 = QLabel(self.tab_2)
        self.label_4.setObjectName(u"label_4")
        self.label_4.setGeometry(QRect(10, 60, 241, 17))
        font1 = QFont()
        font1.setBold(False)
        self.label_4.setFont(font1)
        self.main_path_label_2 = QLabel(self.tab_2)
        self.main_path_label_2.setObjectName(u"main_path_label_2")
        self.main_path_label_2.setGeometry(QRect(10, 90, 301, 31))
        self.main_path_button_2 = QPushButton(self.tab_2)
        self.main_path_button_2.setObjectName(u"main_path_button_2")
        self.main_path_button_2.setGeometry(QRect(350, 90, 89, 25))
        self.main_next_button_2 = QPushButton(self.tab_2)
        self.main_next_button_2.setObjectName(u"main_next_button_2")
        self.main_next_button_2.setEnabled(False)
        self.main_next_button_2.setGeometry(QRect(540, 330, 89, 25))
        self.label_7 = QLabel(self.tab_2)
        self.label_7.setObjectName(u"label_7")
        self.label_7.setGeometry(QRect(10, 150, 271, 21))
        self.recent_path_label = QLabel(self.tab_2)
        self.recent_path_label.setObjectName(u"recent_path_label")
        self.recent_path_label.setGeometry(QRect(10, 180, 301, 31))
        self.recent_path_button = QPushButton(self.tab_2)
        self.recent_path_button.setObjectName(u"recent_path_button")
        self.recent_path_button.setGeometry(QRect(350, 190, 89, 25))
        self.tabWidget.addTab(self.tab_2, "")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 800, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.intro_browser.setHtml(QCoreApplication.translate("MainWindow", u"<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:'Ubuntu'; font-size:11pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><span style=\" font-size:12pt; font-weight:600;\">Welcome to BatteryFOAM</span></p>\n"
"<p align=\"justify\" style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px; font-size:12pt;\"><br /></p>\n"
"<p align=\"justify\" style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">BatteryFOAM is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free So"
                        "ftware Foundation, either version 3 of the License, or (at your option) any later version.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">For details of GNU General Public License, please see &lt;http://www.gnu.org/licenses/&gt;.</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Any academic work using this code or derivatives thereof, must cite the original paper that this code was released alongside.</p></body></html>", None))
        self.label_pic_vertical.setText("")
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Create a new project", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Select a module", None))
        self.carbon_button.setText(QCoreApplication.translate("MainWindow", u"Single Particle Model", None))
        self.main_path_label.setText(QCoreApplication.translate("MainWindow", u"Choose a folder to save your project files", None))
        self.main_next_button.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.halfCell_button.setText(QCoreApplication.translate("MainWindow", u"P2D Model(Half Cell)", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Enter your project name", None))
        self.main_path_button.setText(QCoreApplication.translate("MainWindow", u"Choose", None))
        self.pro_name_editline.setText(QCoreApplication.translate("MainWindow", u"project1", None))
        self.main_name_hint.setText(QCoreApplication.translate("MainWindow", u"?", None))
        self.fullCell_button.setText(QCoreApplication.translate("MainWindow", u"P2D Model(Full Cell)", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"New", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Open a project", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Choose a project folder to open", None))
        self.main_path_label_2.setText(QCoreApplication.translate("MainWindow", u"Please choose...", None))
        self.main_path_button_2.setText(QCoreApplication.translate("MainWindow", u"Choose", None))
        self.main_next_button_2.setText(QCoreApplication.translate("MainWindow", u"Next", None))
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Open the last used project", None))
        self.recent_path_label.setText(QCoreApplication.translate("MainWindow", u"Last used...", None))
        self.recent_path_button.setText(QCoreApplication.translate("MainWindow", u"Open", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Open", None))
    # retranslateUi

