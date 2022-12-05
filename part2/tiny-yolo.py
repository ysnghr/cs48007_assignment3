# import the necessary packages
# creat an environent with BusterOS and install OpenVINO before starting. 
from openvino.inference_engine import IENetwork
from openvino.inference_engine import IEPlugin
from intel.yoloparams import TinyYOLOV3Params
from intel.tinyyolo import TinyYOLOv3
from imutils.video import VideoStream
from pyimagesearch.utils import Conf
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import os
import json
import requests

cd1 = argparse.ArgumentParser()
cd1.add_argument("-c", "--conf", required=True,
	help="Path to the input configuration file")
cd1.add_argument("-i", "--input", help="path to the input video file")
commands = vars(cd1.parse_args())
conf = Conf(commands["conf"])

# Labelling and coloring the objects found
LABELS = open(conf["labels_path"]).read().strip().split("\n")
np.random.seed(42)
COLORS = np.random.uniform(0, 255, size=(len(LABELS), 3))

# MYRIAD is found within OpenVINO that we installed wothin the system' if OpenVino isn't 
# available within the device, it should be installed before using this command
plugin = IEPlugin(device="MYRIAD")
print("[INFO] loading models...")
net = IENetwork(model=conf["xml_path"], weights=conf["bin_path"])
print("[INFO] preparing inputs...")
inputBlob = next(iter(net.inputs))

net.batch_size = 1
(n, c, h, w) = net.inputs[inputBlob].shape

# first statement controls the live stream, second one controls the ready video file. 
if commands["input"] is None:
	print("[INFO] starting video stream...")
	stream1 = VideoStream(usePiCamera=True).start()
	time.sleep(2.0)
else:
	print("[INFO] opening video file...")
	stream1 = cv2.VideoCapture(os.path.abspath(commands["input"]))
print("[INFO] loading model to the plugin...")
execNet = plugin.load(network=net, num_requests=1)
fps = FPS().start()

# frame by frame implementation
while True:
	copy1 = stream1.read()
	copy1 = copy1[1] if commands["input"] is not None else copy1
	if commands["input"] is not None and copy1 is None:
		break
	copy1 = imutils.resize(copy1, width=500)
	copy2 = cv2.resize(copy1, (w, h))
	copy2 = copy2.transpose((2, 0, 1))
	copy2 = copy2.reshape((n, c, h, w))
	output = execNet.infer({inputBlob: copy2})
	foundObjects = []
	
	# TinyYOLO implemented
	for (layerName, outBlob) in output.items():
		layerParams = TinyYOLOV3Params(net.layers[layerName].params,
			outBlob.shape[2])
		foundObjects += TinyYOLOv3.parse_yolo_region(outBlob,
			copy2.shape[2:], copy1.shape[:-1], layerParams,
			conf["prob_threshold"])
	for i in range(len(foundObjects)):
		if foundObjects[i]["confidence"] == 0:
			continue
		for j in range(i + 1, len(foundObjects)):
			if TinyYOLOv3.intersection_over_union(foundObjects[i],
				foundObjects[j]) > conf["iou_threshold"]:
				foundObjects[j]["confidence"] = 0
	foundObjects = [obj for obj in foundObjects if obj['confidence'] >= \
		conf["prob_threshold"]]
	(endY, endX) = copy1.shape[:-1]
	for obj in foundObjects:
		if obj["xmax"] > endX or obj["ymax"] > endY or obj["xmin"] \
			< 0 or obj["ymin"] < 0:
			continue
		label = "{}: {:.2f}%".format(LABELS[obj["class_id"]],
			obj["confidence"] * 100)
		y = obj["ymin"] - 15 if obj["ymin"] - 15 > 15 else \
			obj["ymin"] + 15
		cv2.rectangle(copy1, (obj["xmin"], obj["ymin"]), (obj["xmax"],
			obj["ymax"]), COLORS[obj["class_id"]], 2)
		cv2.putText(copy1, label, (obj["xmin"], y),
			cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[obj["class_id"]], 3)
	cv2.imshow("TinyYOLOv3", copy1)
	#requests.get('server-ip/tiny-yolo', data=json.dumps(foundObjects))
	key = cv2.waitKey(1) & 0xFF
	if key == ord("q"):
		break
	fps.update()
fps.stop()

print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
stream1.stop() if commands["input"] is None else stream1.release()
cv2.destroyAllWindows()