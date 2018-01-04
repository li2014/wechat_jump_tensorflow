# -*- coding: utf-8 -*-

import numpy as np
import cv2
import os
import time
import re

# 屏幕截图
def pull_screenshot(path):
	os.system('adb shell screencap -p /sdcard/%s' % path)
	os.system('adb pull /sdcard/%s .' % path)

# 根据x距离跳跃
def jump(distance, alpha):
	press_time = max(int(distance * alpha), 200)

	cmd = 'adb shell input swipe {} {} {} {} {}'.format(bx1, by1, bx2, by2, press_time)
	os.system(cmd)

screenshot = 'screenshot.png'
alpha = 0
bx1, by1, bx2, by2 = 0, 0, 0, 0
chess_x = 0
target_x = 0

fix = 1.6667
# 检查分辨率是否是960x540
size_str = os.popen('adb shell wm size').read()
if size_str:
	m = re.search(r'(\d+)x(\d+)', size_str)
	if m:
		hxw = "{height}x{width}".format(height=m.group(2), width=m.group(1))
		if hxw == "960x540":
			fix = 3.16

import itertools
jump_times = itertools.count(0)
while True:
	screenshot = str(next(jump_times)) + '.png'
	pull_screenshot(screenshot)
	image_np = cv2.imread(screenshot)
	#在OpenCV中，图像不是用常规的RGB颜色通道来存储的，它们用的是BGR顺序。当读取一幅图像后，默认的是BGR
	#颜色空间转换可以用函数cvtColor()函数
	image_np = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
	#
	gray = cv2.Canny(image_np, 20, 80)

	HEIGHT = image_np.shape[0]
	WIDTH = image_np.shape[1]

	bx1 = WIDTH / 2
	bx2 = WIDTH / 2
	by1 = HEIGHT * 0.785
	by2 = HEIGHT * 0.785
	alpha = WIDTH * fix

	# 获取棋子x坐标
	linemax = []
	for i in range(int(HEIGHT * 0.4), int(HEIGHT * 0.6)):
		line = []
		for j in range(int(WIDTH * 0.15), int(WIDTH * 0.85)):
			if image_np[i, j, 0] > 40 and image_np[i, j, 0] < 70 and image_np[i, j, 1] > 40 and image_np[i, j, 1] < 70 and image_np[i, j, 2] > 60 and image_np[i, j, 2] < 110:
				gray[i, j] = 255
				if len(line) > 0 and j - line[-1] > 1:
					break
				else:
					line.append(j)

		if len(line) > 5 and len(line) > len(linemax):
			linemax = line
		if len(linemax) > 20 and len(line) == 0:
			break

	chess_x = int(np.mean(linemax))

	# 获取目标x坐标
	for i in range(int(HEIGHT * 0.3), int(HEIGHT * 0.5)):
		flag = False
		for j in range(WIDTH):
			# 超过朋友时棋子上方的图案
			if np.abs(j - chess_x) < len(linemax):
				continue
			if not gray[i, j] == 0:
				target_x = j
				flag = True
				break
		if flag:
			break

	# 修改检测图
	gray[:, chess_x] = 255
	gray[:, target_x] = 255
	# 保存检测图
	cv2.imwrite(screenshot.replace(".png",".debug.png"), gray)

	print(chess_x, target_x)
	jump(float(np.abs(chess_x - target_x)) / WIDTH, alpha)

	# 等棋子落稳
	time.sleep(np.random.random() + 0.5)


