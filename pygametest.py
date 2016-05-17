#!/usr/bin/env python
import sys
import os
import math
import pygame
import random
from pygame.locals import*
from itertools import repeat
#-----------------------------Constants-------------------------------
FPS = 40
WIDTH = 800
HEIGHT = 400
#-------------------------------Classes-------------------------------
class Player(object):
	def __init__(self, player_rect, xspeed, yspeed, weapons):
		self.player_rect = player_rect
		self.xspeed = xspeed
		self.yspeed = yspeed
		self.weapons = weapons
	def change_speed(self, xdifference, ydifference):
		self.xspeed += xdifference
		self.yspeed += ydifference
	def move_player(self):
		self.player_rect = self.player_rect.move(player.xspeed, player.yspeed)
	def check_bounds(self):
		if (self.player_rect.right > WIDTH):
			self.xspeed = -self.xspeed/2
			self.player_rect.right = WIDTH
		if (self.player_rect.left < 0):
			self.xspeed = -self.xspeed/2
			self.player_rect.left = 0
		if (self.player_rect.top < 0):
			self.yspeed = -self.yspeed/2
			self.player_rect.top = 0
		if (self.player_rect.bottom > HEIGHT):
			self.yspeed = -self.yspeed/2
			self.player_rect.bottom = HEIGHT
	def check_speed(self):
		if (self.xspeed > 12):
			self.xspeed = 12
		elif (self.xspeed < -12):
			self.xspeed = -12
		if (self.yspeed > 12):
			self.yspeed = 12
		elif (self.yspeed < -12):
			self.yspeed = -12
def get_player_movement_input(player_object, keys):
	if (keys[pygame.K_LEFT] and player_object.xspeed > 0):
		player.xspeed = -1
	elif (keys[pygame.K_LEFT]):
		player.xspeed -= 1
	elif (keys[pygame.K_RIGHT] and player_object.xspeed < 0):
		player.xspeed = 1
	elif keys[pygame.K_RIGHT]:
		player.xspeed += 1
	else:
		player.xspeed = 0
	if keys[pygame.K_UP]:
		player.yspeed += -1
	elif keys[pygame.K_DOWN]:
		player.yspeed += 1
	else:
		player.yspeed = 0
#class for hostile blocks
class Block(object):
	def __init__(self, rect, xspeed, yspeed):
		self.rect = rect
		self.xspeed = xspeed
		self.yspeed = yspeed
	#move blocks based on velocity
	def move_block(self):
		self.rect = self.rect.move(self.xspeed, self.yspeed)
	#check if the block is on the screen, bounces when it hits an edge
	def check_bounds(self):
		if (self.rect.right > WIDTH):
			self.xspeed = -self.xspeed/2
			self.rect.right = WIDTH
		if (self.rect.left < 0):
			self.xspeed = -self.xspeed/2
			self.rect.left = 0
		if (self.rect.top < 0):
			self.yspeed = -self.yspeed/2
			self.rect.top = 0
		if (self.rect.bottom > HEIGHT):
			self.yspeed = -self.yspeed/2
			self.rect.bottom = HEIGHT
#class keeping track of projectiles
class Projectile(object):
	def __init__(self, original_rect, rect, xspeed, yspeed, distance, requires_scaling, started_scaling, scaling, scale_generator):
		self.original_rect = original_rect
		self.rect = rect
		self.xspeed = xspeed
		self.yspeed = yspeed
		self.distance = distance
		self.requires_scaling = requires_scaling
		self.started_scaling = started_scaling
		self.scaling = scaling
		self.scale_generator = scale_generator
	#move the projectile's rect based on its speed
	def move_projectile(self):
		self.rect = self.rect.move(self.xspeed, self.yspeed)
	#check if the projectile
	def check_bounds(self):
		if (self.rect.right > WIDTH):
			self.xspeed = -self.xspeed/2
			self.rect.right = WIDTH
		if (self.rect.left < 0):
			self.xspeed = -self.xspeed/2
			self.rect.left = 0
		if (self.rect.top < 0):
			self.yspeed = -self.yspeed/2
			self.rect.top = 0
		if (self.rect.bottom > HEIGHT):
			self.yspeed = -self.yspeed/2
			self.rect.bottom = HEIGHT
	#NEEDS CHANGING - a generator to create scaling values for the projectile
	def scale_box(self):
		for x in range(0, 20):
			yield (8)
		while True:
			yield (0)
