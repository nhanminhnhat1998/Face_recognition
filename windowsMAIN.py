from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWidgets import (QMainWindow,QLineEdit,QPushButton,QTextEdit,QLabel,QCheckBox, QAbstractItemView,QDialog,
QHBoxLayout,QVBoxLayout,QApplication,QRadioButton,QWidget, QTableWidget,QTableWidgetItem,QFileDialog,QMessageBox,QScrollArea,QGroupBox,QFormLayout)
import qimage2ndarray


#sys.path.insert(1, 'C:\\Users\\Duma\\Documents\\Face_recognizer')
import time
import os
import cv2

import sys
import numpy as np
from vgg_face import VGG_FACE
import pickle
import json
import csv
from datetime import datetime

from win32api import GetSystemMetrics
_dirIcon=os.getcwd()+'/TestData/'

monitorWidth=GetSystemMetrics(0)
monitorHeight=GetSystemMetrics(1)
vgg=VGG_FACE()


class windowsConfig(QDialog):

    def __init__(self):
        super(windowsConfig,self).__init__()

        self.config=self.loadConfig()
        self.draw()

    def loadConfig(self):
        with open('./model_data/config.json') as json_data_file:
            data = json.load(json_data_file)
        return data

    def draw(self):

        txt_modelFeature=QLabel("Model feature: ")
        txt_saveModel=QLabel("Default add model feature: ")
        txt_refeshRate=QLabel("Refesh rate (ms): ")
        txt_threadSleeptime=QLabel("Thread delay time (ms): ")

        self.tbox_modelFeature=QLineEdit()
        self.tbox_modelFeature.setText(self.config["modelFeature"])
        width=self.tbox_modelFeature.fontMetrics().boundingRect(self.tbox_modelFeature.text()).width()+6
        self.tbox_modelFeature.setFixedWidth(width)
        self.tbox_saveModel=QLineEdit()
        self.tbox_saveModel.setText(self.config["savDIRmodelFeature"])
        self.tbox_refeshRate=QLineEdit()
        self.tbox_refeshRate.setText(str(self.config["refeshrate"]))
        self.tbox_threadSleeptime=QLineEdit()
        self.tbox_threadSleeptime.setText(str(self.config["threadSleeptime"]))


        self.btn_cancel=QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self._cancel)
        self.btn_save=QPushButton("Save")
        self.btn_save.clicked.connect(self._save)
        self.btn_browseModel=QPushButton("...")
        self.btn_browseModel.setFixedSize(QSize(monitorWidth*0.02,monitorHeight*0.02))
        self.btn_browseModel.clicked.connect(self._browseFileLocation1)
        self.btn_browseDfSave=QPushButton("...")
        self.btn_browseDfSave.setFixedSize(QSize(monitorWidth*0.02,monitorHeight*0.02))
        self.btn_browseDfSave.clicked.connect(self._browseFileLocation2)

        Hlayout1=QHBoxLayout()
        Hlayout1.addWidget(self.tbox_modelFeature)
        Hlayout1.addWidget(self.btn_browseModel)
        Hlayout2=QHBoxLayout()
        Hlayout2.addWidget(self.tbox_saveModel)

        Hlayout2.addWidget(self.btn_browseDfSave)

        layout=QFormLayout()
        layout.addRow(txt_modelFeature,Hlayout1)
        layout.addRow(txt_saveModel,Hlayout2)
        layout.addRow(txt_refeshRate,self.tbox_refeshRate)
        layout.addRow(txt_threadSleeptime,self.tbox_threadSleeptime)
        layout.addRow(self.btn_cancel,self.btn_save)

        self.setLayout(layout)
        self.setWindowTitle("Configuration")
        self.setWindowModality(Qt.ApplicationModal)

    def getConfig(self):
        return self.config

    def browseFileDialog(self):
        options = QFileDialog.Options()
        fileName, a = QFileDialog.getOpenFileName(self,"QFileDialog.getSaveFileName()","","Text Files (*.pickle)", options=options)
        print(fileName,a)
        if fileName :
            return fileName

    def resetData(self):
        self.tbox_modelFeature.setText(self.config["modelFeature"])
        self.tbox_saveModel.setText(self.config["savDIRmodelFeature"])
        self.tbox_refeshRate.setText(str(self.config["refeshrate"]))
        self.tbox_threadSleeptime.setText(str(self.config["threadSleeptime"]))


    def _browseFileLocation1(self):
        try:
            filename=self.browseFileDialog()
            # checking whether the file is empty or not

            if filename is not None:
                pickle_check=open(filename,'rb')
                if not bool(pickle.load(pickle_check)):
                    QMessageBox.about(self, "Error","The content of the file is empty\nPlase choose diff file")
                else:
                    self.tbox_modelFeature.setText(filename)
        except Exception as e:
            print("Config/_browseFileLocation1: ",e)

    def _browseFileLocation2(self):
        try:
            filename=self.browseFileDialog()
            if filename is not None:
                self.tbox_saveModel.setText(filename)
        except Exception as e:
            print("Config/_browseFileLocation2: ",e)

    def _cancel(self):
        self.close()

    def _save(self):

        self.config["modelFeature"]=self.tbox_modelFeature.text()
        self.config["savDIRmodelFeature"]=self.tbox_saveModel.text()
        self.config["refeshrate"]=int(self.tbox_refeshRate.text())
        self.config["threadSleeptime"]=int(self.tbox_threadSleeptime.text())
        with open('./model_data/config.json', 'w') as outfile:
            json.dump(self.config, outfile)
        QMessageBox.about(self, "Notification","Saved successfully")
        self.close()


