
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from PyQt5.QtWidgets import (QMainWindow,QLineEdit,QPushButton,QTextEdit,QLabel,QCheckBox, QAbstractItemView,QDialog,
QHBoxLayout,QVBoxLayout,QApplication,QRadioButton,QWidget, QTableWidget,QTableWidgetItem,QFileDialog,QMessageBox,QScrollArea,QGroupBox,QFormLayout)
import qimage2ndarray
from datetime import datetime

#sys.path.insert(1, 'C:\\Users\\Duma\\Documents\\Face_recognizer')
import time
import os
import cv2
import sys
import numpy as np
from vgg_face import VGG_FACE
import pickle
import json
from win32api import GetSystemMetrics
from string import punctuation
_dirIcon=os.getcwd()+'/TestData/'

monitorWidth=GetSystemMetrics(0)
monitorHeight=GetSystemMetrics(1)
# vgg=VGG_FACE()

class addCamera(QWidget):
    def __init__(self,vgg_face):
        super(addCamera,self).__init__()

        self.roi=""
    # ###### starting Qthread for video steaming ########
    #     self.th=Thread()
    #     self.th.changePixmap.connect(self.setImage)
    #     self.th.start()
    # ###################################################
        self.flag=True
        self.vgg=vgg_face
        self.refeshRate=20 # the refesh rate of the lbl_vid, is used in setup_camera()
        self.saveDIR=""
        self.loadConfig()
        #self.frame=""
        try:
            self.setup_ui()
            self.setup_camera()
        except Exception as e:
            print(e)
        # self.setup_ui()
        # self.setup_camera()

    def loadConfig(self):
        with open('./model_data/config.json') as json_data_file:
            data = json.load(json_data_file)

        self.refeshrate=data["refeshrate"]
        self.saveDIR=data["savDIRmodelFeature"]

    # def setParameters(self,refeshrate,fileDIR):
    #     self.refeshrate=refeshrate
    #     print(type(refeshrate),refeshrate)
    #     self.tbox_filename.setText(fileDIR)
    #     print(type(fileDIR),fileDIR)


    def setup_ui(self):
        ##@@ Label
        self.lbl_vid = QLabel()
        lbl_Name=QLabel("Name:")
        lbl_filename=QLabel("Filename:")
    # =========== to do ======================
    # + set the size dynamicly
        self.lbl_img_accept=QLabel()
        #self.lbl_img_accept.setPixmap(QPixmap(_dirIcon+"m1.jpg").scaled(150, 150, Qt.KeepAspectRatio, Qt.FastTransformation))
        self.lbl_img_accept.setFixedSize(QSize(monitorWidth*0.1,monitorWidth*0.1))
        self.lbl_img_accept.setAlignment(Qt.AlignCenter)


        ##@@ textbox
        self.tbox_name=QLineEdit("")
        self.tbox_filename=QLineEdit(self.saveDIR)



        ##@@ button
        self.btn_back=QPushButton("<< Back")
        self.btn_accept=QPushButton("Accepct")
        self.btn_accept.clicked.connect(self._saveAndTrain)

        self.btn_filename=QPushButton("...")
        self.btn_filename.clicked.connect(self._browseFileLocation)
        self.btn_filename.setFixedSize(QSize(monitorWidth*0.02,monitorHeight*0.02))

        self.btn_quit = QPushButton("Quit")
        self.btn_quit.clicked.connect(self.close)

####@@@@ Layout design @@@@####
        Htopleft=QHBoxLayout()
        Htopleft.addWidget(lbl_filename)
        Htopleft.addWidget(self.tbox_filename)
        Htopleft.addWidget(self.btn_filename)

        VLeft=QFormLayout()
        VLeft.addRow(Htopleft)
        VLeft.addRow(self.lbl_vid)

        hlayout=QHBoxLayout()
        hlayout.addWidget(lbl_Name)
        hlayout.addWidget(self.tbox_name)

        Frame_utils=QFormLayout()
        Frame_utils.addRow(hlayout)
        Frame_utils.addRow(self.lbl_img_accept)
        Frame_utils.addRow(self.btn_accept)
        Frame_utils.addRow(self.btn_back,self.btn_quit)

        Hlayout_camera = QHBoxLayout()
        Hlayout_camera.addLayout(VLeft)
        Hlayout_camera.addLayout(Frame_utils)

        self.setLayout(Hlayout_camera)




    def setup_camera(self):
        """Initialize camera.
        """
    #    self.capture =  cv2.VideoCapture('rtsp://admin:admin@123@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0&unicast=true&proto=Onvif')

        #_thread.start_new_thread( self.display_video_stream,(self,))
        try:
            self.timer = QTimer()
            self.timer.timeout.connect(self.display_video_stream)
            self.timer.start(self.refeshRate)
        except Exception as e:
            print("addCamera/setup_camera: ",e)


        # self.thread2=threading.Thread(target=self.readVideo)
        # self.thread1=threading.Thread(target=self.display_video_stream)
        #
        # self.thread2.start()
        # self.thread1.start()

    def display_video_stream(self):
        """Read frame from camera and repaint QLabel widget.
        """
        try:
            # dunno y i need to convert colour of the image
            #frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)
            frame=self.frame
            #print(type(frame))
            #frame = cv2.flip(frame, 1)
            if self.flag:
                frame=self.handle_drawing_verification(frame)

            h, w, ch = frame.shape
            bytesPerLine = ch * w
            frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            convertToQtFormat = QImage(frame.data, w, h, bytesPerLine, QImage.Format_RGB888)
            image = convertToQtFormat.scaled(1080, 720, Qt.KeepAspectRatio)
            #print("img conveted face")
        ### converting the image just or displaying
            self.lbl_vid.setPixmap(QPixmap.fromImage(image))
        except Exception as e:
            print("addCamera No frame",e)

    def handle_drawing_verification(self,image):
        boxes,rois=self.vgg.getROI(image)
        #label=""
        for i, roi in enumerate(rois):
            top,right,bottom,left=boxes[i][0],boxes[i][1],boxes[i][2],boxes[i][3]

            image=cv2.rectangle(image, (left, top), (right, bottom), (1,234,10), 4)
            #image=cv2.putText(image, label, (left+10, top+30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 155, 0), 2)
            image2=cv2.cvtColor(roi,cv2.COLOR_BGR2RGB)
            image2 = qimage2ndarray.array2qimage(image2)
        ### converting the image just or displaying
