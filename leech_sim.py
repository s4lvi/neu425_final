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


def add_worm(space, worm_segs):
	segments = 8
	mass = 1
	radius = 20
	
	x = 100
	for i in range(0,segments):
		moment = pymunk.moment_for_circle(mass, 0, radius)
		body = pymunk.Body(mass, moment)
		x = x + 40
		body.position = x, 300
		shape = pymunk.Circle(body, radius)
		shape.friction = 1.0
		resting_length = 10
		stiffness = 20
		damping = 5
		if i > 0:
			jointL = pymunk.DampedSpring(body, worm_segs[i-1][0], (0,20), (0,20), resting_length, stiffness, damping)
			jointC = pymunk.DampedSpring(body, worm_segs[i-1][0], (-20,0), (20,0), .1, stiffness, damping)
			jointR = pymunk.DampedSpring(body, worm_segs[i-1][0], (0,-20), (0,-20), resting_length, stiffness, damping)
			space.add(body, shape, jointL, jointR, jointC)
			worm_segs.append([body, shape, jointL, jointR])
		else:		
			space.add(body, shape)
			worm_segs.append([body, shape])


def to_pygame(p):
    return int(p.x), int(-p.y+600)

def main():


	################ izhikevich setup ################

	segments = 8

	Ne=segments*12+2                 
	Ni=0
	re=np.random.rand(Ne,1)
	ri=np.random.rand(Ni,1)
	a=np.vstack([hstack([0.02*ml.ones((Ne,1))]),hstack([0.02+0.08*ri])])
	b=np.vstack([hstack([0.2*ml.ones((Ne,1))]),hstack([0.25-0.05*ri])])
	c=np.vstack([hstack([-65+15*np.power(re,2)]),hstack([-65*ml.ones((Ni,1))])])
	d=np.vstack([hstack([8-6*np.power(re,2)]),hstack([2*ml.ones((Ni,1))])])
	S=ml.zeros((Ne+Ni,Ne+Ni))
	v=-65*ml.ones((Ne+Ni,1))
	u=np.multiply(b,v)


	firings=np.matrix([])


	for i in range(1,segments):
		n = 12*i
		for ii in range(2,12):
			# connect each neuron to the next one in segment
			S[(n-ii)+2,(n-ii)+1] = 40
		# connect the mid neuron to the start of the next segment
		S[n+1,n-6] = 40
	# connect the last neuron  in the first to the first in the first segment
	# so that it fires cyclically 
	S[1,12] = 40
	   

	startI = 20
	I = ml.zeros((Ne+Ni,1))
	I[0] = startI

	
	############ physics & rendering setup ##############

    	pygame.init()
    	screen = pygame.display.set_mode((800, 600))
    	pygame.display.set_caption("LEECHSIM")
    	clock = pygame.time.Clock()

	space = pymunk.Space()
	space.gravity = (0.0, -100.0)

	shape = pymunk.Segment(space.static_body, (5, 100), (595,100), 1.0)
        shape.friction = 1.0
        space.add(shape)
	
    	worm_segs = []
    	draw_options = pymunk.pygame_util.DrawOptions(screen)
	lines = add_worm(space, worm_segs)
	counter = 0


    	while True:
        	for event in pygame.event.get():
            		if event.type == QUIT:
                		sys.exit(0)
            		elif event.type == KEYDOWN and event.key == K_ESCAPE:
                		sys.exit(0)

 		############### izhikevich #################
		fired=np.argwhere(v>=30)
		v[fired,0]=c[fired,0]
		u[fired,0]=u[fired,0]+d[fired,0]
		I=I+S[:,fired].sum()
		v=v+0.5*(0.04*np.power(v,2)+5*v+140-u+I)
		v=v+0.5*(0.04*np.power(v,2)+5*v+140-u+I)
		u=u+np.multiply(a,(np.multiply(b,v-u)))
		I = ml.zeros((Ne+Ni,1))


		########### leech #############
        	space.step(1/50.0)

        	screen.fill((255,255,255))
        	space.debug_draw(draw_options)
		for i in range(1,segments):
			'''
			print(v[(i*6)-3,0])
			if v[(i*6)-3,0] > 30:
				lengthL = 0
			else:
				lengthL = 30

			if v[(i*6)+3,0] > 30:
				lengthR = 0
			else:
				lengthR = 30

			worm_segs[i][2].rest_length = lengthL
			worm_segs[i][3].rest_length = lengthR
			'''
		
			#'''
			# sine oscillator for test
			length = math.sin((counter+10*i)*3.14159265/45)*20
			worm_segs[i][2].rest_length = length
			worm_segs[i][3].rest_length = -length
			#'''
		counter = counter + 1
        	pygame.display.flip()
        	clock.tick(50)

if __name__ == '__main__':
    	main()
