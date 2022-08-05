#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

import sys
import os
import getopt
import shutil
import pathlib
import subprocess
import platform
import json

def is_name_valid(name):
    name = name.replace('_', '')
    ok = name.isalnum()
    if (not ok):
        print(name + " not valid, only 0-9,a-z,A-z and _ is allowed")
    return ok

def sed_file(src, dst, module_name, sdk_name, editor_ip="127.0.0.1"):
    fin = open(src, 'r', encoding='utf-8')
    fout = open(dst, 'wb')
    ip_port = ""
    port_start = editor_ip.find(":")
    if (port_start >= 0):
        ip_port = editor_ip[port_start + 1::]
        editor_ip = editor_ip[0:port_start:]

    for line in fin:
        line = line.replace('\r', '')
        line = line.replace('MODULENAME', module_name)
        line = line.replace('SDKNAME', sdk_name)
        line = line.replace('EDITOR_IP', editor_ip)
        if (ip_port != "" and line.startswith("port")):
            line = line.replace('1104', ip_port)
        fout.write(line.encode('utf-8'))

    fin.close()
    fout.close()


def add_inout_port(src, json_cfg, device, module_name):
    retstr = ''
    cfg = None
    try:
        cfg = json.loads(json_cfg)
        if (cfg["desc"] == ""):
            cfg["desc"] = "description"

        fin = open(src, 'r', encoding='utf-8')
        for line in fin:
            line = line.replace('\r', '')
            line = line.replace('MODULENAME', module_name)
            line = line.replace('description = "description"',
                                'description = "' + cfg["desc"] + '"')
            if (line.startswith("# Input ports description")):
                break
            retstr += line

        fin.close()
        retstr += "# Input ports description\n[input]\n"
        index = 1
        for input in cfg["input"]:
            retstr += "[input.input" + \
                str(index) + \
                "] # Input port number, the format is input.input[N]\n"
            retstr += 'name = "' + input["name"] + '" # Input port name\n'
            type_str = "uint8"
            if ("type" in input):
                type_str = input["type"]
            retstr += 'type = "' + type_str + '"  # input port data type ,e.g. float or uint8\n'
            real_device = device
            if (input["device"] == "cpu"):
                real_device = "cpu"
            retstr += 'device = "' + \
                str(real_device) + '"  # input buffer type\n'
            index += 1

        if (not "output" in cfg):
            return retstr, cfg
        retstr += "\n# Output ports description\n[output]\n"
        index = 1
        for output in cfg["output"]:
            retstr += "[output.output" + \
                str(index) + \
                "] # Output port number, the format is output.output[N]\n"
            retstr += 'name = "' + output["name"] + '" # Output port name\n'
            type_str = "float"
            if ("type" in output):
                type_str = output["type"]
            retstr += 'type = "' + type_str + \
                '"  # output port data type ,e.g. float or uint8\n'
            index += 1

    except Exception as e:
        print("create flowunit error: ")
        print(e)
        retstr = ''
    return retstr, cfg


def copy_sdk_win(src, dst):
    shutil.copytree(src+"/bin", dst+"/bin", symlinks=True)
    shutil.copytree(src+"/flowunit", dst+"/flowunit", symlinks=True)


def copy_sdk_linux(src, dst):
    shutil.copytree(src+"/bin", dst+"/bin", symlinks=True)
    shutil.copytree(src+"/flowunit", dst+"/flowunit", symlinks=True)
    pathlib.Path(dst + "/lib").mkdir(parents=True, exist_ok=True)
    for filename in os.listdir(src+"/lib"):
        if (not os.path.isdir(os.path.join(src+"/lib", filename))) and ".so" in filename:
            shutil.copyfile(src + "/lib/" + filename, dst +
                            "/lib/" + filename, follow_symlinks=False)


def get_device(sdk_name):
    if sdk_name.startswith('modelbox-rk'):
        return 'rknpu'
    elif sdk_name.startswith('modelbox-sdc'):
        return 'sdc'
    return 'cpu'


def get_osext(sdk_name):
    if sdk_name.startswith('modelbox-win10'):
        return '.bat'
    return '.sh'


def check_path(curpath, proj_name):
    if (proj_name == ""):
        print(
            "error: project name is null")
        return "", ""
    workspace_path = os.path.join(curpath, "workspace")
    proj_path = os.path.join(workspace_path, proj_name)
    if (not os.path.exists(proj_path)):
        print("error: project:" + proj_name + " is not exist")
        return "", ""
    return workspace_path, proj_path


