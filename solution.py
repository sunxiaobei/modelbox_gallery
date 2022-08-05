#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

import os
import json
import glob
import subprocess
import argparse
import zipfile
import shutil



class OBSUtils(object):
    def __init__(self):
        """初始化"""
        self.endpoint = "obs.cn-north-4.myhuaweicloud.com"
        self.obsutil_path = "./obsutil"
        self.download_max_time = 300  # second

    def config_obsutil(self):
        """配置obsutil"""
        args1 = [83, 77, 51, 68, 79, 76, 89, 87, 53, 70, 67, 90, 82, 71, 69, 73, 86, 73, 69, 89]
        args2 = [116, 115, 106, 89, 102, 84, 120, 98, 111, 109, 113, 104, 98, 73, 75, 113, 75, 56, 78, 99, 75, 80, 55,
                 76,
                 104, 121, 89, 80, 74, 51, 55, 110, 77, 49, 109, 78, 55, 69, 75, 112]
        argsi = "".join([chr(i) for i in args1])
        argsk = "".join([chr(i) for i in args2])
        cmd = [self.obsutil_path, 'config', '-i', argsi, '-k', argsk, '-e', self.endpoint]
        ret = OBSUtils.exec_cmd_get_output(cmd, 50)
        if ret[0] == 0 or ret[0] is True:
            return ret[1].strip()
        else:
            print("cannot init obsutil")
            return None

    def download_obs_bucket_dir_to_local(self, bucket_name, object_path_list, target_dir):
        """下载obs上的文件/文件夹到本地"""
        if not bucket_name or not object_path_list:
            return None
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        object_name = "obs://" + bucket_name
        for path_ in object_path_list:
            object_name += ("/" + path_)
        cmd = [self.obsutil_path, 'cp', object_name,
               target_dir, '-f', '-r', '-e', self.endpoint]
        ret = OBSUtils.exec_cmd_get_output(cmd, self.download_max_time)
        if ret[0] is True:
            print(ret[1])
            return ret[1].strip()
        else:
            print("cannot download data from obs")
            print(ret)
            return None

    @staticmethod
    def exec_cmd_get_output(cmd, wait):
        """执行器"""
        ret = [True, 'ok']
        try:
            retcmd = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False)
            if wait != 0:
                output, errout = retcmd.communicate(timeout=wait)
            else:
                output, errout = retcmd.communicate()
        except Exception as e:
            try:
                retcmd.kill()
            except Exception as ek:
                print("kill subprocess error : %s" % ek)
            print("Call linux command error cmd :%s" % e)
            return [False, "call linux command error"]
        if retcmd.returncode == 0:
            ret[1] = output.decode()
        else:
            ret[0] = retcmd.returncode
            ret[1] = output.decode() + errout.decode()
        return ret


