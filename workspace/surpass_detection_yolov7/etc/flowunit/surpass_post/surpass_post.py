# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _flowunit as modelbox
import json
import numpy as np
from utils import YOLO7, draw


class surpass_postFlowUnit(modelbox.FlowUnit):
    def __init__(self):
        super().__init__()

    def open(self, config):
        label_path = config.get_string("label_path", "data/classes.txt")
        with open(label_path) as f:
            self.labels = f.readlines()
        self.labels = [x.strip() for x in self.labels]
        masks = np.array(config.get_int_list("masks", [])).reshape(3, 3)
        anchors = np.array(config.get_int_list("anchors", [])).reshape(-1, 2)
        self.strides = np.array(config.get_int_list("strides", []))
        conf_threshold = config.get_float("conf_threshold", 0.5)
        iou_threshold = config.get_float("iou_threshold", 0.4)
        self.yolov7 = YOLO7(conf_threshold, iou_threshold, anchors=anchors, masks=masks, strides=self.strides)
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):
        modelbox.info("Yolo7Post")

        input_feat1 = data_context.input("in_feat1")
        input_feat2 = data_context.input("in_feat2")
        input_feat3 = data_context.input("in_feat3")
        input_image = data_context.input("in_image")

        out_image = data_context.output("out_image")

        for buffer_feat1, buffer_feat2, buffer_feat3, buffer_img in zip(input_feat1, input_feat2, input_feat3, input_image):
            feat_data_1 = np.array(buffer_feat1.as_object(), copy=False)
            feat_data_2 = np.array(buffer_feat2.as_object(), copy=False)
            feat_data_3 = np.array(buffer_feat3.as_object(), copy=False)

            width = buffer_img.get("width")
            height = buffer_img.get("height")
            channel = buffer_img.get("channel")

            img_data = np.array(buffer_img.as_object(), copy=False)
            img_data = img_data.reshape((height, width, channel))

            buffer_meta = json.loads(buffer_img.get("buffer_meta"))

            feats = [np.transpose(feat.reshape(3, -1, buffer_meta["net_h"] // self.strides[idx],
                                               buffer_meta["net_w"] // self.strides[idx]), (2, 3, 0, 1))
                     for idx, feat in enumerate([feat_data_1, feat_data_2, feat_data_3])]

            bboxes, classes, scores = self.yolov7.yolov7_post_process(feats)

            draw(img_data, bboxes, scores, classes, self.labels, buffer_meta)

            add_buffer = modelbox.Buffer(self.get_bind_device(), img_data)
            add_buffer.copy_meta(buffer_img)
            out_image.push_back(add_buffer)

        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def close(self):
        return modelbox.Status()
