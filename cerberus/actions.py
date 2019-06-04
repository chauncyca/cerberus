import cv2
import copy
import numpy as np

FILEPATH = 'venv/test/locked.jpg'
EXPECTED = (122, 1154)
CROPSIZE = (100, 100) # <- added: what size do you want to extract


def in_range(expected_tuple, found_tuple):
    x_ex_pos = expected_tuple[0]
    y_ex_pos = expected_tuple[1]

    x_fd_pos = found_tuple[0]
    y_fd_pos = found_tuple[1]

    return (x_fd_pos/x_ex_pos >= 1.05 or x_fd_pos/x_ex_pos <= 0.95) and\
           (y_fd_pos/y_ex_pos >= 1.05 or y_fd_pos/y_ex_pos <= 0.95)

def find_circles(filepath):
    img = cv2.imread(filepath, 0)
    img = cv2.medianBlur(img, 5)
    cimg = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, 700,
                               param1=50, param2=30, minRadius=20, maxRadius=100)

    croppedimg = copy.deepcopy(cimg)
    circles = np.uint16(np.around(circles))

    retval = {}
    for i in circles[0, :]:

        if in_range(EXPECTED, (i[0], i[1])):
            # draw the outer circle
            cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)

            # crop ROI around circle...?
            # make sure the bounds won't under-/overflow
            cropCoords = (max(0, i[1] - CROPSIZE[0] // 2), min(img.shape[0], i[1] + CROPSIZE[0] // 2),
                          max(0, i[0] - CROPSIZE[1] // 2), min(img.shape[1], i[0] + CROPSIZE[1] // 2))
            crop_cimg = cimg[cropCoords[0]:cropCoords[1],
                        cropCoords[2]:cropCoords[3]]

            retval["cimg"] = cimg
            retval["cropped"] = crop_cimg
            retval["center"] = (i[0], i[1])
    return retval

img = find_circles(FILEPATH)

cv2.imshow('detected circles', img["cropped"])
cv2.waitKey(0)
cv2.destroyAllWindows()
