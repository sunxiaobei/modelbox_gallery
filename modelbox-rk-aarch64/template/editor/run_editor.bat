:: Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

@echo off
set BASE_PATH=%~dp0
set BASE_PATH_LINUX=%BASE_PATH:\=/%
set SDK_ROOT=%BASE_PATH_LINUX%..
set HILENS_MB_SDK_PATH=%BASE_PATH_LINUX%../SDKNAME

SET PATH=%PATH%;%HILENS_MB_SDK_PATH%/bin
@echo on
modelbox.exe -c %BASE_PATH%/editor_config_win10.conf
pause