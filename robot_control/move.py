#!/usr/bin/env python3
# File name   : move.py
# Description : Control Motor
# Product     : GWR
# Website     : www.gewbot.com
# Author      : William
# Date        : 2019/07/24
import time
import RPi.GPIO as GPIO
import RGB

# motor_EN_A: Pin7  |  motor_EN_B: Pin11
# motor_A:  Pin8,Pin10    |  motor_B: Pin13,Pin12

Motor_A_EN    = 4
Motor_B_EN    = 17

Motor_A_Pin1  = 14
Motor_A_Pin2  = 15
Motor_B_Pin1  = 27
Motor_B_Pin2  = 18

Dir_forward   = 0
Dir_backward  = 1

left_forward  = 0
left_backward = 1

right_forward = 0
right_backward= 1

pwn_A = 0
pwm_B = 0

setup_completed = False

class Move_Command:
	stop_working : bool
	speed : int
	direction : str
	turn : str
	radius : float

	def __init__(self) -> None:
		self.stop_working = False
		self.speed = 0
		self.direction = 'forward'
		self.turn = 'no'
		self.radius = 0.8

	def set_stop_working(self, stop_working : bool) -> None:
		self.stop_working = stop_working

	def set_speed(self, speed : int) -> None:
		if speed >= 0:
			self.speed = speed

	def set_direction(self, direction : str) -> None:
		if direction == 'forward' or direction == 'backward' or direction == 'no':
			self.direction = direction

	def set_turn(self, turn : str) -> None:
		if turn == 'left' or turn == 'right' or turn == 'no':
			self.turn = turn

	def set_radius(self, radius : float) -> None:
		self.radius = radius

	def get_stop_working(self) -> bool:
		return self.stop_working

	def get_speed(self) -> int:
		return self.speed		
	
	def get_direction(self) -> str:
		return self.direction
	
	def get_turn(self) -> str:
		return self.turn
	
	def get_radius(self) -> float:
		return self.radius

def motorStop() -> None:#Motor stops
	GPIO.output(Motor_A_Pin1, GPIO.LOW)
	GPIO.output(Motor_A_Pin2, GPIO.LOW)
	GPIO.output(Motor_B_Pin1, GPIO.LOW)
	GPIO.output(Motor_B_Pin2, GPIO.LOW)
	GPIO.output(Motor_A_EN, GPIO.LOW)
	GPIO.output(Motor_B_EN, GPIO.LOW)


def setup() -> None:#Motor initialization
	global pwm_A, pwm_B
	GPIO.setwarnings(False)
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(Motor_A_EN, GPIO.OUT)
	GPIO.setup(Motor_B_EN, GPIO.OUT)
	GPIO.setup(Motor_A_Pin1, GPIO.OUT)
	GPIO.setup(Motor_A_Pin2, GPIO.OUT)
	GPIO.setup(Motor_B_Pin1, GPIO.OUT)
	GPIO.setup(Motor_B_Pin2, GPIO.OUT)

	motorStop()
	try:
		pwm_A = GPIO.PWM(Motor_A_EN, 1000)
		pwm_B = GPIO.PWM(Motor_B_EN, 1000)
	except:
		pass


def motor_left(status : int, direction : int, speed : int) -> None:#Motor 2 positive and negative rotation
	if status == 0: # stop
		GPIO.output(Motor_B_Pin1, GPIO.LOW)
		GPIO.output(Motor_B_Pin2, GPIO.LOW)
		GPIO.output(Motor_B_EN, GPIO.LOW)
	else:
		if direction == Dir_backward:
			GPIO.output(Motor_B_Pin1, GPIO.HIGH)
			GPIO.output(Motor_B_Pin2, GPIO.LOW)
			pwm_B.start(100)
			pwm_B.ChangeDutyCycle(speed)
		elif direction == Dir_forward:
			GPIO.output(Motor_B_Pin1, GPIO.LOW)
			GPIO.output(Motor_B_Pin2, GPIO.HIGH)
			pwm_B.start(0)
			pwm_B.ChangeDutyCycle(speed)


def motor_right(status : int, direction : int, speed : int) -> None:#Motor 1 positive and negative rotation
	if status == 0: # stop
		GPIO.output(Motor_A_Pin1, GPIO.LOW)
		GPIO.output(Motor_A_Pin2, GPIO.LOW)
		GPIO.output(Motor_A_EN, GPIO.LOW)
	else:
		if direction == Dir_forward:#
			GPIO.output(Motor_A_Pin1, GPIO.HIGH)
			GPIO.output(Motor_A_Pin2, GPIO.LOW)
			pwm_A.start(100)
			pwm_A.ChangeDutyCycle(speed)
		elif direction == Dir_backward:
			GPIO.output(Motor_A_Pin1, GPIO.LOW)
			GPIO.output(Motor_A_Pin2, GPIO.HIGH)
			pwm_A.start(0)
			pwm_A.ChangeDutyCycle(speed)


def move(speed : int, direction : str, turn : str, radius : float = 0.6):   # 0 < radius <= 1  
	#speed = 100
	if direction == 'forward':
		if turn == 'right':
			motor_left(0, left_backward, int(speed*radius))
			motor_right(1, right_forward, speed)
		elif turn == 'left':
			motor_left(1, left_forward, speed)
			motor_right(0, right_backward, int(speed*radius))
		else:
			motor_left(1, left_forward, speed)
			motor_right(1, right_forward, speed)
	elif direction == 'backward':
		if turn == 'right':
			motor_left(0, left_forward, int(speed*radius))
			motor_right(1, right_backward, speed)
		elif turn == 'left':
			motor_left(1, left_backward, speed)
			motor_right(0, right_forward, int(speed*radius))
		else:
			motor_left(1, left_backward, speed)
			motor_right(1, right_backward, speed)
	elif direction == 'no':
		if turn == 'right':
			motor_left(1, left_backward, speed)
			motor_right(1, right_forward, speed)
		elif turn == 'left':
			motor_left(1, left_forward, speed)
			motor_right(1, right_backward, speed)
		else:
			motorStop()
	else:
		pass




def destroy():
	motorStop()
	GPIO.cleanup()             # Release resource

def move_handler(in_q) -> None:
	if setup_completed == False:
		RGB.setup()
		RGB.red()
		setup()
		RGB.blue()

	while True:
		# Get some data
		mc = in_q.get()

		if mc != None:
			if mc.get_stop_working():
				motorStop()
				RGB.pink()
				destroy()
				print("that is the end")
				in_q.task_done()
				break
			
			RGB.green()
			move(mc.get_speed(), mc.get_direction(), mc.get_turn(), mc.get_radius())
			in_q.task_done()

		# Process the data..
        # Indicate completion
		#in_q.task_done()

if __name__ == '__main__':
	RGB.setup()
	RGB.yellow()
	#RGB.police(4)
	try:
		speed_set = 100
		setup()
		move(speed_set, 'forward', 'no', 0.8)
		time.sleep(1.3)
		motorStop()
		RGB.green()
		destroy()
		print("that is the end")
	except KeyboardInterrupt:
		destroy()

