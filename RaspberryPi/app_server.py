import socket
import RPi.GPIO as GPIO
import time
import GlobalShared
import netifaces as ni
import sys
import os
from database import Database
import pickle
from threading import Thread
import odometry
import numpy as np
import datetime

encoderA = 6
encoderB = 5

left_arrow = 2
right_arrow = 3

servo = 21

motor_input1 = 13
motor_input2 = 19
motor_pwm = 26

trigger = 9
echo_fr = 4
echo_right = 16
echo_left = 27
echo_right_up = 17
echo_left_up = 22

go_route = 0

Encoder_Count = 0
front_sensor_value = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

#BASIC SETUP
GPIO.setup(left_arrow, GPIO.OUT)
GPIO.setup(right_arrow, GPIO.OUT)

#ENCODER SETUP
GPIO.setup (encoderA, GPIO.IN)
GPIO.setup (encoderB, GPIO.IN)

#DC SETUP
GPIO.setup(motor_input1, GPIO.OUT)
GPIO.setup(motor_input2, GPIO.OUT)

#ARROWS SIGNALS
GPIO.output(left_arrow, GPIO.HIGH)
GPIO.output(right_arrow, GPIO.HIGH)


#DC SIGNALS
GPIO.output(motor_input1, GPIO.LOW)
GPIO.output(motor_input2, GPIO.HIGH)

#DC PWM
GPIO.setup(motor_pwm, GPIO.OUT)   
pwm_motor= GPIO.PWM(motor_pwm, 50)  
pwm_motor.start(0)

#SERVO PWM
GPIO.setup(servo, GPIO.OUT)  
pwm_servo = GPIO.PWM(servo, 50)  
pwm_servo.start(5)


#DIST SENSORS
GPIO.setup(trigger, GPIO.OUT)
GPIO.setup(echo_fr, GPIO.IN)
GPIO.setup(echo_right, GPIO.IN)
GPIO.setup(echo_left, GPIO.IN)
GPIO.setup(echo_right_up, GPIO.IN)
GPIO.setup(echo_left_up, GPIO.IN)

#CREATE DATABASE
my_database = Database()
my_database.create_database('my_database')

def map_function(value, leftMin, leftMax, rightMin, rightMax):
	# Figure out how 'wide' each range is
	leftSpan = leftMax - leftMin
	rightSpan = rightMax - rightMin

	# Convert the left range into a 0-1 range (float)
	valueScaled = float(value - leftMin) / float(leftSpan) 

	# Convert the 0-1 range into a value in the right range.
	return rightMin + (valueScaled * rightSpan)

def read_data():
	global Encoder_Count
	global go_route

	host = ni.ifaddresses('wlan0')[ni.AF_INET][0]['addr']
	port = 1313

	print(host)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	s.bind((host,port))
	s.listen(5)

	print('Waiting for a connection')

	conn, addr = s.accept()
	print('connection from', addr)
	conn.send(str.encode('GC'))

	while True:
		try:
			data = conn.recv(3000)
			data = data.decode('utf-8')
		except:
			pass

		if data:
			pass
			if data[:2] == b'GO':
				go_route = 1
				data = data[2:]
				pwm_servo.ChangeDutyCycle(5)
				try:
					GlobalShared.points_array = np.array(pickle.loads(data[2:]))
				except:
					pass
				if GlobalShared.points_array.size:
					joint, num_signals = odometry.count_odometry(GlobalShared.points_array)
					for single_joint, single_signal in zip(joint, num_signals):
						Encoder_Count = 0
						single_joint += 27
						go_changed_value = (single_joint/90)*5+3.5
						if go_changed_value > 6.5:
							go_changed_value = 6.5
						elif go_changed_value < 3.5:
							go_changed_value = 3.5
						pwm_servo.ChangeDutyCycle(go_changed_value)
						while Encoder_Count <= single_signal:
							while front_sensor_value <= 30:
								pwm_motor.ChangeDutyCycle(0)
							pwm_motor.ChangeDutyCycle(80)
							time.sleep(0.01)
					pwm_motor.ChangeDutyCycle(0)
				go_route = 0
					
			else:
				try:
					for single_mess in data.split('/'):
						if single_mess[0:2] == 'LA':
							try:
								GlobalShared.left_arrow = single_mess[2]
							except:
								pass
						elif single_mess[0:2] == 'RA':
							try:
								GlobalShared.right_arrow = single_mess[2]
							except:
								pass
						elif single_mess[0:2] == 'FB':
							try:
								GlobalShared.forward_back = single_mess[2]
							except:
								pass
						elif single_mess[0:2] == 'DI':
							try:
								GlobalShared.direction = single_mess[2:]
							except:
								pass
						elif single_mess[0:2] == 'SP':
							try:
								GlobalShared.speed = single_mess[2:]
							except:
								pass
						elif single_mess[0:2] == 'DB':
							my_database = Database()
							my_database.load_database('my_database')
							exam = my_database.read_from_database()
							data_to_send=pickle.dumps(exam)
							conn.send(data_to_send+str.encode('GD'))
						elif single_mess[0:2] == 'EX':
							if s:
								s.close()
							if conn:
								conn.close()
							sys.exit()
				except:
					pass
		else:
			conn, addr = s.accept()
			print('connection from', addr)
			conn.send(str.encode('GC'))

		if go_route == 0:
			#DC
			try:
				if front_sensor_value <= 30:
					pwm_motor.ChangeDutyCycle(0)
				else:
					pwm_motor.ChangeDutyCycle(int(GlobalShared.speed))
			except:
				pass

			#SERVO
			try:
				changed_value = map_function(int(GlobalShared.direction), -5, 5, 3.5, 6.5)
				changed_value = round(changed_value, 1)
				if changed_value > 6.5:
					changed_value = 6.5
				elif changed_value < 3.5:
					changed_value = 3.5
				pwm_servo.ChangeDutyCycle(changed_value)
			except:
				pass

		if GlobalShared.left_arrow == '1':
				GPIO.output(left_arrow, GPIO.HIGH)
		elif GlobalShared.left_arrow == '0':
			GPIO.output(left_arrow, GPIO.LOW)

		if GlobalShared.right_arrow == '1':
			GPIO.output(right_arrow, GPIO.HIGH)
		elif GlobalShared.right_arrow == '0':
			GPIO.output(right_arrow, GPIO.LOW)
		
		if GlobalShared.forward_back == '0':
			GPIO.output(motor_input1, GPIO.HIGH)
			GPIO.output(motor_input2, GPIO.LOW)
		elif GlobalShared.forward_back == '1':
			GPIO.output(motor_input1, GPIO.LOW)
			GPIO.output(motor_input2, GPIO.HIGH)	