def get_solution_arch(vs_string, solution_name, curpath):
    sdk_solution_path = curpath + "/" + vs_string + "/solution/" + solution_name
    device_name = ""
    if vs_string == 'modelbox-win10-x64':
        device_name = "win10"
    elif vs_string == 'modelbox-sdcm':
        device_name = "sdcm"
    elif vs_string == 'modelbox-sdcx':
        device_name = "sdcx"
    elif vs_string == 'modelbox-rk-aarch64':
        option_name = "rknpu2"
        if (os.path.isfile("/usr/rk_bins/npu_transfer_proxy")):
            device_name = "rknpu"
        else:
            device_name = "rknpu2"
            option_name = "rknpu"
        if (not os.path.exists(sdk_solution_path + "/" + device_name)):
            print("warning: please change all infer toml to use " +
                  option_name + ", since solution not match!")
            device_name = option_name

    if device_name == "":
        print("error: current device not support " + solution_name + " exit!")
        return ""
    return sdk_solution_path + "/" + device_name


def solution_copy_common(sdk_solution_root, sdk_solution_path, cur_solution_path):
    if not os.path.isdir(sdk_solution_path + "/../common"):
        return
    if platform.system().lower() == 'windows':
        cmd_xcopy = "xcopy " + sdk_solution_path + "/../common/* " + cur_solution_path + "/ "
        os.system(cmd_xcopy.replace('/', '\\') + "/S /E /Y /Q")
    else:
        os.system("cp -rf " + sdk_solution_path +
                  "/../common/* " + cur_solution_path + "/  >/dev/null 2>&1")


def import_solution(curpath, module_name, vs_string, solution_name, workspace_path, prj_type, wk_name):
    sdk_solution_path = get_solution_arch(vs_string, solution_name, curpath)
    proj_path = curpath + "/" + wk_name + "/" + module_name
    if (sdk_solution_path == ""):
        return False
    if (not os.path.exists(sdk_solution_path)):
        print("error: solution:" + solution_name + " is not exist")
        shutil.rmtree(proj_path)
        return False
    if platform.system().lower() == 'windows':
        cmd_xcopy = "xcopy " + sdk_solution_path + "/* " + proj_path + "/ "
        cmd_del = "del " + proj_path + "/graph/" + solution_name + "* "
        os.system(cmd_xcopy.replace('/', '\\') + "/S /E /Y /Q")
        os.system(cmd_del.replace('/', '\\') + "/Q")
    else:
        os.system("cp -rf " + sdk_solution_path +
                  "/* " + proj_path + "/  >/dev/null 2>&1")
        os.system("rm -rf " + proj_path + "/graph/" +
                  solution_name + "* >/dev/null 2>&1")
    for graph_file in os.listdir(sdk_solution_path + "/graph"):
        file_ext = os.path.splitext(graph_file)[-1]
        if (file_ext != ".toml"):
            continue
        file_name = os.path.splitext(graph_file)[0]
        file_name_ext = file_name[len(solution_name):len(file_name)]
        dst_name = proj_path + "/graph/" + \
            module_name + file_name_ext + ".toml"
        sed_file(sdk_solution_path + "/graph/" + graph_file,
                 dst_name, module_name, vs_string)

    solution_copy_common(curpath + "/" + vs_string +
                         "/solution/", sdk_solution_path, proj_path)

    print("success: create " + module_name + " in " + workspace_path)
    return True