class mainMenu(QWidget):

    def __init__(self):
        super(mainMenu,self).__init__()


        windownSize=QSize(monitorWidth*0.15,monitorHeight*0.15)
        self.setFixedSize(windownSize)
        self.draw()



    def draw(self):
        self.btn_camera=QPushButton("Using camera")
        self.btn_check=QPushButton("Check In/Out")
        self.btn_quit=QPushButton("Quit")
        self.btn_config=QPushButton("*")
        self.btn_reconnect=QPushButton("Reconnect camera")
        self.btn_Management=QPushButton("Edit files")
        # self.btn_camera.clicked.connect(self._btnCamera)
        # self.btn_files.clicked.connect(self._btnFiles)

        Hlayout_menu=QHBoxLayout()
        Hlayout_menu.addWidget(self.btn_camera)
        Hlayout_menu.addWidget(self.btn_check)

        Vlayout=QVBoxLayout()
        Vlayout.addLayout(Hlayout_menu)
        Vlayout.addWidget(self.btn_Management)
        Vlayout.addWidget(self.btn_config)
        Vlayout.addWidget(self.btn_reconnect)
        Vlayout.addWidget(self.btn_quit)
        self.setLayout(Vlayout)


class Thread(QThread):
    changePixmap = pyqtSignal(np.ndarray)
    def __init__(self):
        QThread.__init__(self)
        self.vid_url = 'rtsp://admin:admin@123@192.168.1.99:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif'
        self.sleepTime=0.021
        self.ret=False

    def setSleepTime(self,time):
        self.sleepTime=time/1000
        print(self.sleepTime)
    def run(self):
        #print("run?")
        try:
            self.cap = cv2.VideoCapture(self.vid_url)

            while True:
                time.sleep(self.sleepTime)
                self.ret, frame = self.cap.read()
                #print(self.ret)
                if self.ret:
                    self.changePixmap.emit(frame)

        except Exception as e:
            print("thread ",e)
