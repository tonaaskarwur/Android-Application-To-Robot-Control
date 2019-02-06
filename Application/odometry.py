import numpy as np
import time
import random

def count_odometry(crd):

	n = 500 #
	rk = 0.01
	R = 0.031
	theta = 90
	s = 0.14 #
	l = 0.18 #

	joint_array = []
	signals_array = []

	for i in range(0, np.shape(crd)[1] - 1):
		Va = [crd[0,i+1] - crd[0,i], crd[1,i+1] - crd[1,i]] #odejmowanie nastepnego elementu od poprzedniego (X i Y)

		if Va[0] == 0 and Va[1] == 0:
			continue

		if (Va[0] == 0 and Va[1] > 0):
			alpha = 90
		elif (Va[0] == 0 and Va[1] < 0):
			alpha = 270
		elif (Va[0] < 0 and Va[1] == 0):
			alpha = 180
		elif (Va[0] > 0 and Va[1] == 0):
			alpha = 0
		elif (Va[1] > 0):
			if (np.arctan(Va[1] / Va[0]) * 180/np.pi) > 0:
				alpha = np.arctan(Va[1] / Va[0]) * 180 / np.pi
			else:
				alpha = np.arctan(Va[1] / Va[0]) * 180 / np.pi + 180
		else:
			if (np.arctan(Va[1] / Va[0]) * 180/np.pi) > 0:
				alpha = np.arctan(Va[1] / Va[0]) * 180 / np.pi + 180
			else:
				alpha = np.arctan(Va[1] / Va[0]) * 180 / np.pi

		if (theta > 270 and alpha < 90):
			#Left
			a1 = np.tan((theta - 90) * np.pi / 180)
			a2 = np.tan((2 * alpha - theta - 90) * np.pi / 180)
			b1 = crd[1,i] - crd[0,i] * a1
			b2 = crd[1,i+1] - crd[0,i+1] * a2
			xo = (b2 - b1) / (a1 - a2)
			yo = a1 * xo + b1

			r1 = np.sqrt((crd[0,i] - xo)**2 + (crd[1,i] - yo)**2)
			r2 = np.sqrt((crd[0,i+1] - xo)**2 + (crd[1,i+1] - yo)**2)
			r1 *= rk
			r2 *= rk

			joint = np.arctan(l / (r1 + 0.5 * s)) * 180 / np.pi

			angle = (2 * alpha - 2 * theta)
			angle = (angle + 360) % 360

			num_signals = (r1 * angle * n) / (360 * R)

			theta = (theta + angle + 360) % 360

		elif (theta < 90 and alpha > 270):
			#Right
			a1 = np.tan((90 + theta) * np.pi / 180)
			a2 = np.tan((180-(theta + 90 - 2 * alpha)) * np.pi / 180)
			b1 = crd[1,i] - crd[0,i] * a1
			b2 = crd[1,i+1] - crd[0,i+1] * a2
			xo = (b2 - b1) / (a1 - a2)
			yo = a1 * xo + b1

			r1 = np.sqrt((crd[0,i] - xo)**2 + (crd[1,i] - yo)**2)
			r2 = np.sqrt((crd[0,i+1] - xo)**2 + (crd[1,i+1] - yo)**2)
			r1 *= rk
			r2 *= rk

			joint = -np.arctan(l / (r1 - 0.5 * s)) * 180 / np.pi

			angle = (2 * theta - 2 * alpha)
			angle = (angle + 360) % 360

			num_signals = (r1 * angle * n) / (360 * R)

			theta = (theta - angle + 360) % 360

		elif alpha > theta:
			#Left
			a1 = np.tan((theta - 90) * np.pi / 180)
			a2 = np.tan((2 * alpha - theta - 90) * np.pi / 180)
			b1 = crd[1,i] - crd[0,i] * a1
			b2 = crd[1,i+1] - crd[0,i+1] * a2
			xo = (b2 - b1) / (a1 - a2)
			yo = a1 * xo + b1

			r1 = np.sqrt((crd[0,i] - xo)**2 + (crd[1,i] - yo)**2)
			r2 = np.sqrt((crd[0,i+1] - xo)**2 + (crd[1,i+1] - yo)**2)
			r1 *= rk
			r2 *= rk

			joint = np.arctan(l / (r1 + 0.5 * s)) * 180 / np.pi

			angle = (2 * alpha - 2 * theta)
			angle = (angle + 360) % 360

			num_signals = (r1 * angle * n) / (360 * R)

			theta = (theta + angle + 360) % 360

		elif alpha < theta:
			#Right
			a1 = np.tan((90 + theta) * np.pi / 180)
			a2 = np.tan((180-(theta + 90 - 2 * alpha)) * np.pi / 180)
			b1 = crd[1,i] - crd[0,i] * a1
			b2 = crd[1,i+1] - crd[0,i+1] * a2
			xo = (b2 - b1) / (a1 - a2)
			yo = a1 * xo + b1

			r1 = np.sqrt((crd[0,i] - xo)**2 + (crd[1,i] - yo)**2)
			r2 = np.sqrt((crd[0,i+1] - xo)**2 + (crd[1,i+1] - yo)**2)
			r1 *= rk
			r2 *= rk

			joint = -np.arctan(l / (r1 - 0.5 * s)) * 180 / np.pi

			angle = (2 * theta - 2 * alpha)
			angle = (angle + 360) % 360

			num_signals = (r1 * angle * n) / (360 * R)

			theta = (theta - angle + 360) % 360

		else:
			#Straight
			angle = 0
			distance = np.sqrt(Va[0] ** 2 + Va[1] ** 2) * rk
			num_signals = (distance * n) / (2 * np.pi * R)
			joint = 0

		joint_array.append(int(joint))
		signals_array.append(int(num_signals))

	return joint_array, signals_array


if __name__ == '__main__':
	crd = np.array([[94, 97, 104, 118, 131, 150, 174, 200, 243, 281, 305, 328, 361, 393, 418, 447, 482, 504, 525, 538, 549, 559, 567, 577, 598, 613], [78, 102, 127, 160, 180, 199, 220, 232, 246, 259, 263, 263, 263, 263, 266, 273, 281, 291, 303, 323, 345, 366, 390, 415, 453, 485]])
	joint, num_signals = count_odometry(crd)
	print(joint)
	print('-------------------------')
	print(num_signals)