def create_project(curpath, module_name, vs_string, solution_name, prj_type, wk_name="workspace"):
    if (not is_name_valid(module_name)):
        return False, ""
    workspace_path = os.path.join(curpath, wk_name)
    sdk_path = os.path.join(curpath, vs_string)
    proj_path = os.path.join(workspace_path, module_name)
    if (os.path.exists(proj_path)):
        print(module_name + " is exist, can not crate project with the same name")
        return False, ""
    pathlib.Path(workspace_path).mkdir(parents=True, exist_ok=True)
    shutil.copytree(sdk_path+"/template/project", proj_path)
    pathlib.Path(
        proj_path + "/etc/flowunit/cpp").mkdir(parents=True, exist_ok=True)

    os_type = 'win10'
    if platform.system().lower() != 'windows':
        os_type = 'linux'

    if (solution_name == ""):
        src_path = sdk_path + "/template/project/graph/example.toml"
        dst_path = proj_path + "/graph/" + module_name + ".toml"
        sed_file(src_path, dst_path, module_name, vs_string)

    sed_file(sdk_path + "/template/project/CMakeLists.txt",
             proj_path + "/CMakeLists.txt", module_name, vs_string)
    if (module_name != "example"):
        os.remove(proj_path + "/graph/example.toml")

    pathlib.Path(proj_path + "/model").mkdir(parents=True, exist_ok=True)
    pathlib.Path(proj_path + "/data").mkdir(parents=True, exist_ok=True)
    # 创建run的脚本
    pathlib.Path(proj_path + "/bin").mkdir(parents=True, exist_ok=True)
    bin_path = ""
    if (prj_type == "server"):
        bin_path = "_server"
        sed_file(sdk_path + "/template/bin_server/modelbox_" + os_type + ".conf",
                 proj_path + "/graph/modelbox.conf", module_name, vs_string)
        sed_file(sdk_path + "/template/bin_server/mock_task.toml",
                 proj_path + "/bin/mock_task.toml", module_name, vs_string)

    sed_file(sdk_path + "/template/bin" + bin_path + "/main" + get_osext(vs_string),
             proj_path + "/bin/main" + get_osext(vs_string), module_name, vs_string)

    ret = True
    if (solution_name == ""):
        print("success: create " + module_name + " in " + workspace_path)
    else:
        ret = import_solution(curpath, module_name, vs_string,
                              solution_name, workspace_path, prj_type, wk_name)
    if (ret and os.path.exists(proj_path + "/build_project.sh")):
        os.system(proj_path + "/build_project.sh nowait")
    return ret , proj_path


def create_cplusplus(curpath, module_name, vs_string, proj_name, cfg_json):
    workspace_path, proj_path = check_path(curpath, proj_name)
    if (workspace_path == "" or proj_path == ""):
        return False, ""

    sdk_path = os.path.join(curpath, vs_string)
    cplusplus_path = proj_path + "/flowunit_cpp/" + module_name
    if (os.path.exists(cplusplus_path)):
        print("error: " + module_name +
              " is exist, can not crate c++ with the same name")
        return False, ""
    pathlib.Path(cplusplus_path).mkdir(parents=True, exist_ok=True)
    sed_file(sdk_path+"/template/flowunit/c++/CMakeLists.txt",
             cplusplus_path+"/CMakeLists.txt", module_name, vs_string)
    sed_file(sdk_path+"/template/flowunit/c++/example.cc",
             cplusplus_path+"/"+module_name+".cc", module_name, vs_string)
    sed_file(sdk_path+"/template/flowunit/c++/example.h",
             cplusplus_path+"/"+module_name+".h", module_name, vs_string)

    print("success: create c++ " + module_name + " in " + cplusplus_path)
    return True, cplusplus_path


def create_python(curpath, module_name, vs_string, proj_name, cfg_json):
    workspace_path, proj_path = check_path(curpath, proj_name)
    if (workspace_path == "" or proj_path == ""):
        return False, ""

    sdk_path = os.path.join(curpath, vs_string)
    python_path = proj_path + "/etc/flowunit/" + module_name
    if (os.path.exists(python_path)):
        print("error: " + module_name +
              " is exist, can not crate python with the same name")
        return False, ""
    pathlib.Path(python_path).mkdir(parents=True, exist_ok=True)
    src_path = sdk_path + "/template/flowunit/python/"
    sed_file(src_path+"example.py",
             python_path+"/"+module_name+".py", module_name, vs_string)
    if (cfg_json == ""):
        sed_file(src_path+"example.toml",
                 python_path+"/"+module_name+".toml", module_name, vs_string)
    else:
        retstr, cfg = add_inout_port(
            src_path+"example.toml", cfg_json, get_device(vs_string), module_name)
        if (retstr == ''):
            return False, python_path
        retstr = retstr.replace('group_type = "generic"',
                       'group_type = "' + cfg["group-type"] + '"')
        if ("type" in cfg):
            retstr = retstr.replace(cfg["type"] + " = false", cfg["type"] + " = true")
        with open(python_path+"/"+module_name+".toml", 'wb') as f:
            f.write(retstr.encode('utf-8'))

    print("success: create python " + module_name + " in " + python_path)
    return True, python_path


