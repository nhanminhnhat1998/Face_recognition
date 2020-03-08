from PyQt5.QtCore import *
from PyQt5.QtGui import *
import cv2
import sys
from PyQt5.QtWidgets import (QMainWindow,QLineEdit,QPushButton,QTextEdit,QLabel,QCheckBox, QAbstractItemView,
QHBoxLayout,QVBoxLayout,QApplication,QRadioButton,QWidget, QTableWidget,QTableWidgetItem,QFileDialog,QMessageBox,QScrollArea,QGroupBox,QFormLayout)
import qimage2ndarray
import os
from datetime import datetime
_dirIcon=os.getcwd()+'/TestData/'

#sys.path.insert(1, 'C:\\Users\\Duma\\Documents\\Face_recognizer')
from vgg_face import VGG_FACE
import pickle
import threading
import time as tsleep
import numpy as np
import json
import csv
import requests
import _thread
from win32api import GetSystemMetrics

monitorWidth=GetSystemMetrics(0)
monitorHeight=GetSystemMetrics(1)

class CheckIN_OUT(QWidget):

    def __init__(self,vgg_face,thread):
        QWidget.__init__(self)
        self.video_size = QSize(460,460)
    ######## starting Qthread for video steaming ########
        # self.th=Thread()
        # self.th.changePixmap.connect(self.setImage)
        # self.th.start()
    #####################################################
        #________________________________________________

        #________________________________________________
        self.refeshRate=20 # will be change in loadConfig()
        self.flagPOS=datetime.now()
        self.webError=True
        self.reConect=False
        self.vgg=vgg_face
        self.th=thread
        self.attendance={}
        self.faceLogDIR="./faceLog/"+datetime.now().strftime("%d_%b___%H_%M")+".pickle"
        self.faceLog={}
        self._KnowfaceDIR=self.loadConfig()
        self._Knowface=self._load_data_fromPickle() # this is the images, not the feature for vgg
        self.fileDIR="./OutPutData/"+datetime.now().strftime("%d_%b_%Y")+os.path.basename(self._KnowfaceDIR).replace(".pickle","")+".csv"
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.outVideo= cv2.VideoWriter("D:/CameraOutData/"+datetime.now().strftime("%d_%b___%H_%M")+".avi", fourcc, 20.0, (1920,1080))
        self.webTime=datetime.now()
        self.ACK_TIME_TO_server=datetime.now()
        self._load_attendance()
        self.setup_ui()
        self.setup_camera()
        _thread.start_new_thread(self.checkWebserver,())

    def checkWebserver(self):
        response = os.system("ping -n 1 192.168.1.97")
        print(response)
        if response==0:
            payload={'flag':"3"}
            self.webTime=datetime.now()
            r= requests.post('http://192.168.1.97/test',data=payload)
            print("web check: ",r.status_code)
        else:
            print(" There is no connection to the server ")

    def checkCameraSteam(self):
        response = os.system("ping -n 1 192.168.1.99")
        if response==1:
            print(" Fail to connect to the Camera ")
        #


    def loadConfig(self):
        with open('./model_data/config.json') as json_data_file:
            data = json.load(json_data_file)

        self.refeshrate=data["refeshrate"]
        return data["modelFeature"]


    def _load_attendance(self):

        fileDIR=self.fileDIR

        if not os.path.isfile(fileDIR):
            with open(fileDIR, 'w',newline='') as csvfile:
                fieldnames = ['full_name', 'check_in','check_out','flag']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for k,_ in self._Knowface.items():
                    writer.writerow({'full_name': k, 'check_in': "",'check_out':"",'flag':'1'})
        line=0
        try:
            if os.path.isfile(fileDIR):
                with open(fileDIR, newline='') as csvfile:
                    reader = csv.reader(csvfile, dialect='excel', quoting=csv.QUOTE_NONE)
                    for row in reader:
                        if line!=0:
                            print(row)
                            self.attendance[row[0]]={"IN":row[1].split(" "),
                                                    "OUT":row[2].split(" "),
                                                    "flag":row[3]}
                        line+=1
            for k in self._Knowface:
                if k not in self.attendance:
                    self.attendance[k]={"IN":[''],
                                        "OUT":[''],
                                        "flag":"1"}
            print("Load ",self.attendance)
        except Exception as e:
            print("check/ Load: ",e)

    def _load_data_fromPickle(self):

        #print("2",self._KnowfaceDIR)
        modelFeature=self._KnowfaceDIR
        self.vgg._reload_feature(modelFeature)
        modelFeature_img=modelFeature.replace(".pickle","_img.pickle")
        pickle_in=open(modelFeature_img,'rb')
        return pickle.load(pickle_in)

    def _reload_data_fromPickle(self,filename):
        self._KnowfaceDIR=filename
        if "_img" in self._KnowfaceDIR:
            pickle_in=open(self._KnowfaceDIR,'rb')
            self._Knowface= pickle.load(pickle_in)
            modelFeature=self._KnowfaceDIR.replace("_img","")
            self.vgg._reload_feature(modelFeature)
            print("_img", self._KnowfaceDIR,"modelFeature: "+modelFeature)
        else:
            modelFeature=self._KnowfaceDIR
            self.vgg._reload_feature(modelFeature)
            self._KnowfaceDIR=self._KnowfaceDIR.replace(".pickle","_img.pickle")
            pickle_in=open(self._KnowfaceDIR,'rb')
            self._Knowface= pickle.load(pickle_in)
            print(" ", self._KnowfaceDIR,"modelFeature: "+modelFeature)

        self.redraw_match_pair_box()
    def setup_ui(self):
        """Initialize widgets.
        """
        # ==== label =====
        self.lbl_vid = QLabel()
        #self.lbl_vid.setFixedSize(self.video_size)
        lbl_filename=QLabel("Filename:")

        # self.lbl_img_match=QLabel()
        # self.lbl_img_match.setPixmap(QPixmap(_dirIcon+"m1.jpg").scaled(100, 100, Qt.KeepAspectRatio, Qt.FastTransformation))
        # self.lbl_img_match.setFixedSize(QSize(100,100))

        self.lbl_img_pair=QLabel(" TEST")
        self.lbl_img_pair.setFixedSize(QSize(100,100))

        lbl_imgIn=QLabel("Img IN")
        lbl_imgIn.setFixedWidth(100)
        lbl_imgComp=QLabel("Img Comp")
        lbl_imgComp.setFixedWidth(100)
        lbl_checkin=QLabel("Checkin time")
        lbl_checkin.setFixedWidth(100)
        lbl_checkout=QLabel("Checkout time")
        lbl_checkout.setFixedWidth(100)

        self.lbl_imag_match_list=[]
        self.lbl_imag_pair_list=[]
        self.lbl_txt_checkIN=[]
        self.lbl_txt_checkOUT=[]

        ##### TEXTBOX ######
        self.tbox_filename=QLineEdit("")
        self.tbox_filename.setText(self._KnowfaceDIR)
        self.tbox_filename.setEnabled(False)

        ########## BUTTON ###################
        # self.btn_filename=QPushButton("...")
        # self.btn_filename.clicked.connect(self._browseFileLocation)
        # self.btn_filename.setFixedSize(QSize(monitorWidth*0.02,monitorHeight*0.02))

        self.btn_back=QPushButton("<< Back")

        self.btn_quit = QPushButton("Quit")
        self.btn_quit.clicked.connect(self._close)


