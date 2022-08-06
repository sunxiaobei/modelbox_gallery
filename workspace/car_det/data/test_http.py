#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

import os
import cv2
import json
import base64
import http.client


class HttpConfig:
    '''http调用的参数配置'''
    def __init__(self, host_ip, port, url, img_base64_str):
        self.hostIP = host_ip
        self.Port = port

        self.httpMethod = "POST"
        self.requstURL = url
        self.headerdata = {
            "Content-Type": "application/json"
        }
        self.test_data = {
            "image_base64": img_base64_str
        }
        self.body = json.dumps(self.test_data)


def read_image(img_path):
    '''读取图片数据并转为base64编码的字符串'''
    img_data = cv2.imread(img_path)
    img_str = cv2.imencode('.jpg', img_data)[1].tostring()
    img_bin = base64.b64encode(img_str)
    img_base64_str = str(img_bin, encoding='utf8')
    return img_data, img_base64_str

    
def decode_car_bboxes(bbox_str, input_shape):
    try:
        coco_car_labels = [2, 5, 7]  # car, bus, truck
        bboxes = json.loads(json.loads(bbox_str)['det_result'])
        car_bboxes = list(filter(lambda x: int(x[5]) in coco_car_labels, bboxes))
    except Exception as ex:
        print(str(ex))
        return []
    else:
        for bbox in car_bboxes:
            bbox[0] = int(bbox[0] * input_shape[1])
            bbox[1] = int(bbox[1] * input_shape[0])
            bbox[2] = int(bbox[2] * input_shape[1])
            bbox[3] = int(bbox[3] * input_shape[0])
        return car_bboxes


def draw_bboxes(img_data, bboxes):
    '''画框'''
    for bbox in bboxes:
        x1, y1, x2, y2, _, _ = bbox
        color = (0, 0, 255)
        cv2.rectangle(img_data, (x1, y1), (x2, y2), color, 2)
    return img_data


def test_image(img_path, ip, port, url):
    '''单张图片测试'''
    img_data, img_base64_str = read_image(img_path)
    http_config = HttpConfig(ip, port, url, img_base64_str)

    conn = http.client.HTTPConnection(host=http_config.hostIP, port=http_config.Port)
    conn.request(method=http_config.httpMethod, url=http_config.requstURL,
                body=http_config.body, headers=http_config.headerdata)

    response = conn.getresponse().read().decode()
    print('response: ', response)

    bboxes = decode_car_bboxes(response, img_data.shape)
    imt_out = draw_bboxes(img_data, bboxes)
    cv2.imwrite('./result-' + os.path.basename(img_path), imt_out)


if __name__ == "__main__":
    port = 8083
    ip = "127.0.0.1"
    url = "/v1/car_det"
    img_path = "./car_test_pic.jpg"
    test_image(img_path, ip, port, url)
