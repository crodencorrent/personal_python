#!/usr/bin/env python
import sys
import os
import math
import pygame
import random
from pygame.locals import*
from itertools import repeat
#-----------------------------Constants-------------------------------
FPS = 60
WIDTH = 1200
HEIGHT = 700
#-------------------------------Classes-------------------------------
class Terrain(object):
	def __init__(self, name, sprite, traction, evade, phys, nature, aether):
		self.name = name
		self.sprite = sprite
		self.traction = traction
		self.evade = evade
		self.phys = phys
		self.nature = nature
		self.aether = aether

class Tile(object):
	def __init__(self, rect, x_pos, y_pos, is_occupied, is_passable, terrain):
		self.rect = rect
		self.x_pos = x_pos
		self.y_pos = y_pos
		self.is_occupied = is_occupied
		self.is_passable = is_passable
		self.terrain = terrain
class Battle_Grid(object):
	def __init__(self, grid, width, height):
		self.grid = grid
		self.width = width
		self.height = height
#------------------------------Functions------------------------------
def scroll_map(keys, grid, update_needed, x_offset, y_offset):
	if (keys[pygame.K_LEFT]):
		x_offset[0] -= 3
		update_needed = True
	if (keys[pygame.K_RIGHT]):
		x_offset[0] += 3
		update_needed = True
	if (keys[pygame.K_UP]):
		y_offset[0] -= 3
		update_needed = True
	if (keys[pygame.K_DOWN]):
		y_offset[0] += 3
		update_needed = True
	return update_needed

#--------------------------------------------Initial Setup--------------------------------
GRID_SQUARE_SIZE = 10
#set up battle grid
grid_width = (WIDTH)/GRID_SQUARE_SIZE
grid_height = (HEIGHT)/GRID_SQUARE_SIZE
grid = []
for i in range(0, grid_width):
	x = []
	for j in range(0,grid_height):
		x.append(Tile(pygame.Rect(i*GRID_SQUARE_SIZE,j*GRID_SQUARE_SIZE, GRID_SQUARE_SIZE, GRID_SQUARE_SIZE), i, j,1,1, (0,0,0)))
	grid.append(x)

#initialization of pygame, clock, screen shake
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WIDTH,HEIGHT),0,32)
mapSurface = pygame.Surface((WIDTH, HEIGHT))
gridSurface = pygame.Surface((WIDTH-150, HEIGHT-150))
screen_rect = windowSurface.get_rect()
pygame.display.set_caption('Strategy Garm')
#color declarations
BLACK = (0,0,0)
WHITE = (255, 255, 255)
MYSTERY = (200, 100, 50)
GREEN = (0,255,0)
BLUE = (0, 0, 255)
RED = (255, 0 , 0)
#font setup
basicFont = pygame.font.SysFont(None, 48)
#text setup
windowSurface.fill(WHITE)
mapSurface.fill(WHITE)
i = 0
j = 0
#print grid dimensions
print("width", grid_width)
print("height", grid_height)
#draw grid tiles with random colors
while (i < grid_width-1):
	while (j < grid_height-1):
		rand_color = random.randint(0,2)
		if rand_color == 0:
			color = GREEN
		elif rand_color == 1:
			color = BLUE
		else:
			color = RED
		pygame.draw.rect(mapSurface, color, grid[i][j])
		grid[i][j].terrain = color
		j += 1
	i += 1
	j = 0
i = 0
gridSurface.blit(mapSurface, (0,0))
windowSurface.blit(gridSurface, (0,0))
pygame.display.update()
#----------------------------------------------Game Loop-----------------------------------------------
x_offset = [0]
y_offset = [0]
while True:
	for event in pygame.event.get():
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
	keys = pygame.key.get_pressed()
	#Variable to determine if background needs updating
	update_needed = False
	#Check for input to determine map scrolling
	update_needed = scroll_map(keys, grid, update_needed, x_offset, y_offset)
	#fill window background white
	#fill original screen black (in case of screen shake)
	#---------------------------------------------update the display-----------------------------------
	i = 0
	j = 0
	if update_needed:
		windowSurface.fill(WHITE)
		gridSurface.fill(WHITE)
	gridSurface.blit(mapSurface, (x_offset[0],y_offset[0]))
	windowSurface.blit(gridSurface, (0,0))
	pygame.display.update()
	#----------------------------------------------tick the clock----------------------------------------
	mainClock.tick(FPS)
