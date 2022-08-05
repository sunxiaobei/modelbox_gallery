:: Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

:: 如果HILENS_APP_NAME没有设置，则为本地仿真环境
@echo off
set BASE_PATH=%~dp0
set BASE_PATH_LINUX=%BASE_PATH:\=/%
if "%HILENS_APP_NAME%" == "" (
  set HILENS_APP_ROOT=%BASE_PATH_LINUX%..
  set IVA_SVC_CONFIG={"algorithm":{"multiTask":"no","algType":"mock"},"mockFile":"%BASE_PATH_LINUX%/mock_task.toml","svcInstanceId":"modelbox-instance-mock"}
  set HILENS_DATA_DIR=%BASE_PATH_LINUX%../hilens_data_dir
  set HILENS_IS_SIMULATE=YES
  set HILENS_MB_SDK_PATH=%BASE_PATH_LINUX%../../../SDKNAME
) else (
  set HILENS_MB_SDK_PATH=%HILENS_MB_SDK_ROOT%/sdk_SDKNAME
)
@echo on

set PATH=%PATH%;%HILENS_MB_SDK_PATH%/bin;%HILENS_APP_ROOT%/dependence

@echo off
if "%1" == "default" (
  set HILENS_MB_GRAPH_TYPE=
) else if "%1" == "" (
  set HILENS_MB_GRAPH_TYPE=
) else (
  set HILENS_MB_GRAPH_TYPE=_%1
)

if "%2" == "" (
  set HILENS_MB_LOG_LEVEL=INFO
) else (
  set HILENS_MB_LOG_LEVEL=%2
)
@echo on

modelbox.exe -c %HILENS_APP_ROOT%/graph/modelbox.conf

@echo off
if "%HILENS_IS_SIMULATE%" == "YES" (
  pause
)
@echo on
