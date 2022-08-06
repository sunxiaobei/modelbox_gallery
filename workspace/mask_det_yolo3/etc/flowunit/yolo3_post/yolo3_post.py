# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _flowunit as modelbox

import json
import numpy as np
from yolo3_utils import Yolo3

class yolo3_postFlowUnit(modelbox.FlowUnit):
    # Derived from modelbox.FlowUnit
    def __init__(self):
        super().__init__()

    def open(self, config):
        # Open the flowunit to obtain configuration information
        params = {}
        params['net_h'] = config.get_int('net_h', 288)
        params['net_w'] = config.get_int('net_w', 512)
        params['labels'] = config.get_string_list('labels', [])
        params['strides'] = config.get_int_list('strides', [])
        params['anchors'] = config.get_int_list('anchors', [])
        params['conf_threshold'] = config.get_float('conf_threshold', 0.3)
        params['iou_threshold'] = config.get_float('iou_threshold', 0.4)
        params['flag_hwc'] = config.get_bool('flag_hwc', False)

        self.index = 0
        self.yolo3 = Yolo3(params)
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):
        # Process the data
        input_feat1 = data_context.input("in_feat1")
        input_feat2 = data_context.input("in_feat2")
        input_feat3 = data_context.input("in_feat3")
        out_data = data_context.output("out_data")

        for buffer_feat1, buffer_feat2, buffer_feat3 in zip(input_feat1, input_feat2, input_feat3):
            feat_data_1 = np.array(buffer_feat1.as_object(), copy=False)
            feat_data_2 = np.array(buffer_feat2.as_object(), copy=False)
            feat_data_3 = np.array(buffer_feat3.as_object(), copy=False)
            
            feats = [feat_data_3, feat_data_2, feat_data_1]
            bboxes = self.yolo3.get_result(feats)
            result = {"det_result": str(bboxes)}
            modelbox.debug(f'result for {self.index}-th image is : {result}')
            self.index += 1
            
            result_str = json.dumps(result)
            out_buffer = modelbox.Buffer(self.get_bind_device(), result_str)
            out_data.push_back(out_buffer)

        return modelbox.Status.StatusCode.STATUS_SUCCESS

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
