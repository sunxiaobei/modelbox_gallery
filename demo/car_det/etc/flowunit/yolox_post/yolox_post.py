#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

import _flowunit as modelbox
import json
from yolox_utils import postprocess
# important, must put "import numpy as np" later, otherwise, windows crash, rk wrong data
import numpy as np


class yolox_postFlowUnit(modelbox.FlowUnit):
    def __init__(self):
        self.index = 0
        self.num_classes = 80
        super().__init__()

    def open(self, config):
        self.params = {}
        self.params['net_h'] = config.get_int('net_h', 288)
        self.params['net_w'] = config.get_int('net_w', 512)
        self.params['num_classes'] = config.get_int('num_classes', 80)
        self.params['strides'] = config.get_int_list('strides', [8, 16, 32])
        self.params['conf_thre'] = config.get_float('conf_threshold', 0.3)
        self.params['nms_thre'] = config.get_float('iou_threshold', 0.4)
        self.num_classes = config.get_int('num_classes', 80)

        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):
        in_feat = data_context.input("in_feat")
        out_data = data_context.output("out_data")

        for buffer_feat in in_feat:
            feat_data = np.array(buffer_feat.as_object(), copy=False)
            feat_data = feat_data.reshape((-1, self.num_classes + 5))

            bboxes = postprocess(feat_data, self.params)
            result = {"det_result": str(bboxes)}
            modelbox.debug(f'result for {self.index}-th image is {result}')
            self.index += 1

            result_str = json.dumps(result)
            out_buffer = modelbox.Buffer(self.get_bind_device(), result_str)
            out_data.push_back(out_buffer)

        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def close(self):
        return modelbox.Status()

    def data_pre(self, data_context):
        return modelbox.Status()

    def data_post(self, data_context):
        return modelbox.Status()
