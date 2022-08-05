/*
 * Copyright (c) Huawei Technologies Co., Ltd. 2022. All rights reserved.
 */

#ifndef MODELBOX_FLOWUNIT_MODULENAME_CPU_H_
#define MODELBOX_FLOWUNIT_MODULENAME_CPU_H_

#include <modelbox/base/device.h>
#include <modelbox/flow.h>
#include <modelbox/flowunit.h>

constexpr const char *FLOWUNIT_NAME = "MODULENAME";
constexpr const char *FLOWUNIT_TYPE = "cpu";
constexpr const char *FLOWUNIT_DESC =
    "\n\t@Brief: A MODULENAME flowunit on cpu \n"
    "\t@Port parameter: "
    "\t@Constraint: ";

class MODULENAMEFlowUnit : public modelbox::FlowUnit {
 public:
  MODULENAMEFlowUnit();
  virtual ~MODULENAMEFlowUnit();

  modelbox::Status Open(const std::shared_ptr<modelbox::Configuration> &opts);
  modelbox::Status Close();
  modelbox::Status DataPre(std::shared_ptr<modelbox::DataContext> ct);
  modelbox::Status Process(std::shared_ptr<modelbox::DataContext> ct);
  modelbox::Status DataPost(std::shared_ptr<modelbox::DataContext> ct);
  modelbox::Status DataGroupPre(std::shared_ptr<modelbox::DataContext> ct);
  modelbox::Status DataGroupPost(std::shared_ptr<modelbox::DataContext> ct);
};

#endif  // MODELBOX_FLOWUNIT_MODULENAME_CPU_H_
