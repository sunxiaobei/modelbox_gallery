#!/bin/bash
# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

BASE_PATH=$(cd $(dirname "${BASH_SOURCE[0]}") && pwd)
export PATH=${PATH}:${BASE_PATH}/modelbox-rk-aarch64/bin
export LD_LIBRARY_PATH=${BASE_PATH}/modelbox-rk-aarch64/lib
