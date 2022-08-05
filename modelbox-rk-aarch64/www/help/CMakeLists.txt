# Copyright (C) 2020 Huawei Technologies Co., Ltd. All rights reserved.

cmake_minimum_required(VERSION 2.8.1)

project(modelbox-book)

find_program(NPM npm)

if(NOT NPM)
    message("Skip build modelbox-book")
    return()
endif()

set(NODE_MODULES_PATH ${CMAKE_CURRENT_BINARY_DIR})

if (NOT BOOK_OUTPUT_DIR)
    set(BOOK_OUTPUT_DIR ${CMAKE_CURRENT_BINARY_DIR}/help)
endif()

if (NOT BOOK_INSTALL_DIR)
    set(BOOK_INSTALL_DIR "/usr/local/share/modelbox/www")
endif()

set(BOOK_INSTALL_FLAG ${CMAKE_CURRENT_LIST_DIR}/node_modules/bookinstalled)
set(GITBOOK ${CMAKE_CURRENT_LIST_DIR}/node_modules/.bin/gitbook)

add_custom_target(modelbox-book ALL)
add_custom_command(TARGET modelbox-book 
    COMMENT "Building modelbox book package.."
    WORKING_DIRECTORY ${CMAKE_CURRENT_LIST_DIR}
    COMMAND [ ! -e ${NODE_MODULES_PATH}/node_modules ] || mv ${NODE_MODULES_PATH}/node_modules ${CMAKE_CURRENT_LIST_DIR}/node_modules 
    COMMAND [ -e ${BOOK_INSTALL_FLAG} ] || ${NPM} install gitbook-cli 
    # patch graceful-fs
    COMMAND [ -e ${BOOK_INSTALL_FLAG} ] || sed -i "'/stat = statFix/d'"  ${CMAKE_CURRENT_LIST_DIR}/node_modules/npm/node_modules/graceful-fs/polyfills.js
    COMMAND [ -e ${BOOK_INSTALL_FLAG} ] || ${GITBOOK} install ${CMAKE_CURRENT_LIST_DIR} 
    COMMAND touch ${BOOK_INSTALL_FLAG}
    COMMAND ${GITBOOK} build ${CMAKE_CURRENT_LIST_DIR} ${BOOK_OUTPUT_DIR}
    COMMAND rm -f ${BOOK_OUTPUT_DIR}/assets/*.vsdx
    COMMAND rm -f ${CMAKE_CURRENT_LIST_DIR}/package-lock.json
    COMMAND 
    BYPRODUCTS ${BOOK_INSTALL_FLAG} ${BOOK_OUTPUT_DIR}
    )

install(DIRECTORY 
    ${BOOK_OUTPUT_DIR}
    DESTINATION ${BOOK_INSTALL_DIR}
    COMPONENT document
    )