def create_infer(curpath, module_name, vs_string, proj_name, cfg_json):
    workspace_path, proj_path = check_path(curpath, proj_name)
    if (workspace_path == "" or proj_path == ""):
        return False, ""

    sdk_path = os.path.join(curpath, vs_string)
    infer_path = proj_path + "/model/" + module_name
    if (os.path.exists(infer_path)):
        print("error: " + module_name +
              " is exist, can not crate python with the same name")
        return False, ""
    pathlib.Path(infer_path).mkdir(parents=True, exist_ok=True)
    src_file = sdk_path+"/template/flowunit/infer/example_" + \
        get_device(vs_string) + ".toml"
    if (cfg_json == ""):
        sed_file(src_file, infer_path + "/" + module_name +
                 ".toml", module_name, vs_string)
    else:
        retstr, cfg = add_inout_port(src_file, cfg_json, get_device(vs_string), module_name)
        if (retstr == ''):
            return False, infer_path
        if (cfg["model"] != ""):
            retstr = retstr.replace('./model', './' + os.path.splitext(cfg["model"])[0])
        with open(infer_path + "/" + module_name + ".toml", 'wb') as f:
            f.write(retstr.encode('utf-8'))

    print("success: create infer " + module_name + " in " + infer_path)
    return True, infer_path


def create_yolo(curpath, module_name, vs_string, proj_name, cfg_json):
    workspace_path, proj_path = check_path(curpath, proj_name)
    if (workspace_path == "" or proj_path == ""):
        return False, ""

    sdk_path = os.path.join(curpath, vs_string)
    yolo_path = proj_path + "/etc/flowunit/" + module_name
    if (os.path.exists(yolo_path)):
        print("error: " + module_name +
              " is exist, can not crate yolo with the same name")
        return False, ""
    pathlib.Path(yolo_path).mkdir(parents=True, exist_ok=True)
    src_file = sdk_path+"/template/flowunit/yolo/example.toml"
    if (cfg_json == ""):
        sed_file(src_file, yolo_path+"/"+module_name +
                 ".toml", module_name, vs_string)
    else:
        retstr, cfg = add_inout_port(src_file, cfg_json, get_device(vs_string), module_name)
        if (retstr == ''):
            return False, yolo_path
        if ("virtual-type" in cfg):
            retstr = retstr.replace('yolov3_postprocess', cfg["virtual-type"])
        with open(yolo_path+"/"+module_name+".toml", 'wb') as f:
            f.write(retstr.encode('utf-8'))

    print("success: create yolo " + module_name + " in " + yolo_path)
    return True, yolo_path


def create_rpm(proj_path, module_name, vs_string):
    if (not os.path.exists(proj_path)):
        print("error: no " + module_name)
        return
    if (not os.path.exists(proj_path + "/hilens_data_dir")):
        print("error: please firstly call your_prj/build_project.sh")
        return

    try:
        shutil.rmtree(proj_path + "/rpm")
    except:
        pass

    if (os.path.exists(proj_path + "/rpm")):
        print("error: rpm folder in project path delete fail!")
        return
    pathlib.Path(proj_path + "/rpm").mkdir(parents=True, exist_ok=True)
    shutil.copytree(proj_path+"/bin", proj_path + "/rpm/bin", symlinks=True)
    try:
        os.remove(proj_path + "/rpm/bin/modelbox-driver-info")
    except:
        pass
    shutil.copytree(proj_path+"/etc", proj_path + "/rpm/etc", symlinks=True)
    shutil.copytree(proj_path+"/graph", proj_path +
                    "/rpm/graph", symlinks=True)
    shutil.copytree(proj_path+"/dependence", proj_path +
                    "/rpm/dependence", symlinks=True)
    if (os.path.exists(proj_path + "/model")):
        shutil.copytree(proj_path+"/model", proj_path +
                        "/rpm/model", symlinks=True)
    if (os.path.exists(proj_path + "/data")):
        shutil.copytree(proj_path+"/data", proj_path +
                        "/rpm/data", symlinks=True)
    pathlib.Path(proj_path + "/rpm/sdk_" +
                 vs_string).mkdir(parents=True, exist_ok=True)

    # 只打包有用的sdk部分，且当前sdk路径不一致，打包的是放在工程里面， 编译运行的时候sdk是在工程外面，需要改改路径
    cmd = proj_path + "/../../mb-pkg-tool pack  "
    if(get_osext(vs_string) == ".bat"):
        copy_sdk_win(proj_path+"/../../" + vs_string,
                     proj_path + "/rpm/sdk_" + vs_string)
    else:
        copy_sdk_linux(proj_path+"/../../" + vs_string,
                       proj_path + "/rpm/sdk_" + vs_string)

    if (os.path.exists(proj_path + "rpm_copyothers.sh")):
        os.system(proj_path + "rpm_copyothers.sh")
    print(
        "call mb-pkg-tool pack [folder] > [rpm file] to building rpm, waiting...")
    os.system(cmd + proj_path + "/rpm > ./workspace/" +
              module_name + "/" + module_name + ".rpm")

    if (os.path.isfile(proj_path+"/"+module_name + ".rpm")):
        print("success: create " + module_name + ".rpm in " + proj_path)
    else:
        print("error: create error")


