/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */

#include "MODULENAME.h"
#include "modelbox/flowunit_api_helper.h"

MODULENAMEFlowUnit::MODULENAMEFlowUnit(){};
MODULENAMEFlowUnit::~MODULENAMEFlowUnit(){};

modelbox::Status MODULENAMEFlowUnit::Open(
    const std::shared_ptr<modelbox::Configuration> &opts) {
  return modelbox::STATUS_OK;
}

modelbox::Status MODULENAMEFlowUnit::Close() { return modelbox::STATUS_OK; }

modelbox::Status MODULENAMEFlowUnit::DataPre(
    std::shared_ptr<modelbox::DataContext> ctx) {
  return modelbox::STATUS_OK;
}

modelbox::Status MODULENAMEFlowUnit::Process(
    std::shared_ptr<modelbox::DataContext> ctx) {
  return modelbox::STATUS_OK;
}

modelbox::Status MODULENAMEFlowUnit::DataPost(
    std::shared_ptr<modelbox::DataContext> ctx) {
  return modelbox::STATUS_OK;
}

modelbox::Status MODULENAMEFlowUnit::DataGroupPre(
    std::shared_ptr<modelbox::DataContext> data_ctx) {
  return modelbox::STATUS_OK;
}

modelbox::Status MODULENAMEFlowUnit::DataGroupPost(
    std::shared_ptr<modelbox::DataContext> data_ctx) {
  return modelbox::STATUS_OK;
}

MODELBOX_FLOWUNIT(MODULENAMEFlowUnit, desc) {
  /*set flowunit attributes*/
  desc.SetFlowUnitName(FLOWUNIT_NAME);
  desc.SetFlowUnitGroupType("GroupTypeName");
  desc.AddFlowUnitInput(modelbox::FlowUnitInput("in_1", FLOWUNIT_TYPE));
  desc.AddFlowUnitOutput(modelbox::FlowUnitOutput("out_1"));
  desc.SetFlowType(modelbox::NORMAL);
  desc.SetDescription(FLOWUNIT_DESC);
  /*set flowunit parameter */
  desc.AddFlowUnitOption(modelbox::FlowUnitOption(
      "parameter0", "int", true, "640", "parameter0 describe detail"));
  desc.AddFlowUnitOption(modelbox::FlowUnitOption(
      "parameter1", "int", true, "480", "parameter1 describe detail"));
}

MODELBOX_DRIVER_FLOWUNIT(desc) {
  desc.Desc.SetName(FLOWUNIT_NAME);
  desc.Desc.SetClass(modelbox::DRIVER_CLASS_FLOWUNIT);
  desc.Desc.SetType(FLOWUNIT_TYPE);
  desc.Desc.SetDescription(FLOWUNIT_DESC);
  desc.Desc.SetVersion(PROJECT_VERSION_STR_MACRO);
}
