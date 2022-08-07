# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _flowunit as modelbox
import cv2
import json
import numpy as np


class draw_pose_lightFlowUnit(modelbox.FlowUnit):
    # Derived from modelbox.FlowUnit
    def __init__(self):
        super().__init__()

    def open(self, config):
        # Open the flowunit to obtain configuration information
        self.colors = [[255, 0, 0], [255, 85, 0], [255, 170, 0], [255, 255, 0], 
                       [170, 255, 0], [85, 255, 0], [0, 255, 0], [0, 255, 85], 
                       [0, 255, 170], [0, 255, 255], [0, 170, 255], [0, 85, 255], 
                       [0, 0, 255], [85, 0, 255], [170, 0, 255], [255, 0, 255], 
                       [255, 0, 170], [255, 0, 85], [85, 85, 255], [170, 170, 255], [170, 255, 170]]
        self.cnt_colors = len(self.colors)

        self.BODY_PARTS_KPT_IDS = [[1, 2], [1, 5], [2, 3], [3, 4], [5, 6], [6, 7], [1, 8], [8, 9], [9, 10], [1, 11],
                                   [11, 12], [12, 13], [1, 0], [0, 14], [14, 16], [0, 15], [15, 17], [2, 16], [5, 17]]
        self.BODY_PARTS_PAF_IDS = ([12, 13], [20, 21], [14, 15], [16, 17], [22, 23], [24, 25], [0, 1], [2, 3], [4, 5],
                                   [6, 7], [8, 9], [10, 11], [28, 29], [30, 31], [34, 35], [32, 33], [36, 37], [18, 19], [26, 27])

        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):
        # Process the data
        # modelbox.info('draw_pose_light')
        in_image = data_context.input("in_image")
        in_pose = data_context.input("in_pose")
        out_image = data_context.output("out_image")

        for buffer_img, buffer_pose in zip(in_image, in_pose):
            width = buffer_img.get('width')
            height = buffer_img.get('height')
            channel = buffer_img.get('channel')

            img_data = np.array(buffer_img.as_object(), copy=False)
            img_data = img_data.reshape((height, width, channel))

            pose_str = buffer_pose.as_object()
            pose_data = self.decode_pose(pose_str, (height, width))

            img_out = img_data.copy()
            self.draw_pose(img_out, pose_data)

            out_buffer = modelbox.Buffer(self.get_bind_device(), img_out)
            out_buffer.copy_meta(buffer_img)
            out_image.push_back(out_buffer)

        return modelbox.Status.StatusCode.STATUS_SUCCESS
    
    def decode_pose(self, pose_str, input_shape):
        try:
            result_json = json.loads(pose_str)
            pose = json.loads(result_json['pose_result'])
        except Exception as ex:
            modelbox.error(str(ex))
            return []
        else:
            pose = np.array(pose)
            pose[..., 0] = pose[..., 0] * input_shape[1]
            pose[..., 1] = pose[..., 1] * input_shape[0]
            return pose

    def draw_pose(self, img_data, all_poses):
        for pose in all_poses:
            for part_id in range(len(self.BODY_PARTS_PAF_IDS) - 2):
                kpt_a_id = self.BODY_PARTS_KPT_IDS[part_id][0]
                global_kpt_a_id = pose[kpt_a_id, 0]
                color_a = self.colors[kpt_a_id % self.cnt_colors]
                if global_kpt_a_id > 0:
                    x_a, y_a = pose[kpt_a_id]
                    cv2.circle(img_data, (int(x_a), int(y_a)), 3, color_a, -1)
                kpt_b_id = self.BODY_PARTS_KPT_IDS[part_id][1]
                global_kpt_b_id = pose[kpt_b_id, 0]
                color_b = self.colors[kpt_b_id % self.cnt_colors]
                if global_kpt_b_id > 0:
                    x_b, y_b = pose[kpt_b_id]
                    cv2.circle(img_data, (int(x_b), int(y_b)), 3, color_b, -1)
                if global_kpt_a_id > 0 and global_kpt_b_id > 0:
                    cv2.line(img_data, (int(x_a), int(y_a)), (int(x_b), int(y_b)), color_b, 2)

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
