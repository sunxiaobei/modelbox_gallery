# Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.

cmake_minimum_required(VERSION 3.10)
 
set(UNIT_NAME "MODULENAME")
set(UNIT_DEVICE "cpu")

if(NOT DEFINED MODELBOX_PROJECT_VERSION_MAJOR)
    # build from flowunit cmakelists, not from project cmakelists
    set(MODELBOX_PROJECT_VERSION_MAJOR 1)
    set(MODELBOX_PROJECT_VERSION_MINOR 0)
    set(MODELBOX_PROJECT_VERSION_PATCH 0)
endif()

set(RELEASE_PACKAGE_DIR_BIN ${CMAKE_CURRENT_LIST_DIR}/../bin) 

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -fno-strict-aliasing")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -Wall -fno-strict-aliasing")
if (NOT WIN32)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -DBASE_FILE_NAME='\"$(notdir $<)\"'")
set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -DBASE_FILE_NAME='\"$(notdir $<)\"'")
endif()

file(GLOB_RECURSE UNIT_SOURCE *.cpp *.cc *.c)
 
include_directories(${CMAKE_CURRENT_LIST_DIR})
include_directories(${CMAKE_CURRENT_LIST_DIR}/../../../../SDKNAME/include)

link_directories(${CMAKE_CURRENT_LIST_DIR}/../../../../SDKNAME/lib)

set(UNIT_SHARED modelbox-${CMAKE_PROJECT_NAME}-${UNIT_DEVICE}-${UNIT_NAME})
add_library(${UNIT_SHARED} SHARED ${UNIT_SOURCE})
 
set_target_properties(
  ${UNIT_SHARED} PROPERTIES
  SOVERSION ${MODELBOX_PROJECT_VERSION_MAJOR}
  VERSION ${MODELBOX_PROJECT_VERSION_MAJOR}.${MODELBOX_PROJECT_VERSION_MINOR}.${MODELBOX_PROJECT_VERSION_PATCH}
)

target_link_libraries(${UNIT_SHARED} pthread)
target_link_libraries(${UNIT_SHARED} rt)
target_link_libraries(${UNIT_SHARED} dl)
target_link_libraries(${UNIT_SHARED} modelbox)
target_link_libraries(${UNIT_SHARED} modelbox-device-${UNIT_DEVICE})

if (WIN32)
  install(TARGETS ${UNIT_SHARED} 
      COMPONENT my_flowuint
      RUNTIME DESTINATION ${RELEASE_FLOWUNIT_DIR}
      OPTIONAL
      )
else ()
  install(TARGETS ${UNIT_SHARED} 
      COMPONENT my_flowuint
      LIBRARY DESTINATION ${RELEASE_FLOWUNIT_DIR}
      OPTIONAL
      )
endif()