from windowsCheckIO import CheckIN_OUT
from windowsaddCamera import addCamera
from windowsManagement import management
import requests
# from admin import admin
# if not admin.isUserAdmin():
#         admin.runAsAdmin()
class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()


    ###### starting Qthread for video steaming ########
    # IMPORTANT note: the sleep time of the thread must be
    # greater or equal to the refeshRate of lbl_vid
        self.th=Thread()
        self.th.changePixmap.connect(self.setImage)
        self.th.start()

    ###################################################
        #self.attendance=[]
        self.flag=3 # 0 is mainMenu, 1 is checkIO, 2 is
        self.configDialog=windowsConfig()
        self.config=self.configDialog.getConfig()
        self.th.setSleepTime(self.config["threadSleeptime"])
        self.setWindowIcon(QIcon("./model_data/video_camera_icon_124392.png"))

        #self.craetingAttendanceFile()
        self._mainMenu()

    def _load_data_fromPickle(self):

        #print("2",self._KnowfaceDIR)
        modelFeature=self.config["modelFeature"]
        modelFeature_img=modelFeature.replace(".pickle","_img.pickle")
        pickle_in=open(modelFeature_img,'rb')
        return pickle.load(pickle_in)


    @pyqtSlot(np.ndarray)
    def setImage(self, frame):
        try:
            # chekc if the video still connected or not
            if self.flag == 1:
                self.checkIO.frame=frame
            elif self.flag==2:
                self.addCamera.frame=frame
            else:
                pass
        except Exception as e:
            print("No applicataion selected")
    #@pyqtSlot()
    def _mainMenu(self):
        if self.flag==3:
            self._reconnect()
        self.flag=0
        self.mainMenu=mainMenu()
        windownSize=self.mainMenu.maximumSize()
        self.setFixedSize(windownSize)
        self.setWindowTitle("Main menu")
        self.setCentralWidget(self.mainMenu)
        self.move(monitorWidth*0.35, monitorHeight*0.35)
        self.mainMenu.btn_camera.clicked.connect(self._addCamera)
        self.mainMenu.btn_quit.clicked.connect(self._quit)
        self.mainMenu.btn_check.clicked.connect(self._check)
        self.mainMenu.btn_config.clicked.connect(self._config)
        self.mainMenu.btn_reconnect.clicked.connect(self._reconnect)
        self.mainMenu.btn_Management.clicked.connect(self._manage)
        self.show()

    def _check(self):
        try:
            # response = os.system("ping 192.168.1.97")
            # if response==1:
            #     QMessageBox.about(self,"Error"," Can not connect to ESP8266 ")
            # else:
            #     print(self.postFlag(3))
            self.flag=1
            self.checkIO=CheckIN_OUT(vgg,self.th)
            windownSize=self.checkIO.maximumSize()
            self.setFixedSize(windownSize)
            self.setWindowTitle("Check In/Out")
            self.setCentralWidget(self.checkIO)
            self.move(monitorWidth*0.15, monitorHeight*0.15)
            self.checkIO.btn_back.clicked.connect(self._saveVideo)
            self.checkIO.btn_quit.clicked.connect(self._closeCheck)
            self.show()
        except Exception as e:
            print("Check: ",e)

    def _addCamera(self):
        try:
            self.flag=2
            self.addCamera=addCamera(vgg)
            windownSize=self.addCamera.maximumSize()
            self.setFixedSize(windownSize)
            self.setWindowTitle("Add new using camera")
            self.setCentralWidget(self.addCamera)
            self.move(monitorWidth*0.2, monitorHeight*0.2)
            self.addCamera.btn_back.clicked.connect(self._mainMenu)
            self.addCamera.btn_quit.clicked.connect(self._close)
            self.show()
        except Exception as e:
            print("Add new: ",e)

    def _manage(self):
        self.flag=4
        self.management=management()
        windownSize=self.management.maximumSize()
        self.setFixedSize(windownSize)
        self.setWindowTitle("Main menu")
        self.setCentralWidget(self.management)
        self.management.btn_back.clicked.connect(self._mainMenu)
        self.management.btn_quit.clicked.connect(self._close)

    def _config(self):
        try:
            self.configDialog.resetData()
            self.configDialog.exec_()
            self.th.setSleepTime(self.config["threadSleeptime"])
        except Exception as e:
            print("Config: ",e)

    def _reconnect(self):
        try:
            check=0
            response = os.system("ping -n 1 192.168.1.99")
            time.sleep(0.25)
            if response==0:
                time.sleep(0.25)
                check=3
                self.th.cap=cv2.VideoCapture(self.th.vid_url)

            else :
                check=self.warningMsg("Fail to connect to the Camera")

            if self.th.ret and self.flag!=3:
                check=3
                QMessageBox.about(self,"Notification"," Good to go ")


            if check==0:
                self._reconnect()
            elif check==2:
                self._close()
        except Exception as e:
            print("Reconnect: ",e)

    def warningMsg(self,strmsg):
        msgBox=QMessageBox()
        msgBox.setIcon(QMessageBox.Warning)
        msgBox.setText(strmsg)
        msgBox.setWindowTitle("# WARNING: ")
        msgBox.setStandardButtons(QMessageBox.Retry | QMessageBox.Ignore| QMessageBox.Abort)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Retry:
            return 0
        elif returnValue == QMessageBox.Ignore:
            return 1
        else : return 2

    def _saveVideo(self):
        try:
            self.checkIO.postFlag(2)
            pickle_out=open(self.checkIO.faceLogDIR,'wb')
            pickle.dump(self.checkIO.faceLog,pickle_out)
            print("video saved - facelog saved")
            self._mainMenu()
        except Exception as e:
            print("main/back<<: ",e)
            self._mainMenu()

    def _closeCheck(self):

        self.checkIO.postFlag(2)
        pickle_out=open(self.checkIO.faceLogDIR,'wb')
        pickle.dump(self.checkIO.faceLog,pickle_out)
        print("video saved - facelog saved")
        self.close()
        vgg.close_session_()



    def _quit(self):
        self.mainMenu.close()
        self.close()
        vgg.close_session_()


    def _close(self):
        self.close()
        vgg.close_session_()

    def postFlag(self,flag):
        payload={'flag':str(flag)}
        try:
            r= requests.post('http://192.168.1.97/test',data=payload)
            return r.status_code
        except Exception as e:
            print("ESP8266: ",e)
if __name__ == "__main__":

		app = QApplication(sys.argv)
		w=MainWindow()
		try:
			sys.exit(app.exec_())
		except:
			pass
