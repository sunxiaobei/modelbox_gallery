import numpy as np
import cv2


class YOLO7:
    def __init__(self, conf_threshold, iou_threshold, anchors, masks, strides):
        self.conf_threshold = conf_threshold
        self.iou_threshold = iou_threshold
        self.anchors = anchors
        self.masks = masks
        self.strides = strides

    @staticmethod
    def sigmoid(x):
        return 1 / (1 + np.exp(-x))

    @staticmethod
    def make_grid(nx=20, ny=20):
        xv, yv = np.meshgrid(np.arange(ny), np.arange(nx))
        return np.stack((xv, yv), 2).reshape((ny, nx, -1, 2)).astype(np.float32)

    def process(self, inputs, mask, anchors, stride):
        anchors = [anchors[i] for i in mask]
        ny, nx = map(int, inputs.shape[0:2])
        grid = self.make_grid(nx, ny)
        inputs = self.sigmoid(inputs)

        box_confidence = inputs[..., 4]
        box_confidence = np.expand_dims(box_confidence, axis=-1)

        box_class_probs = inputs[..., 5:]

        box_xy = (inputs[..., :2] * 2. - 0.5 + grid) * stride
        box_wh = (inputs[..., 2:4] * 2) ** 2 * anchors

        box = np.concatenate((box_xy, box_wh), axis=-1)

        return box, box_confidence, box_class_probs

    def filter_boxes(self, boxes, box_confidences, box_class_probs):
        box_scores = box_confidences * box_class_probs
        box_classes = np.argmax(box_scores, axis=-1)
        box_class_scores = np.max(box_scores, axis=-1)
        pos = np.where(box_class_scores >= self.conf_threshold)

        boxes = boxes[pos]
        classes = box_classes[pos]
        scores = box_class_scores[pos]

        return boxes, classes, scores

    def nms_boxes(self, boxes, scores):
        x = boxes[:, 0]
        y = boxes[:, 1]
        w = boxes[:, 2]
        h = boxes[:, 3]

        areas = w * h
        order = scores.argsort()[::-1]

        keep = []
        while order.size > 0:
            i = order[0]
            keep.append(i)

            xx1 = np.maximum(x[i], x[order[1:]])
            yy1 = np.maximum(y[i], y[order[1:]])
            xx2 = np.minimum(x[i] + w[i], x[order[1:]] + w[order[1:]])
            yy2 = np.minimum(y[i] + h[i], y[order[1:]] + h[order[1:]])

            w1 = np.maximum(0.0, xx2 - xx1)
            h1 = np.maximum(0.0, yy2 - yy1)
            inter = w1 * h1

            ovr = inter / (areas[i] + areas[order[1:]] - inter)
            inds = np.where(ovr <= self.iou_threshold)[0]
            order = order[inds + 1]
        keep = np.array(keep)
        return keep

    def yolov7_post_process(self, input_data):

        boxes, classes, scores = [], [], []
        for input, mask, stride in zip(input_data, self.masks, self.strides):
            b, c, s = self.process(input, mask, self.anchors, stride)
            b, c, s = self.filter_boxes(b, c, s)
            boxes.append(b)
            classes.append(c)
            scores.append(s)

        boxes = np.concatenate(boxes)
        classes = np.concatenate(classes)
        scores = np.concatenate(scores)

        nboxes, nclasses, nscores = [], [], []
        for c in set(classes):
            inds = np.where(classes == c)
            b = boxes[inds]
            c = classes[inds]
            s = scores[inds]

            keep = self.nms_boxes(b, s)

            nboxes.append(b[keep])
            nclasses.append(c[keep])
            nscores.append(s[keep])

        if not nclasses and not nscores:
            return [], [], []

        boxes = np.concatenate(nboxes)
        classes = np.concatenate(nclasses)
        scores = np.concatenate(nscores)

        return boxes, classes, scores


def draw(image, boxes, scores, classes, labels, buffer_meta):
    r, dw, dh = buffer_meta["ratio"], buffer_meta["dw"], buffer_meta["dh"]
    for box, score, cl in zip(boxes, scores, classes):
        x, y, w, h = box
        x = (x - dw) / r
        y = (y - dh) / r
        w = w / r
        h = h / r

        top = max(0, (x - w / 2).astype(int))
        left = max(0, (y - h / 2).astype(int))
        right = min(image.shape[1], (x + w / 2).astype(int))
        bottom = min(image.shape[0], (y + h / 2).astype(int))

        cv2.rectangle(image, (top, left), (right, bottom), (255, 0, 0), 2)
        cv2.putText(image, '{0} {1:.2f}'.format(labels[cl], score), (top, left - 6), cv2.FONT_HERSHEY_SIMPLEX,
                    0.6, (0, 0, 255), 2)

