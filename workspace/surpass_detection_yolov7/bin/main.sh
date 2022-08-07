#!/bin/sh
# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

# 如果HILENS_APP_NAME没有设置，则为本地仿真环境
if [ "${HILENS_APP_NAME}" = "" ]; then
  BASE_PATH=$(cd $(dirname $0);pwd)
  export HILENS_APP_ROOT=${BASE_PATH}/..
  export IVA_SVC_CONFIG="{\"algorithm\":{\"multiTask\":\"no\",\"algType\":\"mock\"},\"mockFile\":\"${BASE_PATH}/mock_task.toml\",\"svcInstanceId\":\"modelbox-instance-mock\"}"
  export HILENS_DATA_DIR=${HILENS_APP_ROOT}/hilens_data_dir
  mkdir -p ${HILENS_DATA_DIR}
  export HILENS_IS_SIMULATE=YES
  export HILENS_MB_SDK_PATH=${HILENS_APP_ROOT}/../../modelbox-rk-aarch64
  HILENS_MB_PID_NAME=${HILENS_DATA_DIR}/hilens_modelbox_server_$RANDOM.pid
else
  export HILENS_MB_SDK_PATH=${HILENS_MB_SDK_ROOT}/sdk_modelbox-rk-aarch64
  HILENS_MB_PID_NAME=${HILENS_DATA_DIR}/hilens_modelbox_server.pid
fi

export PATH=${PATH}:${HILENS_MB_SDK_PATH}/bin
export LD_LIBRARY_PATH=${HILENS_MB_SDK_PATH}/lib:${HILENS_APP_ROOT}/dependence

if [ -e /etc/os-release ]; then
  IS_DEBAIN=$(cat /etc/os-release | grep debian | awk '{print $1}')
  if [ ! -z "${IS_DEBAIN}" ]; then
    echo "debain os need load libgomp"
    export LD_PRELOAD=/usr/lib/aarch64-linux-gnu/libgomp.so.1:${LD_PRELOAD}
  fi
fi

if [ "$1" = "default" -o "$1" = "" ]; then
  export HILENS_MB_GRAPH_TYPE=
else
  export HILENS_MB_GRAPH_TYPE=_$1
fi

if [ "$2" = "" ]; then
  export HILENS_MB_LOG_LEVEL=INFO
else
  export HILENS_MB_LOG_LEVEL=$2
fi

modelbox -n "keepname" -k 30 -f -V -c ${HILENS_APP_ROOT}/graph/modelbox.conf -p ${HILENS_MB_PID_NAME}
rm -rf ${HILENS_MB_PID_NAME}
if [ "${HILENS_IS_SIMULATE}" = "YES" ];then
  # delete cache when local-run, avoid cache not refresh
  rm -rf ${HILENS_APP_ROOT}/bin/modelbox-driver-info
fi
