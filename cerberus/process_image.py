import cv2
import numpy as np
from PIL import Image
import imutils

FILEPATH = 'venv/test/locked.jpg'
EXPECTED = (314, 244)
CROPSIZE = (50, 50) # <- added: what size do you want to extract


def take_picture(filepath):
    # initialize the camera
    # initialize the camera
    cam = cv2.VideoCapture(0)  # 0 -> index of camera
    s, img = cam.read()
    if s:  # frame captured without any errors
        # cv2.namedWindow("cam-test", cv2.CV_WINDOW_AUTOSIZE)
        # cv2.imshow("cam-test", img)
        # cv2.waitKey(0)
        # cv2.destroyWindow("cam-test")
        if filepath:
            cv2.imwrite(filepath, img)  # save image
    return Image.fromarray(img)

def in_range(expected_tuple, found_tuple):
    x_ex_pos = expected_tuple[0]
    y_ex_pos = expected_tuple[1]

    x_fd_pos = found_tuple[0]
    y_fd_pos = found_tuple[1]

    return (not(x_fd_pos/x_ex_pos >= 1.05 or x_fd_pos/x_ex_pos <= 0.95)) and\
           (not(y_fd_pos/y_ex_pos >= 1.05 or y_fd_pos/y_ex_pos <= 0.95))

def find_circles(gray_img):
    cimg = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)

    circles = cv2.HoughCircles(gray_img, cv2.HOUGH_GRADIENT, 1, 30,
                               param1=30, param2=20, minRadius=10, maxRadius=200)

    circles = np.uint16(np.around(circles))

    retval = {}
    for i in circles[0, :]:
        if in_range(EXPECTED, (i[0], i[1])):
            # draw the outer circle
            cv2.circle(cimg, (i[0], i[1]), i[2], (0, 255, 0), 2)
            # draw the center of the circle
            # cv2.circle(cimg, (i[0], i[1]), 2, (0, 0, 255), 3)

            # crop ROI around circle...?
            # make sure the bounds won't under-/overflow
            cropCoords = (max(0, i[1] - CROPSIZE[0] // 2), min(gray_img.shape[0], i[1] + CROPSIZE[0] // 2),
                          max(0, i[0] - CROPSIZE[1] // 2), min(gray_img.shape[1], i[0] + CROPSIZE[1] // 2))
            crop_cimg = cimg[cropCoords[0]:cropCoords[1],
                        cropCoords[2]:cropCoords[3]]

            retval["cimg"] = cimg
            retval["cropped"] = crop_cimg
    return retval


def find_center_of_circles(gray_img):
    circles = cv2.HoughCircles(gray_img, cv2.HOUGH_GRADIENT, 1, 30,
                               param1=30, param2=20, minRadius=2, maxRadius=200)
    circles = np.uint16(np.around(circles))

    # for i in circles[0, :]:
    #     cv2.circle(gray_img, (i[0], i[1]), i[2], (0, 255, 0), 2)
    #     cv2.imshow("circs", gray_img)

    retval = []
    for i in circles[0, :]:
        retval.append((i[0], i[1]))
    return retval


def find_shape_center(image, gray):
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.threshold(blurred, 1, 2, cv2.THRESH_BINARY)[1]

    # find contours in the thresholded image
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    # loop over the contours
    for c in cnts:
        # compute the center of the contour
        M = cv2.moments(c)
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])

        # draw the contour and center of the shape on the image
        cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
        cv2.circle(image, (cX, cY), 7, (255, 255, 255), -1)

        # show the image
    return image


def detect_blob(bgr_img):
    # Switch image from BGR colorspace to HSV
    hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)

    # define range of purple color in HSV
    sensitivity = 100
    lower_white = np.array([0, 0, 255-sensitivity], dtype=np.uint8)
    upper_white = np.array([255, sensitivity, 255], dtype=np.uint8)

    # Sets pixels to white if in purple range, else will be set to black
    mask = cv2.inRange(hsv, lower_white, upper_white)

    # Bitwise-AND of mask and purple only image - only used for display
    res = cv2.bitwise_and(bgr_img, bgr_img, mask=mask)

    #    mask = cv2.erode(mask, None, iterations=1)
    # commented out erode call, detection more accurate without it

    # dilate makes the in range areas larger
    mask = cv2.dilate(mask, None, iterations=1)

    # Set up the SimpleBlobdetector with default parameters.
    params = cv2.SimpleBlobDetector_Params()

    # Change thresholds
    params.minThreshold = 0;
    params.maxThreshold = 256;

    # Filter by Area.
    params.filterByArea = True
    params.minArea = 5

    # Filter by Circularity
    params.filterByCircularity = True
    params.minCircularity = 0.1

    # Filter by Convexity
    params.filterByConvexity = True
    params.minConvexity = 0.5

    # Filter by Inertia
    params.filterByInertia = True
    params.minInertiaRatio = 0.5

    detector = cv2.SimpleBlobDetector_create(params)

    # Detect blobs.
    reversemask = 255 - mask
    keypoints = detector.detect(reversemask)

    # for keyPoint in keypoints:
    #     x = keyPoint.pt[0]
    #     y = keyPoint.pt[1]
    #     s = keyPoint.size

    center_list = []
    for keypoint in keypoints:
        center_list.append((np.around(keypoint.pt[0]), np.around(keypoint.pt[1])))

    # Draw green circles around detected blobs
    # im_with_keypoints = cv2.drawKeypoints(bgr_img, keypoints, np.array([]), (0, 255, 0),
    #                                       cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    # return im_with_keypoints
    return center_list


def generate_cropped_file(out_file_path, filepath):
    if not filepath:
        filepath = FILEPATH
    gray_img = cv2.imread(filepath, 0)
    gray_img = cv2.medianBlur(gray_img, 5)

    # cv2.imshow('detected circles', gray_img)
    #
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    im_dict = find_circles(gray_img)
    im = Image.fromarray(im_dict["cropped"])
    im.save(out_file_path)


def run(filepath):
    temppath = "temp.jpg"
    generate_cropped_file(temppath, filepath)

    cropped_image = cv2.imread(temppath, 1)

    retval = dict()
    retval["blob"] = detect_blob(cropped_image)
    retval["orig"] = find_center_of_circles(cv2.cvtColor(cropped_image, cv2.COLOR_BGR2GRAY))
    # retval["blob"] = find_center_of_circles(cv2.cvtColor(found_blob, cv2.COLOR_BGR2GRAY))

    # cv2.imshow('detected circles', cropped_image)
    # cv2.imshow('detected blob', found_blob)
    #
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    return retval


if __name__ == "__main__":
    print(run(""))
