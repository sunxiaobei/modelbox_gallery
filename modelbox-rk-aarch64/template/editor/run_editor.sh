#!/bin/bash
# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

BASE_PATH=$(cd $(dirname $0);pwd)
export SDK_ROOT=${BASE_PATH}/..
export HILENS_MB_SDK_PATH=${SDK_ROOT}/SDKNAME
export PATH=${PATH}:${HILENS_MB_SDK_PATH}/bin
export LD_LIBRARY_PATH=${HILENS_MB_SDK_PATH}/lib

modelbox -f -V -c ${BASE_PATH}/editor_config_linux.conf -p ${BASE_PATH}/editor_server.pid
