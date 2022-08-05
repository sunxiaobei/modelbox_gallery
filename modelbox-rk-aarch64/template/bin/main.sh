#!/bin/sh
# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

# 如果HILENS_APP_NAME没有设置，则为本地仿真环境
if [ "${HILENS_APP_NAME}" = "" ];then
  BASE_PATH=$(cd $(dirname $0);pwd)
  export HILENS_APP_ROOT=${BASE_PATH}/..
  export HILENS_DATA_DIR=${HILENS_APP_ROOT}/hilens_data_dir
  export HILENS_IS_SIMULATE="YES"
  export HILENS_MB_SDK_PATH=${HILENS_APP_ROOT}/../../SDKNAME
else
  export HILENS_MB_SDK_PATH=${HILENS_MB_SDK_ROOT}/sdk_SDKNAME
fi

export PATH=${PATH}:${HILENS_MB_SDK_PATH}//bin
export LD_LIBRARY_PATH=${HILENS_MB_SDK_PATH}/lib:${HILENS_APP_ROOT}/dependence
if [ "$1" = "default" -o "$1" = "" ]; then
  export HILENS_GRAPH_TYPE=
else
  export HILENS_GRAPH_TYPE=_$1
fi

if [ "$2" = "" ]; then
  export HILENS_MB_LOG_LEVEL="INFO"
else
  export HILENS_MB_LOG_LEVEL="$2"
fi

modelbox-tool -verbose -log-level ${HILENS_MB_LOG_LEVEL} flow -run ${HILENS_APP_ROOT}/graph/MODULENAME${HILENS_MB_GRAPH_TYPE}.toml
