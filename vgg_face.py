from keras.models import Model, Sequential
from keras.layers import Input, Convolution2D, ZeroPadding2D, MaxPooling2D, Flatten, Dense, Dropout, Activation
import numpy as np
from keras.preprocessing.image import load_img, save_img, img_to_array
from keras.applications.imagenet_utils import preprocess_input
from keras.preprocessing import image
import os
import sys
import cv2
from keras.models import model_from_json
from yolo3.yolo3 import YOLO

os.environ['CUDA_VISIBLE_DEVICES'] = '0' # running on CPU
import pickle
# config = tf.compat.v1.ConfigProto()
# config.gpu_options.per_process_gpu_memory_fraction = 0.5
# config.gpu_options.allow_growth = True
# session = tf.compat.v1.Session(config=config)


class VGG_FACE():
    def __init__(self):
        #print("called")
        self.model_weight="./model_data/vgg_face_weights.h5"
        self.model_Features="./model_data/KnownFeatures.pickle" # known people faces' feature
        self.fileName="./model_data/test/KnownFeatures.pickle" # this is for testing
        self.fileName2="./model_data/test/KnownFaces_img.pickle" # used to save the image of the faces, for displaying

        self.KnownFeatures=self._load_feature()
        # print(self.KnownFeatures)
        self.model=Sequential()
        self.vgg_face_descriptor=self._generater()
        self.trainDataset=""
        self.epsilon = 0.2
        self.yolo=YOLO()
    def _generater(self):
        self.model.add(ZeroPadding2D((1,1),input_shape=(224,224, 3)))
        self.model.add(Convolution2D(64, (3, 3), activation='relu'))
        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(64, (3, 3), activation='relu'))
        self.model.add(MaxPooling2D((2,2), strides=(2,2)))

        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(128, (3, 3), activation='relu'))
        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(128, (3, 3), activation='relu'))
        self.model.add(MaxPooling2D((2,2), strides=(2,2)))

        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(256, (3, 3), activation='relu'))
        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(256, (3, 3), activation='relu'))
        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(256, (3, 3), activation='relu'))
        self.model.add(MaxPooling2D((2,2), strides=(2,2)))

        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(512, (3, 3), activation='relu'))
        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(512, (3, 3), activation='relu'))
        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(512, (3, 3), activation='relu'))
        self.model.add(MaxPooling2D((2,2), strides=(2,2)))

        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(512, (3, 3), activation='relu'))
        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(512, (3, 3), activation='relu'))
        self.model.add(ZeroPadding2D((1,1)))
        self.model.add(Convolution2D(512, (3, 3), activation='relu'))
        self.model.add(MaxPooling2D((2,2), strides=(2,2)))

        self.model.add(Convolution2D(4096, (7, 7), activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Convolution2D(4096, (1, 1), activation='relu'))
        self.model.add(Dropout(0.5))
        self.model.add(Convolution2D(2622, (1, 1)))
        self.model.add(Flatten())
        self.model.add(Activation('softmax'))


        self.model.load_weights(self.model_weight)

        return Model(inputs=self.model.layers[0].input, outputs=self.model.layers[-2].output)

    def _load_feature(self):
        #load the known face feature if there is any
        try:
            pickle_in = open(self.model_Features,"rb")
            return pickle.load(pickle_in)

        except Exception as e:
            return {}

    def _reload_feature(self,filename):
        try:
            #print(filename)
            pickle_in = open(filename,"rb")
            self.KnownFeatures= pickle.load(pickle_in)

        except Exception as e:
            return {}
    def getKnownFeatures(self):
        return self.KnownFeatures

    def getFeature(self, Image): # is used by self.verifyFace()
        # used to extract the face feature of a picture
        # Image can be a image directory or an read image from cv2.imread()
        # return the feature of that image
        try:
            img=cv2.imread(Image)
            return self.vgg_face_descriptor.predict(preprocess_image(img))[0,:]
        except :
            return self.vgg_face_descriptor.predict(preprocess_image(Image))[0,:]

    def getROI(self,frame): #is used bt trainFace()
        # frame is the image that read by cv2.imread or other similar function
        # return: a list of reion of interest
        try:
            boxes=self.yolo.detect_img(frame)
            rois=[]
            for box in boxes:
                top,right,bottom,left=box[0],box[1],box[2],box[3]
                roi=frame[top:bottom, left:right]
                rois.append(roi)
            return boxes,rois
        except Exception as e:
            print("getROI ",e)


    def verifyFace(self,img2):
        # used to verify the List of known faces, with the img2 which also is an image
        # the facee were trained using the trainFace(), and saved using pickle
        # it return the name of the person in img2 or Unknown if there is none in the List of known faces
        try:
            img2=self.getFeature(img2)
            key_="Unknown"
            #print(self.KnownFeatures)
            min=100
            for key,value in self.KnownFeatures.items():
                result=findCosineSimilarity(value[0],img2)
                if result<min:
                    min=result
                    key_=key
            if not min<self.epsilon:
                key_="Unknown"

                #count=0
                #for face in items:
                #    result=findCosineSimilarity(face,img2)
                #    # fixing this
                #    if result<self.epsilon:
                #        count +=1
                #if count/len(items)>= 0.5:
                #    key_=key
                ##print(count/len(items))
            return key_
        except Exception as e:
            print("verifyFace ",e)


    def close_session_(self):
        self.yolo.close_session()

    def trainSingleFace(self,filename,name,roi):
        dict={}
        dict2={}

        filename2=filename.replace(".pickle","_img.pickle")
        print(filename,filename2)

        try:
            data=[]
            if os.path.exists(filename):
                pickle_in = open(filename,"rb")
                dict=pickle.load(pickle_in)
                pickle_in2 = open(filename2,"rb")
                dict2=pickle.load(pickle_in2)
            # if name in dict:
            #     return False
            pickle_out=open(filename,'wb') ## for training data, contain the feature of the face
            pickle_out_2=open(filename2,'wb') ## for the image of known people


            print(name,filename)
            face_representation=self.getFeature(roi)
            data.append(face_representation)
            #print(data)
            dict[name]=data
            dict2[name]=roi

            # for roi in rois:
            #     print(name,filename)
            #     face_representation=self.getFeature(roi)
            #     data.append(face_representation)
            # if len(rois) >=1:
            #     dict2[name]=rois[0]
            # dict[name]=data
            print(name,filename)
            print(dict)

            pickle.dump(dict,pickle_out)
            pickle.dump(dict2,pickle_out_2)
            pickle_out.close()
            pickle_out_2.close()
            return True
        except Exception as e:
            print(e)
            return False



    # def trainFace(self,roi):
    #     pickle_in = open(self.model_Features,"rb")
    #     dict=pickle.load(pickle_in)
    #     pickle_in2 = open(self.fileName2,"rb")
    #     dict2=pickle.load(pickle_in2)
    def trainFace(self,Dataset_fullpath, newTrain=1):
        # Data set_fullpath is the directory to the train data set
        # eg: the set of knowns faces have 3 people, each can have at leat 1 image up to 10
        # Dataset_fullpath="./Train"
        # Train
        # ---- person1
        # ----------- img.jpg
        # ---- person2
        # ----------- img.jpg
        # ---- person3
        # ----------- img.jpg
        # the folder contrains the image will be the label during training
        # this function will save to the pickle file, no return value

        self.trainDataset=Dataset_fullpath

        dict={}
        dict2={}
        if newTrain==0:
            try:
                pickle_in = open(self.model_Features,"rb")
                dict=pickle.load(pickle_in)
                pickle_in2 = open(self.fileName2,"rb")
                dict2=pickle.load(pickle_in2)

            except Exception as e:
                self.trainFace(Dataset_fullpath)

        print("--- Start training at ",self.trainDataset)

        pickle_out=open(self.fileName,'wb') ## for training data
        pickle_out_2=open(self.fileName2,'wb') ## for the image of known people
        for root, dirs, files in os.walk(self.trainDataset):
            data=[]
            ckc_lbl=""
            for file in files:
                if file.endswith("png") or file.endswith("jpg"):
                    path=os.path.join(root,file)
                    label=os.path.basename(os.path.dirname(path))
                    if ckc_lbl is not label:
                        ckc_lbl=label

                    # ================= TODO ==================
                    # check for duplicate label if retraining
                    # make sure the training data is good
                    frame=cv2.imread(path)
                    _,rois=self.getROI(frame)

                    for roi in rois:
                        print(label,path)
                        face_representation=self.getFeature(roi)
                        data.append(face_representation)
                    if len(rois) >=1:
                        dict2[ckc_lbl]=rois[0]
                    dict[label]=data
        # for key,items in dict.items():
        #     for face in items:
        #         print(key, face)
        pickle.dump(dict,pickle_out)
        pickle.dump(dict2,pickle_out_2)
        pickle_out.close()
        pickle_out_2.close()
        print("=========== DONE ===========")



def preprocess_image(image):# no need Image path, using webcame or a frame
    img = cv2.resize(image, (224, 224))
    img = img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)
    return img

def findCosineSimilarity(source_representation, test_representation):
    # get the distance between 2 images
    a = np.matmul(np.transpose(source_representation), test_representation)
    b = np.sum(np.multiply(source_representation, source_representation))
    c = np.sum(np.multiply(test_representation, test_representation))
    return 1 - (a / (np.sqrt(b) * np.sqrt(c)))
