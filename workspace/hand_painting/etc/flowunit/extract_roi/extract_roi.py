# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _flowunit as modelbox
import numpy as np


class extract_roiFlowUnit(modelbox.FlowUnit):
    def __init__(self):
        super().__init__()

    def open(self, config):
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):
        in_data = data_context.input("in_data")
        out_image = data_context.output("roi_image")

        for buffer_img in in_data:
            modelbox.info("ExtractROI")
            width = buffer_img.get('width')
            height = buffer_img.get('height')
            channel = buffer_img.get('channel')

            img_data = np.array(buffer_img.as_object(), dtype=np.uint8, copy=False)
            img_data = img_data.reshape(height, width, channel)

            box = buffer_img.get("bboxes")
            box = np.array(box).reshape(4,)
            img_roi = self.crop_bbox_img(box, img_data)
            h, w, _ = img_roi.shape
            img_roi = img_roi.flatten()
            img_buffer = modelbox.Buffer(self.get_bind_device(), img_roi)
            img_buffer.copy_meta(buffer_img)
            img_buffer.set("pix_fmt", "bgr")
            img_buffer.set("width", w)
            img_buffer.set("height", h)
            img_buffer.set("width_stride", w * 3)
            img_buffer.set("height_stride", h)
            out_image.push_back(img_buffer)

        return modelbox.Status.StatusCode.STATUS_SUCCESS
    
    def crop_bbox_img(self, bbox, image):
        x1, y1, x2, y2 = bbox
        bbox_img = image[y1:y2, x1:x2, :].copy()
        return bbox_img

    def close(self):
        return modelbox.Status()
