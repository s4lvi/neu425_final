import sys, random
import pygame
from pygame.locals import *
import pymunk
import pymunk.pygame_util
import math
import numpy as np
from numpy import *
import numpy.matlib as ml
import pymunk as pm
import matplotlib.pyplot as mpl

def add_worm(space, worm_segs, num_segs):
	mass = 1
	radius = 20
	
	x = 100
	for i in range(0,num_segs):
		moment = pymunk.moment_for_circle(mass, 0, radius)
		body = pymunk.Body(mass, moment)
		x = x + 40
		body.position = x, 300
		shape = pymunk.Circle(body, radius)
		shape.friction = 1.0
		resting_length = 10
		stiffness = 20
		damping = 2
		if i > 0:
			jointL = pymunk.DampedSpring(body, worm_segs[i-1][0], (0,20), (0,20), resting_length, stiffness, damping)
			jointC = pymunk.DampedSpring(body, worm_segs[i-1][0], (-20,0), (20,0), .1, 30, 5)
			jointR = pymunk.DampedSpring(body, worm_segs[i-1][0], (0,-20), (0,-20), resting_length, stiffness, damping)
			space.add(body, shape, jointL, jointR, jointC)
			worm_segs.append([body, shape, jointL, jointR])
		else:		
			space.add(body, shape)
			worm_segs.append([body, shape])

def main():
	segments = 7 # length of leech


	################ izhikevich model ################

	Ne=segments*12+2                 
	Ni=0
	re=np.random.rand(Ne,1)
	ri=np.random.rand(Ni,1)
	a=np.vstack([hstack([0.02*ml.ones((Ne,1))]),hstack([0.02+0.08*ri])])
	b=np.vstack([hstack([0.2*ml.ones((Ne,1))]),hstack([0.25-0.05*ri])])
	c=np.vstack([hstack([-65+15*np.power(re,2)]),hstack([-65*ml.ones((Ni,1))])])
	d=np.vstack([hstack([8-6*np.power(re,2)]),hstack([2*ml.ones((Ni,1))])])

	S=ml.zeros((Ne+Ni,Ne+Ni))
	volt=ml.ones((Ne+Ni,1))*-65
	u=volt
	np.multiply(b,u)
	
	# create network connections in segments
	for i in range(0,segments):
		n = 12*i
		for ii in range(1,12):
			# connect each neuron to the next one in segment
			S[((n-1)+ii)+1,((n-1)+ii)] = 40
		# connect the mid neuron to the start of the next segment
		S[n+1,n-9] = 40
	# connect the last neuron  in the first to the first in the first segment
	# so that it fires cyclically 
	S[0,11] = 40
	#inpu = input()
	startI = 20
	I = ml.zeros((Ne+Ni,1))
	I[0] = startI

	
	############ physics & rendering setup ##############

    	pygame.init()
    	screen = pygame.display.set_mode((800, 600))
    	pygame.display.set_caption("LEECHSIM")
    	clock = pygame.time.Clock()

	space = pymunk.Space()
	space.gravity = (0.0, 0.0)

	# add a floor and walls so the leech doesnt leave
	shape = pymunk.Segment(space.static_body, (0,0), (800,0), 1.0)
        shape.friction = 1.0
        space.add(shape)
	shape = pymunk.Segment(space.static_body, (0,0), (0,100), 1.0)
        shape.friction = 1.0
        space.add(shape)
	shape = pymunk.Segment(space.static_body, (800,0), (800,100), 1.0)
        shape.friction = 1.0
        space.add(shape)
	
	# setup rendering and create leech
    	worm_segs = []
    	draw_options = pymunk.pygame_util.DrawOptions(screen)
	lines = add_worm(space, worm_segs, segments)

	counter = 0 # for sine oscillator
		
	lengthL = 30 # initial lengths for muscle
	lengthR = 30
	
	oscillator = 1 # 1 for neural oscillator, 2 for sine


	############# simulation loop #############

    	while True:

		# allow closing of program
        	for event in pygame.event.get():
            		if event.type == QUIT:
                		sys.exit(0)
            		elif event.type == KEYDOWN and event.key == K_ESCAPE:
                		sys.exit(0)


		########### render screen #############

        	space.step(1/50.0) # i think this is simulation speed

        	screen.fill((255,255,255))
        	space.debug_draw(draw_options)


 		############### izhikevich #################
		
		fired=np.zeros((Ne+Ni,1))
		for i in range(0,Ne+Ni):
			if volt[i]>=30:
				fired[i]=1
				volt[i] = c[i]
				u[i]=u[i]+d[i]
			
		S2 = S*fired
		I=np.add(I,S2*2)
		print(I)

		volt=volt+0.5*(0.04*ml.power(volt,2)+5*volt+140-u+I)
		volt=volt+0.5*(0.04*ml.power(volt,2)+5*volt+140-u+I)
		u=u+np.multiply(a,(np.multiply(b,volt))-u)
		I = ml.zeros((Ne+Ni,1))


		############ move 'muscles' ##########

		for i in range(1,segments):
			
			if (oscillator == 1):
				if fired[(i*12)-1] > 0:
					lengthL = -200
				else:
					lengthL = 0

				if fired[(i*12)-9] > 0:
					lengthR = -200
				else:
					lengthR = 0

				worm_segs[i][2].rest_length = lengthL
				worm_segs[i][3].rest_length = lengthR
			
			elif (oscillator == 2):
				# sine oscillator for test
				length = math.sin((counter+10*i)*3.14159265/45)*20
				worm_segs[i][2].rest_length = -length
				worm_segs[i][3].rest_length = length

			
		counter = counter + 1
        	pygame.display.flip()
        	clock.tick(50)

if __name__ == '__main__':
    	main()