def dist_sens_loop():
	global front_sensor_value
	my_database = Database()
	my_database.load_database('my_database')

	i = 0

	while True:
		ts = time.time()
		time_stamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

		distances = []

		#FRONT SENSOR

		# set trigger to HIGH
		GPIO.output(trigger, True)

		# set trigger after 0.01ms to LOW
		time.sleep(0.00001)
		GPIO.output(trigger, False)

		StartTime = time.time()
		StopTime = time.time()

		# save StartTime
		while GPIO.input(echo_fr) == 0:
			StartTime = time.time()

		# save time of arrival
		while GPIO.input(echo_fr) == 1:
			StopTime = time.time()

		# time difference between start and arrival
		TimeElapsed = StopTime - StartTime

		# multiply with the sonic speed (34300 cm/s)
		# and divide by 2, because there and back
		distance = (TimeElapsed * 34300) / 2

		front_sensor_value = 100
		distances.append(distance)

		#LEFT SENSOR

		GPIO.output(trigger, True)

		time.sleep(0.00001)
		GPIO.output(trigger, False)

		StartTime = time.time()
		StopTime = time.time()

		while GPIO.input(echo_left) == 0:
			StartTime = time.time()

		while GPIO.input(echo_left) == 1:
			StopTime = time.time()

		TimeElapsed = StopTime - StartTime
		
		distance = (TimeElapsed * 34300) / 2

		distances.append(distance)

		#RIGHT SENSOR
				
		GPIO.output(trigger, True)

		time.sleep(0.00001)
		GPIO.output(trigger, False)

		StartTime = time.time()
		StopTime = time.time()

		while GPIO.input(echo_right) == 0:
			StartTime = time.time()

		while GPIO.input(echo_right) == 1:
			StopTime = time.time()

		TimeElapsed = StopTime - StartTime

		distance = (TimeElapsed * 34300) / 2

		distances.append(distance)

		#LEFT-UP SENSOR

		GPIO.output(trigger, True)

		time.sleep(0.00001)
		GPIO.output(trigger, False)

		StartTime = time.time()
		StopTime = time.time()

		while GPIO.input(echo_left_up) == 0:
			StartTime = time.time()

		while GPIO.input(echo_left_up) == 1:
			StopTime = time.time()

		TimeElapsed = StopTime - StartTime

		distance = (TimeElapsed * 34300) / 2

		distances.append(distance)

		# RIGHT-UP SENSOR

		GPIO.output(trigger, True)

		time.sleep(0.00001)
		GPIO.output(trigger, False)

		StartTime = time.time()
		StopTime = time.time()

		while GPIO.input(echo_right_up) == 0:
			StartTime = time.time()

		while GPIO.input(echo_right_up) == 1:
			StopTime = time.time()

		TimeElapsed = StopTime - StartTime

		distance = (TimeElapsed * 34300) / 2

		distances.append(distance)

		my_database.save_to_database(i, time_stamp, distances[0], distances[1], distances[2],
			distances[3], distances[4], GlobalShared.speed, GlobalShared.direction, GlobalShared.forward_back)
		print ("Measured Distance:", distances)
		my_database.commit_database()

		i += 1	

		time.sleep(1)

def do_Encoder(channel):
	global Encoder_Count
	if GPIO.input(encoderB) == 1:
		Encoder_Count -= 1
	else:
		Encoder_Count += 1
		
# Enable interrupt
GPIO.add_event_detect(encoderA, GPIO.FALLING, callback=do_Encoder)
		
try:

	f1 = Thread(target=read_data)
	f1.daemon = True
	f1.start()
	f2 = Thread(target=dist_sens_loop)
	f2.daemon = True
	f2.start()

	while True:
		time.sleep(0.01)

# Reset by pressing CTRL + C
except KeyboardInterrupt:
	print("Measurement stopped by User")
	exam = my_database.read_from_database()
	print(exam)
	my_database.close_database()
	GPIO.cleanup()
