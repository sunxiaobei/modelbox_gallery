# Copyright (C) 2020 Huawei Technologies Co., Ltd. All rights reserved.

cmake_minimum_required(VERSION 3.10)

project(unit)

if(${CMAKE_SOURCE_DIR} STREQUAL ${CMAKE_BINARY_DIR})
    message(FATAL_ERROR "cannot build the project in the source directory! Out-of-source build is enforced!")
endif()

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

set(MODELBOX_PROJECT_VERSION_MAJOR 1)
set(MODELBOX_PROJECT_VERSION_MINOR 0)
set(MODELBOX_PROJECT_VERSION_PATCH 0)

set(CMAKE_PROJECT_VERSION ${MODELBOX_PROJECT_VERSION_MAJOR})
set(CMAKE_PROJECT_VERSION_MAJOR ${MODELBOX_PROJECT_VERSION_MAJOR})
set(CMAKE_PROJECT_VERSION_MINOR ${MODELBOX_PROJECT_VERSION_MINOR})
set(CMAKE_PROJECT_VERSION_PATCH ${MODELBOX_PROJECT_VERSION_PATCH})
set(CMAKE_PROJECT_VERSION_STRING "${CMAKE_PROJECT_VERSION_MAJOR}.${CMAKE_PROJECT_VERSION_MINOR}.${CMAKE_PROJECT_VERSION_PATCH}")
add_definitions(-DPROJECT_VERSION_STR_MACRO="${CMAKE_PROJECT_VERSION_STRING}")

set(CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/CMake" ${CMAKE_MODULE_PATH})

include(Function)
include(FindPkgConfig)
include(CMakeDependentOption)

if (WIN32)
  set(Boost_ARCHITECTURE  -x64)
  add_definitions(-D_CRT_SECURE_NO_WARNINGS)
  add_definitions(-DESHUTDOWN=108)
  add_definitions(-DRTLD_NODELETE=0x01000)
  add_definitions(-Dlstat=stat)
  add_definitions(-DSC_OS_WINDOW)
  add_definitions(-DOBS_EXPORTS)
  add_definitions(-DCPPREST_FORCE_HTTP_CLIENT_ASIO)
  add_definitions(-Dtimegm=_mkgmtime)
  #编译器找不到klogger
  add_definitions(-DMBLOG_LIBRARY_DEEPBIND)
  # miniinclude for windows.h (memset_s, X509_NAME)
  add_definitions(-DWIN32_LEAN_AND_MEAN)
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wno-ignored-attributes -Wno-attributes -Wno-cast-qual -Wno-unused-function -Wno-deprecated-declarations")
  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wno-ignored-attributes -Wno-attributes -Wno-cast-qual -Wno-unused-function -Wno-deprecated-declarations")
endif()

set(RELEASE_FLOWUNIT_DIR ${CMAKE_CURRENT_LIST_DIR}/etc/flowunit/cpp)
set(OpenCV_DIR ${CMAKE_CURRENT_LIST_DIR}/../../modelbox-rk-aarch64/lib/opencv)

include_directories(${CMAKE_CURRENT_LIST_DIR}/../../modelbox-rk-aarch64/include)
link_directories(${CMAKE_CURRENT_LIST_DIR}/../../modelbox-rk-aarch64/lib)

find_package(OpenCV)
find_package(FFMPEG)

add_subdirectory(flowunit_cpp)