#class for weapons for the player
class Weapon(object):
	def __init__(self, fire_rate, initial_x_velocity, initial_y_velocity, initial_length, initial_height, projectile_distance, scaling_required, current_fire_delay, is_inverted = 0):
		self.fire_rate = fire_rate
		self.initial_x_velocity = initial_x_velocity
		self.initial_y_velocity = initial_y_velocity
		self.initial_height = initial_height
		self.initial_length = initial_length
		self.projectile_distance = projectile_distance
		self.scaling_required = scaling_required
		self.current_fire_delay = current_fire_delay
# Weapons name              fr   xsp   ysp   len  hght   dist   scale_req curr delay
flamethrower =        Weapon(2,   10,    0,    2,   10,   100,     1,         0)
gorp_launcher =       Weapon(20,  10,   10,    20,   5,   400,     0,         0)
#--------------------------------------------Functions-----------------------------------
#see if a "block" is outside the screen, remove it from list if it is
def check_for_outside(block_list):
	i = 0
	rem_list = []
	new_list = []
	for block in block_list:
		if (block.rect.right > WIDTH):
			block.xspeed = -block.xspeed/2
			block.rect.right = WIDTH
			rem_list.append(block)
		elif (block.rect.left < 0):
			block.xspeed = -block.xspeed/2
			block.rect.left = 0
			rem_list.append(block)
		elif (block.rect.top < 0):
			block.yspeed = -block.yspeed/2
			block.rect.top = 0
			rem_list.append(block)
		elif (block.rect.bottom > HEIGHT):
			rem_list.append(block)
		else:
			new_list.append(block)
	return new_list
#check to see if a projectile in a list has reached its maximum distance, delete it if it has
def check_for_outdistance(projectile_list):
	i = 0
	rem_list = []
	new_list = []
	for projectile in projectile_list:
		current_placement = projectile.rect.x + projectile.rect.y
		original_position = projectile.original_rect.x + projectile.original_rect.y
		difference = abs(current_placement - original_position)
		if (difference > projectile.distance):
			rem_list.append(projectile)
		else:
			new_list.append(projectile)
	return new_list
#a generator that yields values for screen shake
def screen_shake():
	s = -1
	for _ in xrange(0, 3):
		for x in range(0, 15, 5):
			yield (x*s, (-x*s)/2)
		for x in range(15, 0, 5):
			yield (x*s, (x*s)/2)
		s *= -1
	while True:
		yield (0, 0)
#create blocks from the 4 corners of the screen with semi-random velocities
def create_blocks(blocks):
	if len(blocks) < 4:
		randcorner = random.randint(1,4)
		print(randcorner)
		sz = random.randint(10,50)
		if randcorner == 1:
			x = 0
			y = 0
			xsp = random.randint(5,10)
			ysp = random.randint(5,10)
		elif randcorner == 2:
			x = 0
			y = HEIGHT - sz
			xsp = random.randint(5,10)
			ysp = random.randint(-10,-5)
		elif randcorner == 3:
			x = WIDTH - sz
			y = HEIGHT - sz
			xsp = random.randint(-10,-5)
			ysp = random.randint(-10,-5)
		elif randcorner == 4:
			x = WIDTH - sz
			y = 0
			xsp = random.randint(-10,-5)
			ysp = random.randint(5,10)
		blocks.append(Block(pygame.Rect(x, y, sz, sz), xsp, ysp))
#checks for input of fire button, fires all weapons not on cooldown
def fire_weapons(player, keys):
	if (keys[pygame.K_SPACE]):
		#if there is no fire delay in effect, fire the next projectile
		for weapon in player.weapons:
			if weapon.current_fire_delay == 0:
				projectile_height = weapon.initial_height
				projectile_length = weapon.initial_length
				projectile_xspeed = weapon.initial_x_velocity
				projectile_yspeed = weapon.initial_y_velocity
				projectile_requires_scaling = weapon.scaling_required
				projectile_distance = weapon.projectile_distance
				initial_rect = Rect(player.player_rect.right, player.player_rect.centery-projectile_height/2, projectile_length, projectile_height)
				useable_rect = Rect(player.player_rect.right, player.player_rect.centery-projectile_height/2, projectile_length, projectile_height)
				new_projectile = Projectile(initial_rect, useable_rect, projectile_xspeed, projectile_yspeed, projectile_distance, projectile_requires_scaling, 0, 10, -1)
				active_projectiles_friendly.append(new_projectile)
				weapon.current_fire_delay = weapon.fire_rate