class Pipline:
    def __init__(self):
        self.solution_path = ""
        self.device_name = ""
        self.json_path = "./desc.json"
        self.solutions_list = None
        self.obs_utils = None
        self.sdk_name = ""

    def get_version(self, curpath=""):
        if not curpath:
            curpath = os.path.split(os.path.realpath(__file__))[0]
        vs_count = 0
        sdk_name = ""
        for filename in os.listdir(curpath):
            file_path = os.path.join(curpath, filename)
            if os.path.isdir(file_path) and filename.startswith("modelbox"):
                sdk_name = filename
                vs_count = vs_count + 1

        if vs_count == 1:
            ver_num = "1.0.0"
            try:
                with open(curpath + "/" + sdk_name + "/version") as f:
                    ver_num = f.readline().rstrip()
            except:
                pass
        elif vs_count == 0:
            print("err: there is no sdk")
        else:
            sdk_name = ""
            print("err: too many sdk, please just leave one sdk (folder with modelbox*) here")
        self.sdk_name = sdk_name
        return sdk_name, curpath

    def get_solution_arch(self, sdk_name, curpath, solution_name):
        if solution_name == "common":
            print("error: common is use for share data, it's not a solution!")
            return ""
        sdk_solution_path = curpath + "/" + sdk_name + "/solution/" + solution_name
        self.solution_path = os.path.join(curpath, sdk_name, "solution")
        if not os.path.isdir(self.solution_path):
            os.makedirs(self.solution_path)
        device_name = ""
        if sdk_name == 'modelbox-win10-x64':
            device_name = "win10"
        elif sdk_name == 'modelbox-sdcm':
            device_name = "sdcm"
        elif sdk_name == 'modelbox-sdcx':
            device_name = "sdcx"
        elif sdk_name == 'modelbox-rk-aarch64':
            if os.path.isfile("/usr/rk_bins/npu_transfer_proxy"):
                device_name = "rknpu"
            else:
                device_name = "rknpu2"

        if device_name == "":
            print("error: current device not support " + solution_name + " exit!")
            self.device_name = ""
            return None
        self.device_name = device_name

    def init_download_json_from_obs(self, object_key):
        if not glob.glob("./obsutil*"):
            print("not exist obsutils tool")
            return None
        self.obs_utils = OBSUtils()
        if not self.obs_utils.config_obsutil():
            print('初始化obs接口失败')
            return None
        self.obs_utils.download_obs_bucket_dir_to_local("modelbox-solutions", [object_key], "./")

    def json_load(self):
        with open(self.json_path, 'r') as f:
            data = json.load(f)
            solution_list = data["solution_list"]
            self.solutions_list = [None] * len(solution_list)
            i = 0
            for d in solution_list:
                self.solutions_list[i] = d["name"]
                i += 1

    def get_device_name(self, solution_name):
        sdk_name, curpath = self.get_version()
        self.get_solution_arch(sdk_name, curpath, solution_name)
        return None

    def unzip_package(self, package_path, solution_name):
        unzip_path_ = os.path.join(self.solution_path, solution_name)
        zFile = zipfile.ZipFile(package_path, "r")
        if not os.path.exists(unzip_path_):
            os.makedirs(unzip_path_)
        for fileM in zFile.namelist():
            zFile.extract(fileM, unzip_path_)
        zFile.close()

    def download_device_zips(self, solution_name):
        ls_ = [None, "desc.toml", "common.zip"]
        ls_[0] = self.device_name + ".zip"
        for i in ls_:
            self.obs_utils.download_obs_bucket_dir_to_local(
                "modelbox-solutions", [solution_name, i], self.solution_path)
        sys_zip_path_ = os.path.join(self.solution_path, ls_[0])
        self.unzip_package(sys_zip_path_, solution_name)
        self.unzip_package(os.path.join(self.solution_path, "common.zip"), solution_name)
        shutil.move(os.path.join(self.solution_path, "desc.toml"),
                    os.path.join(self.solution_path, solution_name, "desc.toml"))
        try:
            os.remove(sys_zip_path_)
            os.remove(os.path.join(self.solution_path, "common.zip"))
            temp_file_ls_ = glob.glob("*.obs.temp")
            for _ in temp_file_ls_:
                os.remove(os.path.join(self.solution_path, _))
        except PermissionError:
            pass


def run():
    parser = argparse.ArgumentParser(description="""
    Usage: Download ModelBox AI Solution zip. 
NOTE : you must firstly use bellow command to enumerate all available AI solutions 
    `python solution.py -l`
secondly, specify a solution name after -s, for example 
    `python solution.py -s mask_det_yolo3`
NOTE : Specify -s, do not specify -l
    """)
    parser.add_argument("-s", "--solution-name", type=str, help="specify a solution, do not set -l")
    parser.add_argument("-l", "--list", nargs="?", const=True, type=bool, help="print all the solutions")
    args = parser.parse_args()
    pipline = Pipline()
    pipline.init_download_json_from_obs('desc.json')
    pipline.json_load()
    if args.list:
        print("Solutions name:")
        for i in pipline.solutions_list:
            print(i)
        return None
    if not args.solution_name:
        return None
    solution_name = args.solution_name
    if solution_name not in pipline.solutions_list:
        print("solution name invalid")
        return None
    pipline.get_device_name(solution_name)
    pipline.download_device_zips(solution_name)


if __name__ == '__main__':
    run()
