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
#initialization of pygame, clock, screen shake
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WIDTH,HEIGHT),0,32)
mapSurface = pygame.Surface((WIDTH, HEIGHT))
gridSurface = pygame.Surface((WIDTH-150, HEIGHT-150))
GRID_SURFACE_WIDTH = WIDTH - 150
GRID_SURFACE_HEIGHT = HEIGHT - 150
screen_rect = windowSurface.get_rect()
pygame.display.set_caption('Strategy Garm')
#-----------------------------------------Image Loading----------------------------------
terrain_sheet = spritesheet.spritesheet('Terrain_Tiles.png')
# Sprite is 16x16 pixels at location 0,0 in the file...
terrain = terrain_sheet.image_at((0, 0, 16, 16))
image2 = pygame.image.load('rogue(1).png').convert_alpha()
# Load two images into an array, their transparent bit is (255, 255, 255)
images = terrain_sheet.images_at(((0, 0, 16, 16),(17, 0, 16,16)), colorkey=(255, 255, 255))
#-------terrain images
base_size = 32
lava_sprite = terrain_sheet.image_at((0,base_size*4,32,32))
tree_sprite = terrain_sheet.image_at((base_size*7,base_size*6,32,32))
#-----------------------------------------------------------------------------------------
#color declarations
#-------------------------------Classes-------------------------------
class Terrain(object):
	def __init__(self, name, sprite, traction = 0, evade = 0, phys = 0, nature = 0, energy = 0, phantasm = 0):
		self.name = name
		self.sprite = sprite
		self.traction = traction
		self.evade = evade
		self.phys = phys
		self.nature = nature
		self.energy = energy
		self.phantasm = phantasm

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

class Profession(object):
	def __init__(self, weight_class = "light", base_hp = 5, base_ep = 5, hp_growth = 1, ep_growth = 1, 
	base_weight = 1, base_atk = 1, base_def = 1, base_speed = 1, base_magic = 1, base_mdef = 1,
	atk_growth = 1, def_growth = 1, speed_growth = 1, magic_growth = 1, mdef_growth = 1):
		self.weight_class = weight_class
		self. base_hp = base_hp
		self.base_ep = base_ep
		self.hp_growth = hp_growth
		self.ep_growth = ep_growth
		self.base_weight = base_weight
		self.base_atk = base_atk
		self.base_def = base_def
		self.base_speed = base_speed
		self.base_magic = base_magic
		self.base_mdef = base_mdef
		self.atk_growth = atk_growth
		self.def_growth = def_growth
		self.speed_growth = speed_growth
		self.magic_growth = magic_growth
		self.mdef_growth = mdef_growth

default_prof = Profession()
class Unit(object):
	def __init__(self, sprite = image2, level = 1, grid_position = (0,0), hp = 10, max_hp = 10, ep = 10, max_ep = 10, profession = default_prof):
		self.sprite = sprite
		self.grid_position = grid_position
		self.level = level
		self.max_hp = max_hp
		self.max_ep = max_ep
		self.hp = hp
		self.ep = ep
		self.profession = profession
		self.x_pos = 0
		self.y_pos = 0
test_unit = Unit()
print(test_unit.profession.weight_class)
print(test_unit.x_pos)

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
def is_in(point, rect):
	if (point[0] < rect.left + rect.width) and (point[0] > rect.left):
		if (point[1] > rect.top and point[1] < rect.top + rect.height):
			return True
	return False

def draw_units(mapSurface, unit_list):
	for unit in unit_list:
		mapSurface.blit(unit.sprite, (unit.x_pos*16,unit.y_pos*16), area=None, special_flags = BLEND_RGBA_SUB)
#------------------------------------Terrain Declarations---------------------------------
lava = Terrain("Lava", lava_sprite)
tree = Terrain("Tree", tree_sprite)
#--------------------------------------------Initial Setup--------------------------------
GRID_SQUARE_SIZE = 16
#set up battle grid
grid_width = (WIDTH)/GRID_SQUARE_SIZE
if grid_width%2 == 1:
	grid_width = grid_width - 1
grid_height = (HEIGHT)/GRID_SQUARE_SIZE
if grid_height%2 == 1:
	grid_height = grid_height - 1

grid = []
for i in range(0, grid_width):
	x = []
	for j in range(0,grid_height):
		x.append(Tile(pygame.Rect(i*GRID_SQUARE_SIZE,j*GRID_SQUARE_SIZE, GRID_SQUARE_SIZE, GRID_SQUARE_SIZE), i, j,1,1, (0,0,0)))
	grid.append(x)


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
while (i < grid_width):
	while (j < grid_height):
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
friendly_units = []
friendly_units.append(test_unit)
while True:
#---------------------------------------------Player input----------------------------------------------
	for event in pygame.event.get():
		#Check for quit
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		#Get the mouse input
		if event.type == pygame.MOUSEBUTTONUP:
			pos = pygame.mouse.get_pos()
			mouse_x = pos[0]
			mouse_y = pos[1]
			#check if the mouse is in the grid window
			if (mouse_x < GRID_SURFACE_WIDTH and mouse_y < GRID_SURFACE_HEIGHT):
				print(pygame.mouse.get_pos())
				actual_x = mouse_x - x_offset[0]
				actual_y = mouse_y - y_offset[0]
				actuals = (actual_x, actual_y)
				grid_space = (actual_x/16, actual_y/16)
				print(actual_x, actual_y)
				print(grid_space)
				print(is_in(pygame.mouse.get_pos(), gridSurface.get_rect()))
				if (grid_space[0] < grid_width and grid_space[1] < grid_height):
					print(grid[grid_space[0]][grid_space[1]].terrain.name)
	#get array of keypresses
	keys = pygame.key.get_pressed()
	#Variable to determine if background needs updating
	update_needed = False
	#Check for input to determine map scrolling
	update_needed = scroll_map(keys, grid, update_needed, x_offset, y_offset)
	#fill window background white
	#fill original screen black (in case of screen shake)
	#---------------------------------------------update the display-----------------------------------
	if update_needed:
		windowSurface.fill(WHITE)
		gridSurface.fill(WHITE)
	#mapSurface contains grid, sprites should be blit to mapSurfaces
	#transparent sprites must be blit with BLEND_RGBA_MIN to achieve transparency
	#Drawing a sprite to the "map" surface
	draw_units(mapSurface,friendly_units)
	#drawing the map surface to the grid window (the area in the upper left)
	gridSurface.blit(mapSurface, (x_offset[0],y_offset[0]))
	#Drawing the grid window to the entire window
	windowSurface.blit(gridSurface, (0,0))
	#update the display
	pygame.display.update()
	#----------------------------------------------tick the clock----------------------------------------
	mainClock.tick(FPS)
