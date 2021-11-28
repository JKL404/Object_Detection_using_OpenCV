import os
from app import app
import urllib.request
from werkzeug.utils import secure_filename
from flask import Flask, flash, request, redirect, url_for, render_template


@app.route('/')
def home():
	return render_template('index.html')


@app.route('/textdetect/')
def upload_form():
	return render_template('upload.html')

@app.route('/textdetect/', methods=['POST'])
def upload_image():
	#Code to run main scan file
    import cv2
    import numpy as np
    import matplotlib.pyplot as plt
    import time
    # Load webcam
    font = cv2.FONT_HERSHEY_SIMPLEX
    starting_time = time.time()
    frame_id = 0
    net = cv2.dnn.readNet("./weights/yolov3-tiny.weights", "./configuration/yolov3-tiny.cfg")
	### Change here for custom classes for trained model
    classes = []
    mylist = []
    flag = 0
    with open("./configuration/coco.names", "r") as f:
	     classes = [line.strip() for line in f.readlines()]
    # Load webcam
    cap = cv2.VideoCapture(0)
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    while 1:
        _, img = cap.read()
        frame_id += 1
        img = cv2.resize(img,(1280,720))
        hight,width,_ = img.shape
        blob = cv2.dnn.blobFromImage(img, 1/255,(416,416),(0,0,0),swapRB = True,crop= False)

        net.setInput(blob)

        output_layers_name = net.getUnconnectedOutLayersNames()

        layerOutputs = net.forward(output_layers_name)

        boxes =[]
        confidences = []
        class_ids = []


        for output in layerOutputs:
            for detection in output:
                score = detection[5:]
                class_id = np.argmax(score)
                confidence = score[class_id]
                if confidence > 0.1:
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * hight)
                    w = int(detection[2] * width)
                    h = int(detection[3]* hight)
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)
                    boxes.append([x,y,w,h])
                    confidences.append((float(confidence)))
                    class_ids.append(class_id)

        indexes = cv2.dnn.NMSBoxes(boxes,confidences, 0.8, 0.3)
        for i in range(len(boxes)):
            if i in indexes:
                x, y, w, h = boxes[i]
                label = str(classes[class_ids[i]])
                confidence = confidences[i]
                color = colors[class_ids[i]]
                cv2.rectangle(img, (x, y), (x + w, y + h), color, 2)
                cv2.putText(img, label + " " + str(round(confidence, 2)), (x, y + 30), font, 3, color, 3)
                flag=0
                for ls in mylist:
                    if ls is label:
                       flag=1
                if flag != 1:
                    mylist.append(label)
        elapsed_time = time.time() - starting_time
        fps = frame_id / elapsed_time
        cv2.putText(img, "FPS: " + str(round(fps, 2)), (40, 670), font, .7, (0, 255, 255), 1)
        cv2.putText(img, "press [esc] to exit", (40, 690), font, .45, (0, 255, 255), 1)
        cv2.imshow("Image", img)
        key = cv2.waitKey(1)
        if key == 27:
            print("[button pressed] ///// [esc].")
            print("[feedback] ///// Videocapturing succesfully stopped")
            break
    cap.release()
    cv2.destroyAllWindows()
    return render_template('message.html' , itemss=mylist )

if __name__ == "__main__":
    app.run()
