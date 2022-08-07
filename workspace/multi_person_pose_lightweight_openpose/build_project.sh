#!/bin/bash
# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

CUR_PATH=$(cd $(dirname $0);pwd)
BASE_PATH=${CUR_PATH}/../..
SDK_PATH=""

# change to Debug if you want
OUR_BUILD_TYPE=Release

# windows or linux
unamestr=`uname`
gitbash=`echo ${unamestr} | grep MINGW64_NT`

toml2unix()
{
  if [ ! -d $1 ];then
    return
  fi

  for file in $(ls $1)
  do
    if [ -d $1"/"$file ];then
      toml2unix $1"/"$file
    elif [ "${file##*.}"x = "toml"x -o "${file##*.}"x = "conf"x ];then
      dos2unix $1"/"$file
    fi
  done
}

get_sdk_path()
{
  sdk_count=0
  for dir in $(ls ${BASE_PATH})
  do
    if [ -d ${BASE_PATH}"/"$dir ];then
      if [[ $dir = modelbox* ]];then
        SDK_PATH=${BASE_PATH}"/"$dir
        let sdk_count++
      fi
  fi
  done

  if [ ${sdk_count} -ne 1 ];then
    echo "err, find ${sdk_count} sdk, exit"
	  read -p "press Enter to continue..."
    exit 1
  fi
}
get_sdk_path

# do c++ build if have c++ flowunit
cplusplus_build()
{
  need_build=0
  for file in $(ls ${CUR_PATH}/flowunit_cpp)
  do
    if [ -d ${CUR_PATH}/flowunit_cpp/$file ];then
      need_build=1
      break
    fi
  done
  if [ "${need_build}" = "0" ];then
    return
  fi

  export CMAKE_INCLUDE_PATH=${SDK_PATH}/include
  export CMAKE_LIBRARY_PATH=${SDK_PATH}/lib

  mkdir -p ${CUR_PATH}/build
  cd ${CUR_PATH}/build

  if [ ! -z ${gitbash} ]; then
    cmake  -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=${OUR_BUILD_TYPE} ..
  else
    cmake  -DCMAKE_BUILD_TYPE=${OUR_BUILD_TYPE} ..
  fi
  cmake --build . --target install --config ${OUR_BUILD_TYPE} -j 4
}
cplusplus_build

# avoid windows format toml file, it makes toml error
toml2unix ${CUR_PATH}/graph
toml2unix ${CUR_PATH}/etc
toml2unix ${CUR_PATH}/model
toml2unix ${CUR_PATH}/run/editor
toml2unix ${CUR_PATH}/bin

# create run
mkdir -p ${CUR_PATH}/hilens_data_dir
if [ ! -z ${gitbash} ]; then
  REAL_PATH=`cygpath -m -d ${CUR_PATH}`
  MAIN_EXT=".bat"
else
  REAL_PATH=${CUR_PATH}
  MAIN_EXT=".sh"
  chmod +x ${CUR_PATH}/bin/main${MAIN_EXT}
  chmod +x ${CUR_PATH}/rpm_copyothers.sh
fi

echo -e "\nbuild success: you can run main"${MAIN_EXT}" in ./bin folder\n";

# wait 5s , it not p press, auto exit
if [ ! -z ${gitbash} ] && [ "$1" != "nowait" ]; then
  KEY_VALUE=""
  echo -e "Press 'p' to pause..., any key to exit\n";
  read -rs -t5 -n1 KEY_VALUE
  if [ "${KEY_VALUE}" = "p" -o "${KEY_VALUE}" = "P" ];then
    read -p "Press any key to exit"
  fi
fi