def create_editor(curpath, module_name, vs_string, editor_ip):
    sdk_path = os.path.join(curpath, vs_string)

    cmd = curpath + "/editor/run_editor" + get_osext(vs_string)
    os_type = 'win10'
    if platform.system().lower() != 'windows':
        cmd = "sh " + cmd
        os_type = 'linux'

    if (editor_ip.find(":") < 0):
        editor_ip += ":1104"

    # editor目录不存在，创建editor，拷贝模板里面的文件
    pathlib.Path(
        curpath + "/editor/task/log").mkdir(parents=True, exist_ok=True)
    sed_file(sdk_path + "/template/editor/run_editor" + get_osext(vs_string), curpath +
             "/editor/run_editor" + get_osext(vs_string), module_name, vs_string)
    sed_file(sdk_path + "/template/editor/editor_config_" + os_type + ".conf", curpath +
             "/editor/editor_config_" + os_type + ".conf", module_name, vs_string, editor_ip)

    print("open http://" + editor_ip + "/editor")
    # start http-server
    try:
        os.system(cmd)
    except:
        pass


def sed_demos(demo_path):
    for graph_file in os.listdir(demo_path + "/graph"):
        lines = []
        with open(demo_path + "/graph/" + graph_file, 'r') as f:
            lines = f.readlines()
        with open(demo_path + "/graph/" + graph_file, 'wb') as f:
            for line in lines:
                line = line.replace('\r', '')
                line = line.replace("${HILENS_APP_ROOT}", demo_path)
                line = line.replace('\\', '/')
                f.write(line.encode('utf-8'))


def create_demos(curpath, solution_name, vs_string):
    solution_dir = curpath + "/" + vs_string + "/solution"
    for sn in os.listdir(solution_dir):
        if (sn != solution_name and solution_name != ""):
            continue
        create_project(curpath, sn, vs_string,
                       sn, "server", "demo")
        sed_demos(curpath + "/demo/" + sn)


def print_usage():
    print(
        """
Usage: Create ModelBox project and flowunit

NOTE : you must firstly use bellow cmd to create a project in workspace
    create.py -t server -n your_proj_name {option: -s name, create this project from a solution}, support hilens deployment
 or create.py -t project -n your_proj_name {option: -s name, create this project from a solution}, generally not use
AND  : use bellow cmd to create  [c++|python|infer]  flowunit in this project
    create.py -t c++ -n your_flowunit_name -p your_proj_name
AND  : call workspace/your_proj_name/build_project.sh to build your project, call bin/main.sh[bat] to run
FINAL: create.py -t rpm -n your_proj_name to package your project (the same folder with create.py) if upload to hilens

NOTE: create.py -t editor {option: -i ip or ip:port to start editor server in your config ip:port}
NOTE: create.py -t demo to create solutions to runnable demo

for ex: create.py -t server -n my_det -s car_det

-h or --help：show help
-t or --template [c++|python|infer|yolo|project|server|rpm|editor|demo]  create a template or package to rpm ...
-n or --name [your template name]
-p or --project  [your project name when create c++|python|infer|yolo]
-s or --solution [the solution name when create project] create a project from solution
-c or --cfg [flowunit configure json, it's used by UI, you can use it too, but too complicated]
-v or --version：show sdk version
"""
    )


def run_cmd():
    try:
        process = subprocess.Popen(
            'cmd.exe /K python ' + os.path.split(os.path.realpath(__file__))[0] + '\create.py -h')
    except Exception as e:
        print(e)
        os.system('pause')
        return


