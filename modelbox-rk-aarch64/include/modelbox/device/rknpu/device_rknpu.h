/*
 * Copyright (C) 2022 Huawei Technologies Co., Ltd. All rights reserved.
 */

#ifndef MODELBOX_DEVICE_RKNPU_H_
#define MODELBOX_DEVICE_RKNPU_H_

#include <modelbox/base/device.h>
#include <modelbox/data_context.h>
#include <modelbox/device/rknpu/rknpu_memory.h>
#include <modelbox/flow.h>

namespace modelbox {
typedef void MppBufHdl;

constexpr const char *DEVICE_TYPE = "rknpu";
constexpr const char *DEVICE_DRIVER_NAME = "device-rknpu";
constexpr const char *DEVICE_DRIVER_DESCRIPTION = "A rknpu device driver";

class RKNPU : public Device {
 public:
  RKNPU(const std::shared_ptr<DeviceMemoryManager> &mem_mgr);
  virtual ~RKNPU();
  const std::string GetType() const override;

  Status DeviceExecute(DevExecuteCallBack rkfun, int32_t priority,
                       size_t rkcount) override;
  bool NeedResourceNice() override;
};

class RKNPUFactory : public DeviceFactory {
 public:
  RKNPUFactory();
  virtual ~RKNPUFactory();

  std::map<std::string, std::shared_ptr<DeviceDesc>> DeviceProbe();
  const std::string GetDeviceFactoryType();
  std::shared_ptr<Device> CreateDevice(const std::string &device_id);

 private:
  std::map<std::string, std::shared_ptr<DeviceDesc>> ProbeRKNNDevice();
};

class RKNPUDesc : public DeviceDesc {
 public:
  RKNPUDesc() = default;
  virtual ~RKNPUDesc() = default;
};

// use it to store the rknn device names
class RKNNDevs {
public:
    static RKNNDevs &Instance()
    {
        static RKNNDevs rk_nndevs;
        return rk_nndevs;
    }

    void SetNames(std::vector<std::string> &dev_names);
    const std::vector<std::string>& GetNames();

private:
    RKNNDevs() = default;
    ~RKNNDevs() = default;
    RKNNDevs(const RKNNDevs &) = delete;
    RKNNDevs &operator = (const RKNNDevs &) = delete;
    
    std::vector<std::string> dev_names_;
};

}  // namespace modelbox

#endif  // MODELBOX_DEVICE_RKNPU_H_