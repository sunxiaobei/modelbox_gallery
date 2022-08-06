# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _flowunit as modelbox
import numpy as np
from paint_utils import hand_pose, draw_click_lines, draw_color_palette


class paintingFlowUnit(modelbox.FlowUnit):
    def __init__(self):
        super().__init__()

    def open(self, config):
        self.draw_pts = []
        self.tmp_array = np.array([], dtype=np.uint8)
        self.pick_color = [255, 255, 255]
        self.heatmap_h = config.get_int('heatmap_h', 64)
        self.heatmap_w = config.get_int('heatmap_w', 64)
        self.kps = config.get_int('kps', 21)
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):
        modelbox.info("Draw")
        in_image = data_context.input("in_image")
        in_pose = data_context.input("in_pose")
        out_paint = data_context.output("out_paint")

        for image, buffer_feat in zip(in_image, in_pose):
            width = image.get('width')
            height = image.get('height')
            channel = image.get('channel')
            out_img = np.array(image.as_object(), dtype=np.uint8, copy=False)
            out_img = out_img.reshape(height, width, channel)

            bboxes = image.get("bboxes")
            bboxes = np.array(bboxes).reshape(4,)
            pose_feat = np.array(buffer_feat.as_object(), dtype=np.float32, copy=False)
            pose_data = self.decode_pose(pose_feat)

            palette_left = draw_color_palette(out_img)

            self.draw_pts, self.tmp_array, self.pick_color = hand_pose(out_img, pose_data, bboxes, self.draw_pts, palette_left, self.tmp_array, self.pick_color)

            out_img = draw_click_lines(out_img, self.draw_pts, self.tmp_array)
            
            add_buffer = modelbox.Buffer(self.get_bind_device(), out_img)
            add_buffer.copy_meta(image)
            out_paint.push_back(add_buffer)
        
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def close(self):
        return modelbox.Status()

    def decode_pose(self, pose_feat):
        heatmaps = pose_feat.reshape((self.kps, self.heatmap_h, self.heatmap_w))
        heatmaps_reshaped = heatmaps.reshape((self.kps, -1))
        idx = np.argmax(heatmaps_reshaped, 1).reshape((self.kps, 1))
        maxvals = np.amax(heatmaps_reshaped, 1).reshape((self.kps, 1))
        preds = np.tile(idx, (1, 2)).astype(np.float32)
        preds[:, 0] = preds[:, 0] % self.heatmap_w
        preds[:, 1] = preds[:, 1] // self.heatmap_w

        preds = np.where(np.tile(maxvals, (1, 2)) > 0.0, preds, -1)

        for k in range(self.kps):
            heatmap = heatmaps[k]
            px = int(preds[k][0])
            py = int(preds[k][1])

            if 1 < px < self.heatmap_w - 1 and 1 < py < self.heatmap_h - 1:
                diff = np.array([
                    heatmap[py][px + 1] - heatmap[py][px - 1],
                    heatmap[py + 1][px] - heatmap[py - 1][px]
                ])
                preds[k] += np.sign(diff) * .25
        all_preds = np.zeros((preds.shape[0], 3), dtype=np.float32)
        all_preds[:, 0:2] = preds
        all_preds[:, 2:3] = maxvals

        return all_preds