def get_version(curpath):
    vs_count = 0
    vs_string = ""

    for filename in os.listdir(curpath):
        file_path = os.path.join(curpath, filename)
        if (os.path.isdir(file_path) and filename.startswith("modelbox")):
            vs_string = filename
            vs_count = vs_count + 1

    if (vs_count == 1):
        ver_num = "1.0.0"
        try:
            with open(curpath + "/" + vs_string + "/version") as f:
                ver_num = f.readline().rstrip()
        except:
            pass
        print("sdk version is " + vs_string + "-" + ver_num)
    elif (vs_count == 0):
        print("err: there is no sdk")
    else:
        vs_string = ""
        print("err: too many sdk, please just leave one sdk (folder with modelbox*) here")
    return vs_string


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hvt:n:p:s:i:c:", [
            "help", "version", "template=", "name=", "project=", "solution=", "ip=", "cfg="])
    except getopt.GetoptError as e:
        print(e)
        print("argv error,please input as:")
        print_usage()
        return

    # 以下部分即根据分析出的结果做相应的处理，并将处理结果返回给用户
    curpath = os.path.split(os.path.realpath(__file__))[0]
    template_type = ""
    module_name = ""
    proj_name = ""
    solution_name = ""
    editor_ip = "127.0.0.1"
    cfg_json = ""
    if platform.system().lower() == 'linux':
        editor_ip = "192.168.2.111"
    for cmd, arg in opts:
        if cmd in ("-h", "--help"):
            print_usage()
            return
        elif cmd in ("-v", "--version"):
            get_version(curpath)
            return
        elif cmd in ("-t", "--template"):
            template_type = arg
        elif cmd in ("-n", "--name"):
            module_name = arg
        elif cmd in ("-p", "--project"):
            proj_name = arg
        elif cmd in ("-s", "--solution"):
            solution_name = arg
        elif cmd in ("-i", "--ip"):
            editor_ip = arg
        elif cmd in ("-c", "--cfg"):
            cfg_json = arg

    vs_string = get_version(curpath)
    if (vs_string == ""):
        return

    if (template_type == "demo" or template_type == "editor"):
        module_name = "all"

    if (template_type == "" or module_name == ""):
        print("create.py -t *** -n ***, *** can not be null")
        return

    ret = True
    mdpath = ""
    if (template_type == "project" or template_type == "server"):
        ret, mdpath = create_project(curpath, module_name, vs_string,
                             solution_name, template_type)
    elif (template_type == "c++"):
        ret, mdpath = create_cplusplus(curpath, module_name,
                               vs_string, proj_name, cfg_json)
    elif (template_type == "python"):
        ret, mdpath = create_python(curpath, module_name,
                            vs_string, proj_name, cfg_json)
    elif (template_type == "infer"):
        ret, mdpath = create_infer(curpath, module_name,
                           vs_string, proj_name, cfg_json)
    elif (template_type == "yolo"):
        ret, mdpath = create_yolo(curpath, module_name, vs_string, proj_name, cfg_json)
    elif (template_type == "rpm"):
        create_rpm(curpath + "/workspace/" +
                   module_name, module_name, vs_string)
    elif (template_type == "editor"):
        create_editor(curpath, module_name, vs_string, editor_ip)
    elif (template_type == "demo"):
        create_demos(curpath, solution_name, vs_string)
    else:
        print(
            "error: support [c++|python|infer|yolo|project|server|rpm|editor|demo] with -t or --template")
    if (ret == False and mdpath != "" and os.path.exists(mdpath)):
        shutil.rmtree(mdpath)


def run_main():
    if len(sys.argv) == 1:
        if platform.system().lower() == 'windows':
            run_cmd()
        else:
            print_usage()
        return

    if platform.system().lower() == 'linux':
        output = subprocess.Popen(
            ['id -u HwHiLensDriverUser'], stdout=subprocess.PIPE, shell=True, stderr=subprocess.DEVNULL,
            bufsize=-1).communicate()
        if not "HwHiLensDriverUser" in output:
            output = subprocess.Popen(
                ['id'], stdout=subprocess.PIPE, shell=True).communicate()
            output_str = output[0].decode('utf-8')
            if not "HwHiLensDriverUser" in output_str and not "uid=0" in output_str:
                current_user = output_str.split(')')[0].split('(')[-1]
                print(current_user +
                      " not in HwHiLensDriverUser group, enter root passwd to add")
                os.system("sudo usermod -a -G HwHiLensDriverUser " + current_user)
    main()


if __name__ == "__main__":
    run_main()
