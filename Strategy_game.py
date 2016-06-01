#!/usr/bin/env python
import sys
import os
import math
import pygame
import random
import spritesheet
from pygame.locals import*
from itertools import repeat
#-----------------------------Constants-------------------------------
FPS = 60
WIDTH = 1200
HEIGHT = 700
#-------------------------------Classes-------------------------------
class Terrain(object):
	def __init__(self, name, sprite, traction = 0, evade = 0, phys = 0, nature = 0, aether = 0):
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
GRID_SQUARE_SIZE = 16
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
#-----------------------------------------Image Loading----------------------------------
terrain_sheet = spritesheet.spritesheet('Terrain_Tiles.png')
# Sprite is 16x16 pixels at location 0,0 in the file...
terrain = terrain_sheet.image_at((0, 0, 16, 16))
image2 = pygame.image.load('rogue.png').convert_alpha()
# Load two images into an array, their transparent bit is (255, 255, 255)
images = terrain_sheet.images_at(((0, 0, 16, 16),(17, 0, 16,16)), colorkey=(255, 255, 255))
#-------terrain images
base_size = 32
lava_sprite = terrain_sheet.image_at((0,base_size*4,32,32))
tree_sprite = terrain_sheet.image_at((base_size*7,base_size*6,32,32))
#-----------------------------------------------------------------------------------------
#------------------------------------Terrain Declarations---------------------------------
lava = Terrain("Lava", lava_sprite)
tree = Terrain("Tree", tree_sprite)
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
#print grid dimensionsk
print("width", grid_width)
print("height", grid_height)
#draw grid tiles with random colors
while (i < grid_width-1):
	while (j < grid_height-1):
		rand_terr = random.randint(0,1)
		#draw terrain for top left of each 2x2 square
		if (j%2 == 0 and i%2 == 0):
			if rand_terr == 0:
				terrain = lava
			else:
				terrain = tree
			mapSurface.blit(terrain.sprite, (i*16,j*16))	
		#assign same terrain to right square
		elif(i%2 == 1):
			terrain = grid[i-1][j].terrain
		#assign same terrain to lower squares
		else:
			terrain = grid[i][j-1].terrain
		grid[i][j].terrain = terrain
		j += 1
	i += 1
	j = 0
i = 0
#Draw map onto grid, grid onto screen
#Grid surface contains the area where the grid is visible, map surface contains entire grid
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
	#mapSurface contains grid, sprites should be blit to mapSurfaces
	#transparent sprites must be blit with BLEND_RGBA_MIN to achieve transparency
	mapSurface.blit(image2, (16,16), area=None, special_flags = BLEND_RGBA_MAX)
	gridSurface.blit(mapSurface, (x_offset[0],y_offset[0]))
	windowSurface.blit(gridSurface, (0,0))
	pygame.display.update()
	#----------------------------------------------tick the clock----------------------------------------
	mainClock.tick(FPS)
