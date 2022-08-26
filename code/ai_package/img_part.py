import cv2
import numpy as np


def partimg():
    def part_other_and_number(img):
        # cv2.imshow('img',img)
        # 灰度化处理：
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        # cv2.imshow('huidu',gray)
        # 二值化处理
        ret2, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        # binary=cv2.threshold(gray,140,255,1)[1]#二值化函数 草了白字可以 黑字不好
        # cv2.imshow('binary',binary)
        # 膨胀
        kernel = np.ones((6, 6), np.uint8)
        dilate = cv2.dilate(binary, kernel, iterations=4)
        # cv2.imshow("dilate",dilate )
        # 轮廓查找
        contours, hierarchy = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        for contour in contours:
            epsilon = 0.001
            approx = cv2.approxPolyDP(contour, epsilon, True)
            x, y, w, h = cv2.boundingRect(approx)
            if (w > 7 * h):
                area = binary[0:y, 0:(x + w)]
                numberarea = binary[y:(y + h), x:(x + w)]

        return area, numberarea

    def getHProjection(image):
        hProjection = np.zeros(image.shape, np.uint8)
        # 图像高与宽
        (h, w) = image.shape
        # 长度与图像高度一致的数组
        h_ = [0] * h
        # 循环统计每一行白色像素的个数
        for y in range(h):
            for x in range(w):
                if image[y, x] == 255:
                    h_[y] += 1
        # 绘制水平投影图像
        for y in range(h):
            for x in range(h_[y]):
                hProjection[y, x] = 255
        # cv2.imshow('hProjection2',hProjection)
        return h_

    def getVProjection(image):
        vProjection = np.zeros(image.shape, np.uint8);
        (h, w) = image.shape
        w_ = [0] * w
        for x in range(w):
            for y in range(h):
                if image[y, x] == 255:
                    w_[x] += 1
        for x in range(w):
            for y in range(h - w_[x], h):
                vProjection[y, x] = 255
        return w_

    # 读入原始图像
    origineImage = cv2.imread('test.jpg')
    img, number = part_other_and_number(origineImage)
    # cv2.imshow('image',img)
    # cv2.waitKey(0)
    # 图像灰度化   
    # image = cv2.imread('test.jpg',0)
    """
    image = cv2.cvtColor(origineImage,cv2.COLOR_BGR2GRAY)
    cv2.imshow('gray',image)
    # 将图片二值化
    retval, img = cv2.threshold(image,127,255,cv2.THRESH_BINARY_INV)
    cv2.imshow('binary',img)
    """
    # 图像高与宽
    (h, w) = img.shape
    Position = []

    W = getVProjection(img)
    Wstart = 0
    Wend = 0
    W_Start = w
    W_End = w
    for j in range(len(W) - 1, 0, -1):
        if W[j] > 0 and Wstart == 0:
            W_Start = j
            Wstart = 1
            Wend = 0
        if W[j] <= 0 and Wstart == 1:
            W_End = j
            Wstart = 0
            Wend = 1
        if Wend == 1:
            img = img[0:h, 0:j]
            Wend = 0
            break


    (h, w) = img.shape

    # 水平投影
    H = getHProjection(img)
    start = 0
    H_Start = []
    H_End = []

    list = []
    for i in range(len(H)):
        if H[i] > 0 and start == 0:
            H_Start.append(i)
            start = 1
        if H[i] <= 0 and start == 1:
            H_End.append(i)
            start = 0
    photolist = []
    for i in range(len(H_Start)):
        # 获取行图
        if i>=3:
            break
        try:
            cropImg = img[H_Start[i]:H_End[i], 0:w]
        except:
            break
        photolist.append(cropImg)
        """cv2.imshow('cropImg',cropImg)
        cv2.waitKey(0)"""
        # 对行图像进行垂直投影
        W = getVProjection(cropImg)
        Wstart = 0
        Wend = 0
        W_Start = 0
        W_End = 0
        for j in range(len(W)):
            if W[j] > 0 and Wstart == 0:
                W_Start = j
                Wstart = 1
                Wend = 0
            if W[j] <= 0 and Wstart == 1:
                W_End = j
                Wstart = 0
                Wend = 1
            if Wend == 1:
                Position.append([W_Start, H_Start[i], W_End, H_End[i]])
                Wend = 0
    # 根据确定的位置分割字符
    return photolist, number
