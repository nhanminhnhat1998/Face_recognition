import numpy as np
import cv2
from datetime import datetime
from PIL import ImageGrab
from win32api import GetSystemMetrics
monitorWidth=GetSystemMetrics(0)
monitorHeight=GetSystemMetrics(1)
fourcc=cv2.VideoWriter_fourcc(*'XVID')
outVideo= cv2.VideoWriter("D:/screenRecord/"+datetime.now().strftime("%d_%b___%H_%M")+".avi", fourcc, 20.0, (monitorWidth,monitorHeight))

print("recording ...")
while 1:
    img= ImageGrab.grab()
    img_np=np.array(img)
    img_in=cv2.cvtColor(img_np,cv2.COLOR_BGR2RGB)
    outVideo.write(img_in)
    cv2.imshow("Fuck",img_in)
    if cv2.waitKey(1)==27:
        break
print("Stop recording")
cv2.destroyAllWindows()
outVideo.release()
