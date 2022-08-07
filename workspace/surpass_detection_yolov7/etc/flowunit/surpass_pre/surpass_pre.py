# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

#!/usr/bin/env python
# -*- coding: utf-8 -*-
import _flowunit as modelbox
import numpy as np
import cv2
import json


class surpass_preFlowUnit(modelbox.FlowUnit):
    def __init__(self):
        super().__init__()

    def open(self, config):
        self.net_h = config.get_int('net_h', 320)
        self.net_w = config.get_int('net_w', 320)
        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def process(self, data_context):

        in_image = data_context.input("in_image")
        out_image = data_context.output("out_image")
        resized_out = data_context.output("resized_image")

        for buffer_img in in_image:
            
            width = buffer_img.get('width')
            height = buffer_img.get('height')
            channel = buffer_img.get('channel')

            img_data = np.array(buffer_img.as_object(), copy=False)
            img_data = img_data.reshape((height, width, channel))

            resized_image, ratio, (dw, dh) = self.letterbox(img_data)

            h, w, c = resized_image.shape
            resized_image = resized_image.flatten()
            img_buffer = modelbox.Buffer(self.get_bind_device(), resized_image)
            img_buffer.copy_meta(buffer_img)
            img_buffer.set("pix_fmt", "bgr")
            img_buffer.set("width", w)
            img_buffer.set("height", h)
            img_buffer.set("width_stride", w * 3)
            img_buffer.set("height_stride", h)
            resized_out.push_back(img_buffer)

            buffer_meta = {"ratio": ratio, "dh": dh, "dw": dw, "net_h": self.net_h, "net_w": self.net_w}
            buffer_img.set("buffer_meta", json.dumps(buffer_meta))
            out_image.push_back(buffer_img)

        return modelbox.Status.StatusCode.STATUS_SUCCESS

    def letterbox(self, img, color=(114, 114, 114)):
        shape = img.shape[:2]
        new_shape = (self.net_h, self.net_w)
        r = min(new_shape[0] / shape[0], new_shape[1] / shape[1])

        new_unpad = int(round(shape[1] * r)), int(round(shape[0] * r))
        dw, dh = new_shape[1] - new_unpad[0], new_shape[0] - new_unpad[1] 

        dw /= 2
        dh /= 2

        if shape[::-1] != new_unpad: 
            img = cv2.resize(img, new_unpad, interpolation=cv2.INTER_LINEAR)
        top, bottom = int(round(dh - 0.1)), int(round(dh + 0.1))
        left, right = int(round(dw - 0.1)), int(round(dw + 0.1))
        img = cv2.copyMakeBorder(img, top, bottom, left, right, cv2.BORDER_CONSTANT, value=color)
        return img, r, (dw, dh)

    def close(self):
        return modelbox.Status()