####@@@@ Layout design @@@@####
        Htopleft=QHBoxLayout()
        Htopleft.addWidget(lbl_filename)
        Htopleft.addWidget(self.tbox_filename)
        # Htopleft.addWidget(self.btn_filename)

        VRight=QFormLayout()
        VRight.addRow(Htopleft)


        self.formLayout=QFormLayout()

        # ==== layout ====
        Vlayout_header=QHBoxLayout()
        Vlayout_header.addWidget(lbl_imgIn)
        Vlayout_header.addWidget(lbl_imgComp)
        Vlayout_header.addWidget(lbl_checkin)
        Vlayout_header.addWidget(lbl_checkout)

        self.formLayout.addRow(Vlayout_header)

        self.groupBox=QGroupBox(datetime.now().strftime("%d %b, %Y"))
        self.draw_match_pair_box()
        self.groupBox.setLayout(self.formLayout)

        scroll = QScrollArea()
        scroll.setWidget(self.groupBox)
        scroll.setWidgetResizable(True)
        scroll.setFixedHeight(self.video_size.height())
        scrollWidth=0
        if self.lbl_imag_match_list is not None and self.lbl_imag_pair_list is not None:
            scrollWidth=(self.lbl_imag_match_list[0].width() *4 *1.1)
        scroll.setFixedWidth(scrollWidth)

        VRight.addWidget(scroll)
        VRight.addWidget(self.btn_back)
        VRight.addWidget(self.btn_quit)

        self.main_layout = QHBoxLayout()
        self.main_layout.addWidget(self.lbl_vid)
        self.main_layout.addLayout(VRight)

        self.move(monitorWidth*0.15, monitorHeight*0.15)
        self.setLayout(self.main_layout)

    def draw_match_pair_box(self):
        try:
            for key,value in self._Knowface.items():

                i= list(self._Knowface.keys()).index(key)
                frame = cv2.cvtColor(value, cv2.COLOR_BGR2RGB)
                image = qimage2ndarray.array2qimage(frame)
                self.lbl_imag_match_list.append(QLabel())
                self.lbl_imag_match_list[i].setPixmap(QPixmap.fromImage(image).scaled(100, 100, Qt.KeepAspectRatio, Qt.FastTransformation))
                self.lbl_imag_match_list[i].setFixedSize(QSize(100,100))

                self.lbl_imag_pair_list.append(QLabel())
                self.lbl_imag_pair_list[i].setFixedSize(QSize(100,100))

                time=""
                self.lbl_txt_checkIN.append(QLabel())
                for t in self.attendance[key]["IN"]:
                    time+=t+"\n"
                self.lbl_txt_checkIN[i].setText(time)
                self.lbl_txt_checkIN[i].setFixedSize(QSize(100,100))
                self.lbl_txt_checkIN[i].setAlignment(Qt.AlignCenter)

                time=""
                self.lbl_txt_checkOUT.append(QLabel())
                for t in self.attendance[key]["OUT"]:
                    time+=t+"\n"
                self.lbl_txt_checkOUT[i].setText(time)
                self.lbl_txt_checkOUT[i].setFixedSize(QSize(100,100))
                self.lbl_txt_checkOUT[i].setAlignment(Qt.AlignCenter)

                hlayout=QHBoxLayout()
                hlayout.addWidget(self.lbl_imag_pair_list[i])
                hlayout.addWidget(self.lbl_imag_match_list[i])
                hlayout.addWidget(self.lbl_txt_checkIN[i])
                hlayout.addWidget(self.lbl_txt_checkOUT[i])
                self.formLayout.addRow(hlayout)

        except Exception as e:
            print("CheckIO/draw_match_pair_box: ",e)

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
            print("CheckIO/setup_camera: ",e)

    def update_CSV(self,name,flag):
        #print(fileDIR)
        try:
            fileDIR=self.fileDIR
            line=0
            temp={}
            if os.path.isfile(fileDIR):
                with open(fileDIR, newline='') as csvfile:
                    reader = csv.reader(csvfile, dialect='excel', quoting=csv.QUOTE_NONE)
                    for row in reader:
                        if line!=0:
                            temp[row[0]]={"IN":row[1].split(" "),
                                        "OUT":row[2].split(" "),
                                        "flag":row[3]}
                        line+=1
            if name not in temp:
                temp[name]={"IN":[''],
                            "OUT":[''],
                            "flag":"1"}
            with open(fileDIR, 'w',newline='') as csvfile:
                #print("Write: ",self.attendance)

                fieldnames = ['full_name', 'check_in','check_out','flag']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                if flag==1:
                    temp[name]["flag"]="0"
                    temp[name]['IN'].append(self.attendance[name]["IN"][-1])
                else :
                    temp[name]["flag"]="1"
                    temp[name]['OUT'].append(self.attendance[name]["OUT"][-1])

                for k,v in temp.items():
                    IN=""
                    out=""
                    for i in v["IN"]:
                        IN+=i+" "
                    for i in v["OUT"]:
                        out+=i+" "

                    #print("write: ",IN, out)
                    writer.writerow({'full_name': k, 'check_in': IN.strip(),'check_out':out.strip(),'flag':temp[k]["flag"]})
        except Exception as e:
            print("UpdataCSV: ",e)

    def warningMsg(self,strmsg):
        msgBox=QMessageBox()
        msgBox.setIcon(QMessageBox.Information)
        msgBox.setText(strmsg)
        msgBox.setWindowTitle("# WARNING: ")
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        returnValue = msgBox.exec()
        if returnValue == QMessageBox.Ok:
            self.webError=False

    def postFlag(self,flag):
        payload={'flag':str(flag)}
        try:
            delay=datetime.now()-self.webTime
            response = os.system("ping -n 1 192.168.1.97")
            if delay.seconds>=2 and response==0:
                print(payload)
                self.webTime=datetime.now()
                r= requests.post('http://192.168.1.97/test',data=payload)
                print(r.status_code)
            elif response==1:
                print("server is offline")
        except Exception as e:
            print("ESP8266: ",e)

    def handle_drawing_verification(self,image):
        try:
            boxes,rois=self.vgg.getROI(image)
            label=""
            #print("2233")
            #print("loiz")
            for i, roi in enumerate(rois):
                top,right,bottom,left=int(boxes[i][0]*0.965),int(boxes[i][1]*1.03),int(boxes[i][2]*1.03),int(boxes[i][3]*0.965)
                ROI=image[top:bottom, left:right]
                label=self.vgg.verifyFace(ROI)
                 ###put object rectangle(X1,y1), (x2,y2)
                image=cv2.rectangle(image, (left, top), (right, bottom), (1,234,10), 3)
                image=cv2.putText(image, label, (left+5, top+30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 155, 0), 2)
                DATETime=datetime.now()
                now=DATETime.strftime("%H:%M")

                #print(self.faceLog)
                if label is not "Unknown":
                    self.faceLog[DATETime.strftime("%H:%M:%S")]=ROI
                    employee = self.attendance[label]
                    i=list(self._Knowface.keys()).index(label)
                    frame = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
                    image2 = qimage2ndarray.array2qimage(frame)
                    #print(type(self.lbl_imag_pair_list[i].pixmap()))


                    ## check_in
                    if (employee["flag"] =="1") and (employee["IN"][-1]!=now) and (employee["OUT"][-1]!=now) :
                        self.lbl_imag_pair_list[i].setPixmap(QPixmap.fromImage(image2).scaled(100, 100, Qt.KeepAspectRatio, Qt.FastTransformation))
                        employee["flag"]="0"
                        employee["IN"].append(now)
                        #print("employee['IN']",employee["IN"])

                        time=""
                        for t in employee["IN"]:
                            time+=t+"\n"
                        self.lbl_txt_checkIN[i].setText(time)
                        self.update_CSV(label,1)
                        ## Talk to the server ESP8266
                        _thread.start_new_thread(self.postFlag,(1,))
                        ## _______________________________
                    ## check_out
                    elif (employee["flag"] =="0") and (employee["OUT"][-1]!=now) and (employee["IN"][-1]!=now) :
                        self.lbl_imag_pair_list[i].setPixmap(QPixmap.fromImage(image2).scaled(100, 100, Qt.KeepAspectRatio, Qt.FastTransformation))
                        employee["flag"] ="1"
                        employee["OUT"].append(now)
                        #print("employee['OUT']",employee["OUT"])

                        time=""
                        for t in employee["OUT"]:
                            time+=t+"\n"
                        self.lbl_txt_checkOUT[i].setText(time)
                        self.update_CSV(label,0)
                        ## Talk to the server ESP8266

                        _thread.start_new_thread(self.postFlag,(1,))
                        ## _______________________________

            return image
        except Exception as e:
            print("CheckIO/handle_drawing_verification: ",e)


    def display_video_stream(self):
        """Read frame from camera and repaint QLabel widget.
        """

        try:
            #print("__------------------------------______-")
            if (datetime.now() - self.ACK_TIME_TO_server).seconds>=45:
                self.ACK_TIME_TO_server=datetime.now()
                print("ACK")
                _thread.start_new_thread(self.postFlag,(3,))
                _thread.start_new_thread(self.checkCameraSteam,())
            height,width,_=self.frame.shape
            x1=int(0.15*width)
            w=int(0.7*width)

            line1=[(x1,0),(x1,height)]
            line2=[(x1+w,0),(x1+w,height)]

            cv2.line(self.frame,line1[0],line1[1],(0,0,255),2)
            cv2.line(self.frame,line2[0],line2[1],(0,0,255),2)

            frame_in = self.frame[:,x1:x1+w]
            frame_final=self.frame

            delay=datetime.now()-self.webTime

            frame_out=self.handle_drawing_verification(frame_in)
            frame_final[:,x1:x1+w]=frame_out



            self.outVideo.write(frame_final)

            frame_final = cv2.cvtColor(frame_final, cv2.COLOR_BGR2RGB)
            h, w, ch = frame_final.shape
            bytesPerLine = ch * w
            convertToQtFormat = QImage(frame_final.data, w, h, bytesPerLine, QImage.Format_RGB888)
            image = convertToQtFormat.scaled(1080, 720, Qt.KeepAspectRatio)
            #print("img conveted face")

            self.lbl_vid.setPixmap(QPixmap.fromImage(image))
            #print("")
        except Exception as e:
            print("CheckIO No frame",e)


    def _close(self):
        self.vgg.close_session_()
        self.close()
