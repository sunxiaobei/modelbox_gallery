# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _flowunit as modelbox
import cv2
import json
import numpy as np


class draw_mask_bboxFlowUnit(modelbox.FlowUnit):
    # Derived from modelbox.FlowUnit
    def __init__(self):
        super().__init__()

    def open(self, config):
        # Open the flowunit to obtain configuration information
        self.labels = config.get_string_list('labels', [])
        self.face_cover_ratio = config.get_float('face_cover_ratio', 0.9)
        self.mask_cover_ratio = config.get_float('mask_cover_ratio', 0.5)
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):
        in_image = data_context.input("in_image")
        in_bbox = data_context.input("in_bbox")
        out_image = data_context.output("out_image")

        for buffer_img, buffer_bbox in zip(in_image, in_bbox):
            width = buffer_img.get('width')
            height = buffer_img.get('height')
            channel = buffer_img.get('channel')

            img_data = np.array(buffer_img.as_object(), copy=False)
            img_data = img_data.reshape((height, width, channel))

            bbox_str = buffer_bbox.as_object()
            bboxes = self.decode_bboxes(bbox_str, (height, width))
            img_out = self.draw_mask_info(img_data, bboxes)
            
            out_buffer = modelbox.Buffer(self.get_bind_device(), img_out)
            out_buffer.copy_meta(buffer_img)
            out_image.push_back(out_buffer)

        return modelbox.Status.StatusCode.STATUS_SUCCESS
    
    def decode_bboxes(self, bbox_str, input_shape):
        det_result = json.loads(bbox_str)['det_result']
        bbox_data = json.loads(det_result)
        for bbox in bbox_data:
            bbox[0] = int(bbox[0] * input_shape[1])
            bbox[1] = int(bbox[1] * input_shape[0])
            bbox[2] = int(bbox[2] * input_shape[1])
            bbox[3] = int(bbox[3] * input_shape[0])
        return bbox_data

    def overlap(self, x1, x2, x3, x4):
        left = max(x1, x3)
        right = min(x2, x4)
        return right - left

    def cover_ratio(self, box1, box2):
        '''计算两个矩形框的IOU与box2区域的比值'''
        def _overlap(x1, x2, x3, x4):
            left = max(x1, x3)
            right = min(x2, x4)
            return right - left
        
        w = _overlap(box1[0], box1[2], box2[0], box2[2])
        h = _overlap(box1[1], box1[3], box2[1], box2[3])
        if w <= 0 or h <= 0:
            return 0
        inter_area = w * h
        small_area = (box2[2] - box2[0]) * (box2[3] - box2[1])
        return inter_area * 1.0 / small_area

    def find_max_cover_bbox(self, curr_bbox, bboxes, pick_label, threshold):
        '''找出重合度最大的bbox'''
        max_index = -1
        max_ratio = 0.0
        for ix in range(len(bboxes)):
            label_index = int(bboxes[ix][5])
            if self.labels[label_index] != pick_label:
                continue
            ratio = self.cover_ratio(curr_bbox, bboxes[ix])
            if ratio > max_ratio:
                max_index = ix
                max_ratio = ratio

        if max_index >= 0 and max_ratio >= threshold:
            return bboxes[max_index]
        else:
            return None

    def draw_mask_info(self, image, bboxes):
        '''在图中画出口罩佩戴信息'''
        thickness = 2
        font_scale = 1
        text_font = cv2.FONT_HERSHEY_SIMPLEX
        for bbox in bboxes:
            label_index = int(bbox[5])
            if self.labels[label_index] != 'head':
                continue

            x_min, y_min, x_max, y_max = bbox[0], bbox[1], bbox[2], bbox[3]

            face_bbox = self.find_max_cover_bbox(
                bbox, bboxes, 'face', self.face_cover_ratio)
            if not face_bbox:
                yellow = (255, 255, 0)
                cv2.rectangle(image, (x_min, y_min),
                              (x_max, y_max), yellow, thickness)
                cv2.putText(image, 'unknown', (x_min, y_min-20),
                            text_font, font_scale, yellow, thickness)
                continue

            mask_bbox = self.find_max_cover_bbox(
                face_bbox, bboxes, 'mask', self.mask_cover_ratio)
            if not mask_bbox:
                red = (0, 0, 255)
                cv2.putText(image, 'no mask', (x_min, y_min-20),
                            text_font, font_scale, red, thickness)
                cv2.rectangle(image, (x_min, y_min),
                              (x_max, y_max), red, thickness)
            else:
                green = (0, 255, 0)
                cv2.putText(image, 'has mask', (x_min, y_min-20),
                            text_font, font_scale, green, thickness)
                cv2.rectangle(image, (x_min, y_min),
                              (x_max, y_max), green, thickness)
                cv2.rectangle(image, (mask_bbox[0], mask_bbox[1]),
                              (mask_bbox[2], mask_bbox[3]), green, thickness)

        return image

    def close(self):
        # Close the flowunit
        return modelbox.Status()

    def data_pre(self, data_context):
        # Before streaming data starts
        return modelbox.Status()

    def data_post(self, data_context):
        # After streaming data ends
        return modelbox.Status()

    def data_group_pre(self, data_context):
        # Before all streaming data starts
        return modelbox.Status()

    def data_group_post(self, data_context):
        # After all streaming data ends
        return modelbox.Status()
