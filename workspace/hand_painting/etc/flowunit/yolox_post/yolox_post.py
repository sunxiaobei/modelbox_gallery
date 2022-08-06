# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _flowunit as modelbox

import numpy as np 
from yolox_utils import postprocess, expand_bboxes_with_filter, draw_color_palette


class yolox_postFlowUnit(modelbox.FlowUnit):
    # Derived from modelbox.FlowUnit
    def __init__(self):
        super().__init__()

    def open(self, config):
        self.net_h = config.get_int('net_h', 320)
        self.net_w = config.get_int('net_w', 320)
        self.num_classes = config.get_int('num_classes', 2)
        self.num_grids = int((self.net_h / 32) * (self.net_w / 32)) * (1 + 2*2 + 4*4)
        self.conf_thre = config.get_float('conf_threshold', 0.3)
        self.nms_thre = config.get_float('iou_threshold', 0.4)
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):
        modelbox.info("YOLOX POST")
        in_image = data_context.input("in_image")
        in_feat = data_context.input("in_feat")

        has_hand = data_context.output("has_hand")
        no_hand = data_context.output("no_hand")

        for buffer_img, buffer_feat in zip(in_image, in_feat):
            width = buffer_img.get('width')
            height = buffer_img.get('height')
            channel = buffer_img.get('channel')

            img_data = np.array(buffer_img.as_object(), copy=False)
            img_data = img_data.reshape((height, width, channel))

            feat_data = np.array(buffer_feat.as_object(), copy=False)
            feat_data = feat_data.reshape((self.num_grids, self.num_classes + 5))

            ratio = (self.net_h / height, self.net_w / width)
            bboxes = postprocess(feat_data, (self.net_h, self.net_w), self.conf_thre, self.nms_thre, ratio)
            box = expand_bboxes_with_filter(bboxes, width, height, ratio=1.2)

            if box:
                buffer_img.set("bboxes", box)
                has_hand.push_back(buffer_img)

            else:
                draw_color_palette(img_data)
                img_buffer = modelbox.Buffer(self.get_bind_device(), img_data)
                img_buffer.copy_meta(buffer_img)
                no_hand.push_back(img_buffer)
            
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def close(self):
        # Close the flowunit
        return modelbox.Status()
