#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

import numpy as np


def nms(boxes, scores, nms_thr):
    """Single class NMS implemented in Numpy."""
    x1 = boxes[:, 0]
    y1 = boxes[:, 1]
    x2 = boxes[:, 2]
    y2 = boxes[:, 3]

    nms_areas = (x2 - x1) * (y2 - y1)
    nms_order = scores.argsort()[::-1]

    nms_keep = []
    while nms_order.size > 0:
        i = nms_order[0]
        nms_keep.append(i)
        xx1 = np.maximum(x1[i], x1[nms_order[1:]])
        yy1 = np.maximum(y1[i], y1[nms_order[1:]])
        xx2 = np.minimum(x2[i], x2[nms_order[1:]])
        yy2 = np.minimum(y2[i], y2[nms_order[1:]])

        w = np.maximum(0.0, xx2 - xx1)
        h = np.maximum(0.0, yy2 - yy1)
        nms_inter = w * h
        try:
            ovr = nms_inter / (nms_areas[i] + nms_areas[nms_order[1:]] - nms_inter)
        except ZeroDivisionError:
            ovr = 1.0

        inds = np.where(ovr <= nms_thr)[0]
        nms_order = nms_order[inds + 1]

    return nms_keep


def multiclass_nms_class_agnostic(boxes, scores, nms_thr, score_thr):
    """Multiclass NMS implemented inNumpy. Class-agnostic version."""
    cls_inds = scores.argmax(1)
    cls_scores = scores[np.arange(len(cls_inds)), cls_inds]

    valid_score_mask = cls_scores > score_thr
    if valid_score_mask.sum() == 0:
        return None
    valid_scores = cls_scores[valid_score_mask]
    valid_boxes = boxes[valid_score_mask]
    valid_cls_inds = cls_inds[valid_score_mask]
    nms_keep = nms(valid_boxes, valid_scores, nms_thr)
    if nms_keep:
        dets = np.concatenate(
            [valid_boxes[nms_keep], valid_scores[nms_keep, None], valid_cls_inds[nms_keep, None]], 1
        ).tolist()
    return dets


def decode_outputs(outputs, net_h, net_w, strides):
    """decode bounding boxes from model outputs"""
    grids = []
    expanded_strides = []

    hsizes = [net_h // stride for stride in strides]
    wsizes = [net_w // stride for stride in strides]

    for hsize, wsize, stride in zip(hsizes, wsizes, strides):
        xv, yv = np.meshgrid(np.arange(wsize), np.arange(hsize))
        grid = np.stack((xv, yv), 2).reshape(1, -1, 2)
        grids.append(grid)
        shape = grid.shape[:2]
        expanded_strides.append(np.full((*shape, 1), stride))

    grids = np.concatenate(grids, 1)
    expanded_strides = np.concatenate(expanded_strides, 1)
    outputs[..., :2] = (outputs[..., :2] + grids) * expanded_strides
    outputs[..., 2:4] = np.exp(outputs[..., 2:4]) * expanded_strides

    return outputs


def postprocess(image_pred, params):
    """postprocess for yolox model"""
    predictions = decode_outputs(image_pred, params['net_h'], params['net_w'], params['strides'])

    boxes = predictions[:, :4]
    scores = predictions[:, 4:5] * predictions[:, 5:]

    boxes_xyxy = np.ones_like(boxes)
    try:
        boxes_xyxy[:, 0] = np.clip((boxes[:, 0] - boxes[:, 2] / 2.) / params['net_w'], 0., 1.)  # [0, 1]
        boxes_xyxy[:, 1] = np.clip((boxes[:, 1] - boxes[:, 3] / 2.) / params['net_h'], 0., 1.)  # [0, 1]
        boxes_xyxy[:, 2] = np.clip((boxes[:, 0] + boxes[:, 2] / 2.) / params['net_w'], 0., 1.)  # [0, 1]
        boxes_xyxy[:, 3] = np.clip((boxes[:, 1] + boxes[:, 3] / 2.) / params['net_h'], 0., 1.)  # [0, 1]
    except ZeroDivisionError:
        pass

    detections = multiclass_nms_class_agnostic(boxes_xyxy, scores, params['nms_thre'], params['conf_thre'])

    return detections
