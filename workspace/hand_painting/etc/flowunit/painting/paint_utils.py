import copy
import math
import numpy as np
import cv2
from one_euro_filter import GaussianFilter


points_score_thr = 0.1
thickness = 2
link_pairs = [
    [[0, 1], [1, 2], [2, 3], [3, 4]],
    [[0, 5], [5, 6], [6, 7], [7, 8]],
    [[0, 9], [9, 10], [10, 11], [11, 12]],
    [[0, 13], [13, 14], [14, 15], [15, 16]],
    [[0, 17], [17, 18], [18, 19], [19, 20]]
]

color_palette = [
    (173, 173, 255), (165, 214, 255), (182, 255, 253),
    (191, 255, 202), (255, 246, 155), (255, 196, 160),
    (255, 178, 189), (255, 198, 255), (255, 255, 252), (6, 6, 6)
]

angle_pairs = [[(0, 2), (3, 4)], [(0, 6), (7, 8)], [(0, 10), (11, 12)], [(0, 14), (15, 16)], [(0, 18), (19, 20)]]


def hand_pose(img, pose, box, draw_pts, palette_left, tmp_array, pick_color):
    
    x1, y1, x2, y2 = box
    gesture, index_, pts_hand = decode_landmarks(pose, x1, y1, x2, y2)
    
    if tmp_array.size == 0:
        tmp_array = np.zeros_like(img, dtype=np.uint8)

    click_state = False

    if gesture == "five":
        click_state = True
        cv2.circle(img, index_, 6, (0, 0, 255), 1)
    
    if gesture == "love" and index_[1] < palette_left:
        pick_color = img[index_[1], index_[0], :].copy()
        pick_color = tuple((int(c) for c in pick_color))
        cv2.circle(img, index_, 6, (255, 0, 0), 1)

    if gesture == "fist":
        tmp_array = np.zeros_like(img, dtype=np.uint8)
        draw_pts = []

    if click_state and index_[1] > palette_left:
        draw_pts.append((index_[0], index_[1], pick_color))

    else:
        draw_pts = []
    
    draw_hand_pose(img, pts_hand, pick_color)
    return draw_pts, tmp_array, pick_color


def decode_landmarks(pose, x1, y1, x2, y2):
    pts_hand = {}
    scale = np.array([abs(x2 - x1), abs(y2 - y1)], dtype=np.float32)
    scale_x = scale[0] / 64
    scale_y = scale[1] / 64
    center = np.array([(x1 + x2) / 2, (y1 + y2) / 2], dtype=np.float32)
    pose[:, 0] = pose[:, 0] * scale_x + center[0] - scale[0] * 0.5
    pose[:, 1] = pose[:, 1] * scale_y + center[1] - scale[1] * 0.5

    for ptk, (xh, yh, score) in enumerate(pose):
        pts_hand[str(ptk)] = {
            "x": xh,
            "y": yh,
            "s": score
        }
        if ptk == 8:
            index_ = int(xh), int(yh)

    angle_list =  get_angle_list(pts_hand)
    gesture = get_gesture(angle_list)

    return gesture, index_, pts_hand


def draw_hand_pose(img_, hand_, color):

    for link_pair in link_pairs:
        for pair in link_pair:
            if hand_[str(pair[0])]['s'] > points_score_thr and hand_[str(pair[1])]['y'] > points_score_thr:
                cv2.line(img_, (int(hand_[str(pair[0])]['x']), int(hand_[str(pair[0])]['y'])),
                        (int(hand_[str(pair[1])]['x']), int(hand_[str(pair[1])]['y'])), color, thickness)


def draw_click_lines(img, draw_pts, tmp_array):
    draw_line = np.array(copy.deepcopy(draw_pts))

    if len(draw_line) >= 2:
        #smooth_filter = OneEuroFilter(np.array(draw_line[0][:2]))
        draw_line = draw_line.reshape(-1, 3, 1)
        gaussian_filter = GaussianFilter()
        draw_line[:, :2, :] = gaussian_filter(draw_line[:, :2, :].astype(np.float32))
        draw_line = draw_line.reshape(-1, 3)
        for i in range(len(draw_line) - 1):
            pt1 = draw_line[i][:2]
            pt2 = draw_line[i + 1][:2]
            cv2.line(tmp_array, (int(pt1[0]), int(pt1[1])), (int(pt2[0]), int(pt2[1])), draw_line[i][-1], 4, cv2.LINE_AA)
        
    
    img2gray = cv2.cvtColor(tmp_array, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(img2gray, 2, 255, cv2.THRESH_BINARY)
    mask_inv = cv2.bitwise_not(mask)

    img = cv2.bitwise_and(img, img, mask=mask_inv)
    img = np.uint8(img + tmp_array)
    return img


def vector_2d_angle(v1, v2):
    v1_x, v1_y = v1
    v2_x, v2_y = v2
    try:
        angle_ = math.degrees(
            math.acos(
                (v1_x * v2_x + v1_y * v2_y) / (((v1_x ** 2 + v1_y ** 2) ** 0.5) * ((v2_x ** 2 + v2_y ** 2) ** 0.5))))

    except ZeroDivisionError as e:
        print(e)
        angle_ = 65535.
    except (TypeError, ValueError) as e:
        print(e)
        angle_ = 65535.

    if angle_ > 180.:
        angle_ = 65535.
    return angle_


def draw_color_palette(img):
    _, W, _ = img.shape
    palette_c = W // len(color_palette)
    for i, c in enumerate(color_palette):
        cv2.rectangle(img, (i * palette_c, 0), ((i + 1) * palette_c, palette_c), c, -1)

    return palette_c



def get_angle_list(hand):
    angle_list = [vector_2d_angle(
            ((int(hand[str(p1[0])]['x']) - int(hand[str(p1[1])]['x'])), (int(hand[str(p1[0])]['y']) - int(hand[str(p1[1])]['y']))),
            ((int(hand[str(p2[0])]['x']) - int(hand[str(p2[1])]['x'])), (int(hand[str(p2[0])]['y']) - int(hand[str(p2[1])]['y'])))
        ) for p1, p2 in angle_pairs]

    return angle_list


def get_gesture(angle_list):
    thr_angle = 65.
    thr_angle_thumb = 53.
    thr_angle_s = 49.
    gesture_str = "other"
    if 65535. not in angle_list:
        if (angle_list[0] > thr_angle_thumb) and (angle_list[1] > thr_angle) and (angle_list[2] > thr_angle) and (
                angle_list[3] > thr_angle) and (angle_list[4] > thr_angle):
            gesture_str = "fist"
        elif (angle_list[0] > 5) and (angle_list[1] < thr_angle_s) and (angle_list[2] > thr_angle) and (
                angle_list[3] > thr_angle) and (angle_list[4] > thr_angle):
            gesture_str = "one"
        elif (angle_list[0] < thr_angle_s) and (angle_list[1] < thr_angle_s) and (angle_list[2] > thr_angle) and (
                angle_list[3] > thr_angle) and (angle_list[4] < thr_angle_s):
            gesture_str = "love"

        elif (angle_list[0] < thr_angle_s) and (angle_list[1] < thr_angle_s) and (angle_list[2] < thr_angle_s) and (
            angle_list[3] < thr_angle_s) and (angle_list[4] < thr_angle_s):
            gesture_str = "five"
 
    return gesture_str