########################################
 # this is the original image from the camera, will be used for training
            self.roi=roi
########################################
            # cv2.imshow('frame',self.roi)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     cv2.destroyAllWindows()
            self.lbl_img_accept.setPixmap(QPixmap.fromImage(image2).scaled(150, 150, Qt.KeepAspectRatio, Qt.FastTransformation))
        return image



    def saveDialog(self):
        self.d=QDialog()

        lbl_saveFace=QLabel("",self.d)
        image=cv2.cvtColor(self.roi,cv2.COLOR_BGR2RGB)
        image = qimage2ndarray.array2qimage(image)
        lbl_saveFace.setPixmap(QPixmap.fromImage(image).scaled(300, 300, Qt.KeepAspectRatio, Qt.FastTransformation))
        lbl_name=QLabel(self.tbox_name.text(),self.d)
        lbl_saveDIR=QLabel("filename: "+self.tbox_filename.text())

        btn_save = QPushButton("Save",self.d)
        btn_cancel=QPushButton("Cancel",self.d)



        Hlay=QHBoxLayout()
        Hlay.addWidget(btn_cancel)
        Hlay.addWidget(btn_save)
        Vlay=QVBoxLayout()
        Vlay.addWidget(lbl_saveFace)
        Vlay.addWidget(lbl_name)
        Vlay.addWidget(lbl_saveDIR)
        Vlay.addLayout(Hlay)
        Vlay.setAlignment(Qt.AlignCenter)

        self.d.setLayout(Vlay)
        self.d.setWindowTitle("Dialog")
        self.d.setWindowModality(Qt.ApplicationModal)

        btn_cancel.clicked.connect(self._cancelDialog)
        btn_save.clicked.connect(self._saveDialog)

        self.d.exec_()

    def browseFileDialog(self):
        options = QFileDialog.Options()
        fileName, a = QFileDialog.getOpenFileName(self,"QFileDialog.getSaveFileName()","","Text Files (*.pickle)", options=options)
        print(fileName,a)
        if fileName :
            return fileName


    # @pyqtSlot(np.ndarray)
    # def setImage(self, frame):
    #     #print("RUNNING")
    #     self.frame=frame

    def _browseFileLocation(self):
        try:
            filename=self.browseFileDialog()
            if filename is not None:
                self.tbox_filename.setText(filename)


        except Exception as e:
            print("Add new/_browseFileLocation: ",e)



    def _cancelDialog(self):
        try:
            self.flag=True
            self.d.close()
        except Exception as e:
            print("Add new/_cancelDialog: ",e)


    def _saveDialog(self):
        self.flag=True

        f=self.vgg.trainSingleFace(self.tbox_filename.text(),self.tbox_name.text(),self.roi)
        if f:
            QMessageBox.about(self,"Notification"," Saved ")
        else:
            QMessageBox.about(self,"Notification"," Faile ")
        self.d.close()


    def _saveAndTrain(self):
        text=self.tbox_name.text()
        filename=self.tbox_filename.text()
        check=True
        self.flag=False
        ## double check this bit, ##
        lst=punctuation.replace("_","")

        if len(text) !=0:
            if text[0].isdigit():
                self.flag=True
                QMessageBox.about(self, "Error", "You can not put number in front of your name")
                return 0
            if " " in text:
                text=text.replace(" ","_")
                self.tbox_name.setText(text)
            for c in text:
                if c in lst:
                    print(c)
                    self.flag=True
                    QMessageBox.about(self, "Error", "Your name must not have any special character \neg. !@#$%^&*()<>?:\"{}\" etc ")
                    return 0
            if os.path.exists(filename):
                pickle_in = open(filename,"rb")
                dict=pickle.load(pickle_in)
                if text in dict:
                    QMessageBox.about(self, "Error"," Name already exists")
                    return 0
            if check:
                if self.lbl_img_accept.pixmap() is not None :
                    self.saveDialog()
                else:
                    QMessageBox.about(self, "Error"," Face is not detected")
                    return 0
                ### saving process ####
        else:
            self.flag=True
            QMessageBox.about(self, "Error","What is your name")
            return 0
