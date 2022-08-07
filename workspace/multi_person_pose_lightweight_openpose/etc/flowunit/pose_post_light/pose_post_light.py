# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _flowunit as modelbox
import json
import numpy as np
from pose_utils_light import *


class pose_post_lightFlowUnit(modelbox.FlowUnit):
    # Derived from modelbox.FlowUnit
    def __init__(self):
        super().__init__()

    def open(self, config):
        # Open the flowunit to obtain configuration information
        self.net_h = config.get_int('net_h', 288)
        self.net_w = config.get_int('net_w', 512)
        self.num_kpts = config.get_int('num_kpts', 18)
        self.stride = config.get_int('stride', 8)
        self.upsample_ratio = config.get_int('upsample_ratio', 4)
        self.feat_shape = (self.net_h // self.stride, self.net_w // self.stride)
        self.params = {'net_h': self.net_h, 'net_w': self.net_w, 'num_kpts': self.num_kpts,
                        'stride': self.stride, 'upsample_ratio':self.upsample_ratio}
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):
        # Process the data
        in_heatmaps = data_context.input("in_heatmaps")
        in_pafs = data_context.input("in_pafs")
        out_pose = data_context.output("out_pose")

        for buffer_heatmaps, buffer_pafs in zip(in_heatmaps, in_pafs):
            heatmaps = np.array(buffer_heatmaps.as_object(), copy=False)
            heatmaps = heatmaps.reshape((self.num_kpts+1, self.feat_shape[0], self.feat_shape[1]))

            pafs = np.array(buffer_pafs.as_object(), copy=False)
            pafs = pafs.reshape((2*(self.num_kpts+1), self.feat_shape[0], self.feat_shape[1]))

            pose = get_pose(heatmaps, pafs, self.params)
            result = {"pose_result": str(pose)}
            
            result_str = json.dumps(result)
            out_buffer = modelbox.Buffer(self.get_bind_device(), result_str)
            out_pose.push_back(out_buffer)

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
