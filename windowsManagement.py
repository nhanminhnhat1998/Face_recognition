from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import sys
from PyQt5.QtWidgets import (QMainWindow,QLineEdit,QPushButton,QTextEdit,QLabel,QCheckBox, QAbstractItemView,QGridLayout,
QHBoxLayout,QVBoxLayout,QApplication,QRadioButton,QWidget, QTableWidget,QTableWidgetItem,QFileDialog,QMessageBox,QScrollArea,QGroupBox,QFormLayout)
import qimage2ndarray
import os
from datetime import datetime

#sys.path.insert(1, 'C:\\Users\\Duma\\Documents\\Face_recognizer')
import pickle
import threading
import time
import numpy as np
import json
import csv
from win32api import GetSystemMetrics

monitorWidth=GetSystemMetrics(0)
monitorHeight=GetSystemMetrics(1)
class management(QWidget):

    def __init__(self):
        QWidget.__init__(self)
        self.video_size = QSize(460,460)
        #self._Knowface=self._load_data_fromPickle()
        self.dataSrc={}
        self.dataSrc_img={}

        self.dirSrc=""

        self.setup_ui()

    def _load_data_fromFaceLog(self,fileDIR):

        pickle_in=open(fileDIR,'rb')
        data= pickle.load(pickle_in)
        return data,fileDIR

    def _load_data_fromPickle(self,fileDIR):
        data={}
        data_img={}
        #print("2",self._KnowfaceDIR)
        if "_img" in fileDIR:
            modelFeature=fileDIR.replace("_img","")
            modelFeature_img=fileDIR

            print("_img", fileDIR,"modelFeature: "+modelFeature)

        else:
            modelFeature_img=fileDIR.replace(".pickle","_img.pickle")
            modelFeature=fileDIR

            print(" ", modelFeature_img,"modelFeature: "+fileDIR)

        pickle_in_img=open(modelFeature_img,'rb')
        pickle_in=open(modelFeature,'rb')

        data_img= pickle.load(pickle_in_img)
        data= pickle.load(pickle_in)
        return data,data_img, modelFeature,modelFeature_img

    def draw_Src(self):
        try:

            if  len(self.lbl_img)  >=1:
                i=0
                while 1:
                    #print(self.formLayout.rowCount())
                    self.formLayout.removeRow(i)
                    del self.lbl_img[i]
                    del self.tbox_name[i]
                    del self.btn_copy[i]
                    del self.btn_delete[i]
                    if len(self.lbl_img) == 0:
                        break


            for key,value in self.dataSrc_img.items():
                i= list(self.dataSrc_img.keys()).index(key)
                frame = cv2.cvtColor(value, cv2.COLOR_BGR2RGB)
                image = qimage2ndarray.array2qimage(frame)

                self.lbl_img.append(QLabel())
                self.lbl_img[i].setPixmap(QPixmap.fromImage(image).scaled(100, 100, Qt.KeepAspectRatio, Qt.FastTransformation))
                self.lbl_img[i].setFixedSize(QSize(100,100))

                self.tbox_name.append(QLineEdit())
                self.tbox_name[i].setText(key)



                vlay=QVBoxLayout()
                vlay.addWidget(self.tbox_name[i])
                if not self.checkBox.isChecked():
                    self.btn_copy.append(QPushButton("Copy"))
                    self.btn_copy[i].installEventFilter(self)

                    self.btn_delete.append(QPushButton("Delete"))
                    self.btn_delete[i].installEventFilter(self)

                    vlay.addWidget(self.btn_delete[i])
                    vlay.addWidget(self.btn_copy[i])

                hlayout=QHBoxLayout()
                hlayout.addWidget(self.lbl_img[i])
                hlayout.addLayout(vlay)


                self.formLayout.addRow(hlayout)

        except Exception as e:
            print("Management/draw_match_pair_box: ",e)

    def setup_ui(self):


        lbl_src=QLabel("File 1:")
        lbl_dst=QLabel("File 2:")


        self.tbox_srcFile=QLineEdit()
        self.tbox_srcFile.setEnabled(False)
        self.tbox_dstFile=QLineEdit()
        self.tbox_dstFile.setEnabled(False)

        self.checkBox=QCheckBox("View Only this is for debug and testing")

        self.btn_browseSrc=QPushButton("...")
        self.btn_browseSrc.setFixedSize(QSize(monitorWidth*0.02,monitorHeight*0.02))
        self.btn_browseSrc.clicked.connect(self._browseSrc)

        self.btn_browseDst=QPushButton("...")
        self.btn_browseDst.setFixedSize(QSize(monitorWidth*0.02,monitorHeight*0.02))
        self.btn_browseSrc.clicked.connect(self._browseDst)

        self.btn_back=QPushButton("<< Back")
        self.btn_back.clicked.connect(self._back)

        self.btn_quit=QPushButton("Quit")
        self.btn_quit.clicked.connect(self._quit)

        self.btn_save=QPushButton("Save")
        self.btn_save.clicked.connect(self._save)

        ## groupBox
        self.lbl_img=[]
        self.tbox_name=[]
        self.btn_delete=[]
        self.btn_copy=[]

        self.groupBoxSrc=QGroupBox()

        # lay output
        self.gridBox=QGridLayout()
        self.formLayout=QFormLayout()
        self.groupBoxSrc.setLayout(self.formLayout)

        scroll = QScrollArea()
        scroll.setWidget(self.groupBoxSrc)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(monitorHeight*0.5)
        scroll.setFixedWidth(monitorWidth*0.12)

        hlaysrc=QHBoxLayout()
        hlaysrc.addWidget(lbl_src)
        hlaysrc.addWidget(self.tbox_srcFile)
        hlaysrc.addWidget(self.btn_browseSrc)

        vlaysrc=QVBoxLayout()
        vlaysrc.addLayout(hlaysrc)
        vlaysrc.addWidget(self.checkBox)
        vlaysrc.addWidget(scroll)

        hBtnLayout=QHBoxLayout()
        hBtnLayout.addWidget(self.btn_back)
        hBtnLayout.addWidget(self.btn_save)
        hBtnLayout.addWidget(self.btn_quit)

        vMain=QVBoxLayout()
        vMain.addLayout(vlaysrc)
        vMain.addLayout(hBtnLayout)

        self.setLayout(vMain)
        #self.show()

    def browseFileDialog(self):
        options = QFileDialog.Options()
        fileName, a = QFileDialog.getOpenFileName(self,"QFileDialog.getSaveFileName()","","Text Files (*.pickle)", options=options)
        print(fileName,a)
        if fileName:
          return fileName


    def eventFilter(self,ob,event):
        try:
            for i in range(0,len(self.btn_copy)):
                if ob is self.btn_copy[i] and event.type()==2:
                    print("Copy: ",i)
                    self.copy_Item(i)
                    return False
                elif ob is self.btn_delete[i] and event.type()==2:
                    print("Delete: ",i)
                    self.del_Item(i)
                    return False

            return False
        except Exception as e:
            print("eventFilter: ",e)
    def del_Item(self,idx):
        del self.dataSrc[self.tbox_name[idx].text()]
        del self.dataSrc_img[self.tbox_name[idx].text()]
        self.btn_copy[idx].removeEventFilter(self)
        self.btn_delete[idx].removeEventFilter(self)
        self.formLayout.removeRow(idx)
        del self.lbl_img[idx]
        del self.tbox_name[idx]
        del self.btn_copy[idx]
        del self.btn_delete[idx]

    def copy_Item(self,idx):

        filename=self.browseFileDialog()
        data,data_img,dir,dir_img=self._load_data_fromPickle(filename)
        for k in data:
            if self.tbox_name[idx].text() == k:
                QMessageBox.about(self,"Error"," This person is already exit ")
                return False

        key=list(self.dataSrc.keys())[idx]

        print(dir,dir_img)
        data[key]=self.dataSrc[key]
        data_img[key]=self.dataSrc_img[key]
        print(data)
        pickle_out=open(dir,'wb') ## for training data, contain the feature of the face
        pickle_out_img=open(dir_img,'wb') ## for the image of known people
        pickle.dump(data,pickle_out)
        pickle.dump(data_img,pickle_out_img)
        QMessageBox.about(self,"Notification"," Done and Done ")


    def saveData(self,flag):
        if flag==1: # this is for file 1
            i=0
            temp={}
            temp_img={}
            for k in self.dataSrc.copy() :
                i= list(self.dataSrc.keys()).index(k)
                newName=self.tbox_name[i].text()
                temp[newName]=self.dataSrc[k]
                temp_img[newName]=self.dataSrc_img[k]
                # newkey=self.tbox_name[i].text()
                # print(newkey,k)
                # if newkey !=k:
                #     self.dataSrc[newkey]=self.dataSrc.pop(k)
                #     self.dataSrc_img[newkey]=self.dataSrc_img.pop(k)
                # i+=1
                # print(self.dataSrc)
            del self.dataSrc
            del self.dataSrc_img
            self.dataSrc=temp
            self.dataSrc_img=temp_img

            dir=self.dirSrc
            dir_img=self.dirSrc.replace(".pickle","_img.pickle")
            print("copy_Items",dir,dir_img)
            pickle_out=open(dir,'wb') ## for training data, contain the feature of the face
            pickle_out_img=open(dir_img,'wb') ## for the image of known people
            pickle.dump(self.dataSrc,pickle_out)
            pickle.dump(self.dataSrc_img,pickle_out_img)
            del temp
            del temp_img
            QMessageBox.about(self,"Notification"," Done and Done ")

    @pyqtSlot()

    def _save(self):
        try:
            if self.warningMsg("the old file will be Overwritten"):
                self.saveData(1)
        except Exception as e:
            print("management/_save: ",e)


    def warningMsg(self,strmsg):
        msgBox=QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(strmsg)
        msgBox.setWindowTitle("# WARNING: ")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            return True
    def _quit(self):
        pass

    def _back(self):
        pass



    def _browseSrc(self):
        try:
            filename=self.browseFileDialog()
            self.dirSrc=filename
            if filename is not None:
                self.tbox_srcFile.setText(filename)
                if self.checkBox.isChecked():
                    self.btn_save.setEnabled(False)
                    self.dataSrc_img,_=self._load_data_fromFaceLog(filename)
                else:
                    self.dataSrc,self.dataSrc_img,_,_=self._load_data_fromPickle(filename)
                self.draw_Src()
        except Exception as e:
            print(e)

    def _browseDst(self):
        pass
# 
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     win = management()
#     win.show()
#     sys.exit(app.exec_())
