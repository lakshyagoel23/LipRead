#! /usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2021 Imperial College London (Pingchuan Ma)
# Apache 2.0  (http://www.apache.org/licenses/LICENSE-2.0)

import sys
import os

# Add the parent directory of 'ibug' to the Python path
current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the directory where demo.py is located
sys.path.append(current_dir)  # Add this directory to the system path

# Now, you can import from the ibug module
from ibug.fan_predictor.fan.fan import FANPredictor
import warnings

from ibug.face_alignment.fan.fan_predictor import FANPredictor
from ibug.face_detection import RetinaFacePredictor

warnings.filterwarnings("ignore")


class LandmarksDetector:
    def __init__(self, device="cuda:0", model_name="resnet50"):
        self.face_detector = RetinaFacePredictor(
            device=device,
            threshold=0.8,
            model=RetinaFacePredictor.get_model(model_name),
        )
        self.landmark_detector = FANPredictor(device=device, model=None)

    def __call__(self, video_frames):
        landmarks = []
        for frame in video_frames:
            detected_faces = self.face_detector(frame, rgb=False)
            face_points, _ = self.landmark_detector(frame, detected_faces, rgb=True)
            if len(detected_faces) == 0:
                landmarks.append(None)
            else:
                max_id, max_size = 0, 0
                for idx, bbox in enumerate(detected_faces):
                    bbox_size = (bbox[2] - bbox[0]) + (bbox[3] - bbox[1])
                    if bbox_size > max_size:
                        max_id, max_size = idx, bbox_size
                landmarks.append(face_points[max_id])
        return landmarks