/*
 * Copyright (C) 2022 Huawei Technologies Co., Ltd. All rights reserved.
 */

#ifndef MODELBOX_RKNPU_API_H_
#define MODELBOX_RKNPU_API_H_

#include <modelbox/base/status.h>
#include <modelbox/buffer.h>
#include "im2d.h"
#include "rga.h"
#include "rk_mpi.h"
#include "rk_type.h"

#define MPPFRAMETORGA(frame, fmt)                               \
  wrapbuffer_fd(mpp_buffer_get_fd(mpp_frame_get_buffer(frame)), \
                (int)mpp_frame_get_width(frame),                \
                (int)mpp_frame_get_height(frame), fmt,          \
                (int)mpp_frame_get_hor_stride(frame),           \
                (int)mpp_frame_get_ver_stride(frame));

#define MPP_ALIGN(x, a) (((x) + (a)-1) & ~((a)-1))
#define MPP_ALIGN_MPP_WH 16
#define MPP_ALIGN_WIDTH 16
#define MPP_ALIGN_HEIGHT 2
#define RK_POLL_TIMEOUT 500

#define CHECK_MPP_RET(call_func, msg, return_ret) \
  do {                                            \
    int32_t ret = call_func;                      \
    if (ret != MPP_OK) {                          \
      MBLOG_ERROR << msg << ret;                  \
      return return_ret;                          \
    }                                             \
  } while (0)

#define CHECK_RKNN_RET(call_func, msg, return_ret) \
  do {                                             \
    int32_t ret = call_func;                       \
    if (ret != RKNN_SUCC) {                        \
      MBLOG_ERROR << msg << ret;                   \
      return return_ret;                           \
    }                                              \
  } while (0)

namespace modelbox {
constexpr const char *IMG_DEFAULT_FMT = "bgr";

std::shared_ptr<modelbox::Buffer> CreateEmptyMppImg(
    int w, int h, RgaSURF_FORMAT fmt, const std::shared_ptr<Device> &dev,
    rga_buffer_t &rga_buf);

RgaSURF_FORMAT GetRGAFormat(const std::string fmt_str);

Status CopyRGBMemory(uint8_t *psrc, uint8_t *pdst, int w, int h, int ws,
                     int hs);
Status CopyNVMemory(uint8_t *psrc, uint8_t *pdst, int w, int h, int ws, int hs);

Status GetRGAFromImgBuffer(std::shared_ptr<Buffer> &in_img, RgaSURF_FORMAT fmt,
                           rga_buffer_t &rgb_buf);

std::shared_ptr<modelbox::Buffer> ColorChange(MppFrame &frame, RgaSURF_FORMAT fmt,
                                              std::shared_ptr<Device> device);
std::shared_ptr<modelbox::Buffer> MirrorImg(std::shared_ptr<modelbox::Buffer> in_buf, 
                                            RgaSURF_FORMAT fmt);

class MppJpegDec {
 public:
  MppJpegDec();
  virtual ~MppJpegDec();
  Status Init();
  Status SendBuf(MppBuffer &in_buf, int &w, int &h);
  Status SendBuf(void *in_buf, int buf_len, int &w, int &h);
  Status ReceiveFrame(MppFrame &out_frame);

 private:
  void GetJpegWH(int &nW, int &nH, unsigned char *buf, int bufLen);
  Status DecPkt(MppPacket &packet, int w = 0, int h = 0);
  Status ShutDown();

  MppCtx codec_ctx_{nullptr};
  MppApi *rk_api_{nullptr};
  MppBufferGroup frm_grp_{nullptr};
};

class InferenceRKNPUParams {
  public:
   InferenceRKNPUParams(){};
   virtual ~InferenceRKNPUParams(){};

   std::vector<std::string> input_name_list_, output_name_list_;
   std::vector<std::string> input_type_list_, output_type_list_;

   int32_t device_id_{0};
};

class InferenceInputParams {
  public:
   InferenceInputParams(){};
   virtual ~InferenceInputParams(){};

   int32_t in_width_ = 0;
   int32_t in_height_ = 0;
   int32_t in_wstride_ = 0;
   int32_t in_hstride_ = 0;
   std::string pix_fmt_;
};

}  // namespace modelbox

#endif  // MODELBOX_RKNPU_API_H_