#initialization of pygame, clock, screen shake
#--------------------------------------------Initial Setup--------------------------------
pygame.init()
mainClock = pygame.time.Clock()
shake = repeat((0, 0))
#window setup
org_screen = pygame.display.set_mode((WIDTH,HEIGHT),0,32)
windowSurface = org_screen.copy()
screen_rect = windowSurface.get_rect()
pygame.display.set_caption('Hello world!')
#color declarations
BLACK = (0,0,0)
WHITE = (255, 255, 255)
MYSTERY = (200, 100, 50)
GREEN = (0,255,0)
#font setup
basicFont = pygame.font.SysFont(None, 48)
#text setup
#player setup
player_rect = pygame.Rect(WIDTH/2, HEIGHT/2, 50,50)
player = Player(player_rect, 0, 0, [flamethrower, gorp_launcher])
#block setup
block1_rect = pygame.Rect(100, 100, 20, 20)
block1 = Block(block1_rect, 5, 3)
block2_rect = pygame.Rect(50, 50, 30, 30)
block2 = Block(block2_rect, 6, -4)
blocks = [block1,block2]
#projectile list
active_projectiles_friendly = []
#draw white background
windowSurface.fill(WHITE)
pygame.draw.rect(windowSurface, GREEN, player.player_rect)
#draw text to surface
#draw window to screen
pygame.display.update()
fire_delay = 0
#game loop
while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	#if less than 4 blocks, add more
	create_blocks(blocks)
	#get list of keys pressed
	keys = pygame.key.get_pressed()
	#check the keys pressed, act accordingly
	get_player_movement_input(player, keys)
	#if the key is space, fire projectiles, add them to the list of active projectiles
	fire_weapons(player, keys)
	#move player, check bounds
	player.check_speed()
	player.move_player()
	#hold player on screen (possibly replace with check bounds method)
	player.player_rect.clamp_ip(screen_rect) 
	#move blocks, check bounds
	for block in blocks:
		block.move_block()
	#check through players projectiles
	for projectile in active_projectiles_friendly:
		#move them, if they haven't outlived their distance
		projectile.move_projectile()
		#scale them
		#if they haven't begun scaling, create their scaling generator
		if (projectile.requires_scaling == 1 and projectile.started_scaling == 0):
			projectile.scale_generator = projectile.scale_box()
			projectile.started_scaling = 1
		#if they have begun scaling, scale their height and make sure their center remains correct
		elif (projectile.requires_scaling == 1 and projectile.started_scaling == 1):
			offset_project = projectile.scale_generator.next()
			projectile.rect.height += offset_project
			projectile.rect.centery = projectile.original_rect.centery
	blocks = check_for_outside(blocks)
	active_projectiles_friendly = check_for_outdistance(active_projectiles_friendly)
	windowSurface.fill(WHITE)
	#check collision between player and blocks
	check = player.player_rect.collidelist(blocks)
	if (check != -1):
		print("collision!")
		blocks.pop(check)
		shake = screen_shake()
	#check collision between friendly projectiles and blocks
	for projectile in active_projectiles_friendly:
		check = projectile.rect.collidelist(blocks)
		if (check != -1):
			print("collision of projectile!")
			blocks.pop(check)
			shake = screen_shake()
	#draw shit to the screen
	org_screen.fill((0, 0, 0))
	pygame.draw.rect(windowSurface, GREEN, player.player_rect)
	for block in blocks:
		pygame.draw.rect(windowSurface, MYSTERY, block.rect)
	for projectile in active_projectiles_friendly:
		pygame.draw.rect(windowSurface, BLACK, projectile.rect)
	org_screen.blit(windowSurface, next(shake))
	#update the display
	pygame.display.update()
	#reduce counters
	for weapon in player.weapons:
		if weapon.current_fire_delay > 0:
			weapon.current_fire_delay -= 1
	#tick the clock
	mainClock.tick(FPS)