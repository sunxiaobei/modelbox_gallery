# -*- coding: utf-8 -*-
# !/usr/bin/python3
# utils for yolo3 detection

import numpy as np


class Yolo3:
    def __init__(self, config):
        '''Yolo3实例初始化'''
      
        # 模型输入尺寸
        self.net_h = config['net_h']
        self.net_w = config['net_w']

        # 检测模型的类别
        self.labels = config['labels']
        self.num_labels = len(self.labels)

        # 检测模型的anchors，用于解码出检测框
        self.stride_list = config['strides']
        self.num_anchors_per_stride = 3
        self.anchor_list = np.array(config['anchors']).reshape((3, 3, 2))

        # 检测框的输出阈值与NMS筛选阈值
        self.conf_threshold = config['conf_threshold']
        self.iou_threshold = config['iou_threshold']
        self.FLAG_HWC = config['flag_hwc']

    def cal_iou(self, box1, box2):
        '''计算两个矩形框的IOU'''
        def _overlap(x1, x2, x3, x4):
            left = max(x1, x3)
            right = min(x2, x4)
            return right - left
        
        w = _overlap(box1[0], box1[2], box2[0], box2[2])
        h = _overlap(box1[1], box1[3], box2[1], box2[3])
        if w <= 0 or h <= 0:
            return 0
        inter_area = w * h
        union_area = (box1[2] - box1[0]) * (box1[3] - box1[1]) + \
            (box2[2] - box2[0]) * (box2[3] - box2[1]) - inter_area
        return inter_area * 1.0 / union_area

    def multiclass_nms(self, candidate_bboxes, threshold):
        '''使用NMS筛选检测框'''
        result = []

        for ix in range(self.num_labels):
            label_bboxes = candidate_bboxes[ix]
            sorted_boxes = sorted(label_bboxes, key=lambda x: x[4])[::-1]

            filtered = dict()
            for iy in range(len(sorted_boxes)):
                if iy in filtered:
                    continue

                keep_bbox = sorted_boxes[iy]
                for iz in range(iy+1, len(sorted_boxes)):
                    if iz in filtered:
                        continue

                    curr_bbox = sorted_boxes[iz]
                    iou = self.cal_iou(curr_bbox, keep_bbox)
                    if iou >= threshold:
                        filtered[iz] = 1

            for iy in range(len(sorted_boxes)):
                if iy not in filtered:
                    result.append(sorted_boxes[iy])
        return result

    def decode_outputs(self, conv_output, anchors):
        '''从模型输出的特征矩阵中解码出检测框的位置、类别、置信度等信息'''
        def _sigmoid(x):
            s = 1 / (1 + np.exp(-x))
            return s
       
        blob_h, blob_w, _ = conv_output.shape
        pred = conv_output.reshape((blob_h * blob_w, 3, 5+self.num_labels))

        pred[..., 4:] = _sigmoid(pred[..., 4:])
        pred[..., 0] = (_sigmoid(pred[..., 0]) +
                        np.tile(range(blob_w), (3, blob_h)).transpose((1, 0))) / blob_w
        pred[..., 1] = (_sigmoid(pred[..., 1]) + np.tile(np.repeat(
                        range(blob_h), blob_w), (3, 1)).transpose((1, 0))) / blob_h
        pred[..., 2] = (np.exp(pred[..., 2]) *
                        anchors[:, 0:1].transpose((1, 0))) / self.net_w
        pred[..., 3] = (np.exp(pred[..., 3]) *
                        anchors[:, 1:2].transpose((1, 0))) / self.net_h

        bboxes_xyxy = np.zeros((blob_h * blob_w, 3, 4))
        bboxes_xyxy[..., 0] = np.maximum(
            (pred[..., 0] - pred[..., 2] / 2.0), 0.0)  # x_min
        bboxes_xyxy[..., 1] = np.maximum(
            (pred[..., 1] - pred[..., 3] / 2.0), 0.0)  # y_min
        bboxes_xyxy[..., 2] = np.minimum(
            (pred[..., 0] + pred[..., 2] / 2.0), 1.0)  # x_max
        bboxes_xyxy[..., 3] = np.minimum(
            (pred[..., 1] + pred[..., 3] / 2.0), 1.0)  # y_max

        pred[..., :4] = bboxes_xyxy
        pred = pred.reshape((-1, 5 + self.num_labels))
        pred[:, 4] = pred[:, 4] * pred[:, 5:].max(1)
        pred = pred[pred[:, 4] >= self.conf_threshold]
        pred[:, 5] = np.argmax(pred[:, 5:], axis=-1)

        candidate_bboxes = [[] for ix in range(self.num_labels)]
        for ix in range(pred.shape[0]):
            bbox = [pred[ix, iy] for iy in range(4)]
            bbox.append(pred[ix, 4])
            bbox.append(int(pred[ix, 5]))
            candidate_bboxes[bbox[5]-1].append(bbox)

        return candidate_bboxes

    def get_result(self, model_outputs):
        '''从模型输出中得到检测框'''

        num_outputs = len(model_outputs)
        num_channel = self.num_anchors_per_stride * (self.num_labels + 5)
        candidate_bboxes = [[] for ix in range(self.num_labels)]
        for ix in range(num_outputs):
            pred = model_outputs[ix]
            if self.FLAG_HWC:  # 模型输出格式为HWC                
                pred = pred.reshape((self.net_h // self.stride_list[ix],
                                     self.net_w // self.stride_list[ix],
                                     num_channel))
            else:
                pred = pred.reshape((num_channel,
                                     self.net_h // self.stride_list[ix],
                                     self.net_w // self.stride_list[ix]))
                pred = pred.transpose((1, 2, 0))
            blob_anchors = self.anchor_list[ix]
            blob_bboxes = self.decode_outputs(pred, blob_anchors)
            candidate_bboxes = [candidate_bboxes[iy] + blob_bboxes[iy]
                                for iy in range(self.num_labels)]

        bboxes = self.multiclass_nms(candidate_bboxes, self.iou_threshold)
        return bboxes
