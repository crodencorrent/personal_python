#!/usr/bin/env python
import sys
import os
import math
import pygame
import random
import spritesheet
import Queue
from pygame.locals import*
from itertools import repeat
#-----------------------------Constants-------------------------------
FPS = 30
WIDTH = 1200
HEIGHT = 700
#initialization of pygame, clock, screen shake
pygame.init()
mainClock = pygame.time.Clock()
windowSurface = pygame.display.set_mode((WIDTH,HEIGHT),0,32)
mapWindow = pygame.Surface((WIDTH, HEIGHT))
gridSurface = pygame.Surface((WIDTH-150, HEIGHT-150))
GRID_SURFACE_WIDTH = WIDTH - 150
GRID_SURFACE_HEIGHT = HEIGHT - 150
screen_rect = windowSurface.get_rect()
pygame.display.set_caption('Strategy Garm')
#-----------------------------------------Image Loading----------------------------------
terrain_sheet = spritesheet.spritesheet('Terrain_Tiles.png')
move_animation_sheet = spritesheet.spritesheet('move_rect_animation.bmp.png')
attack_animation_sheet = spritesheet.spritesheet('attack_rect_animation.png')
unit_sheet = spritesheet.spritesheet('units_red.png')
count = 0
move_anims = []
while count < 8:
	new_anim = move_animation_sheet.image_at((count*32, 0, 32, 32))
	new_anim = pygame.transform.smoothscale(new_anim, (16,16))
	move_anims.append(new_anim)
	count += 1
count = 0
attack_anims = []
while count < 8:
	new_anim = attack_animation_sheet.image_at((count*32, 0, 32, 32))
	new_anim = pygame.transform.smoothscale(new_anim, (16,16))
	attack_anims.append(new_anim)
	count += 1
# Sprite is 16x16 pixels at location 0,0 in the file...
terrain = terrain_sheet.image_at((0, 0, 16, 16))
image2 = pygame.image.load('rogue(1).png').convert_alpha()
image2.set_alpha(0)
print(image2.get_alpha())
image2 = unit_sheet.image_at((0,0,32,32), colorkey = (255,255,255))
# Load two images into an array, their transparent bit is (255, 255, 255)
images = terrain_sheet.images_at(((0, 0, 16, 16),(17, 0, 16,16)), colorkey=(255, 255, 255))
#-------terrain images
base_size = 32
lava_sprite = terrain_sheet.image_at((0,base_size*4,32,32))
tree_sprite = terrain_sheet.image_at((base_size*7,base_size*6,32,32))
#-----------------------------------------------------------------------------------------
#color declarations
#-------------------------------Classes-------------------------------
class CurrentInfo(object):
	def __init__(self, currently_selected_unit = None, selected_space = None, selected_target = None):
		self.currently_selected_unit = currently_selected_unit
		self.selected_space = selected_space
		self.selected_target = selected_target
current_info = CurrentInfo()
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
		self.is_moveable = True
		self.is_move_highlighted = False
		self.is_attack_highlighted = False
		self.terrain = terrain
		self.unit = None
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
	def __init__(self, sprite = image2, level = 1, hp = 10, max_hp = 10, ep = 10, max_ep = 10, profession = default_prof, skill_list = [],
		atk = 10, defn = 10, speed = 10, magic = 10, mdef = 10):
		self.sprite = sprite
		self.x_pos = 10
		self.y_pos = 10
		self.level = level
		self.max_hp = max_hp
		self.max_ep = max_ep
		self.hp = hp
		self.ep = ep
		self.atk = atk
		self.defn = defn
		self.speed = speed
		self.magic = magic
		self.mdef = mdef
		self.profession = profession
		self.move_range = 5
		self.is_move_selected = False
		self.is_attack_selected = False
		self.skill_list = skill_list
		self.is_friendly = True
		self.attack_range = 1
		self.all_occupied = []
		self.is_move_selected = False
		self.is_attack_selected = False
	def move(self, grid, x_pos, y_pos):
		#unoccupy old squares
		grid[self.x_pos][self.y_pos].is_occupied = False
		grid[self.x_pos +1][self.y_pos].is_occupied = False
		grid[self.x_pos][self.y_pos+1].is_occupied = False
		grid[self.x_pos+1][self.y_pos+1].is_occupied = False
		grid[self.x_pos][self.y_pos].unit = None
		grid[self.x_pos +1][self.y_pos].unit = None
		grid[self.x_pos][self.y_pos+1].unit = None
		grid[self.x_pos+1][self.y_pos+1].unit = None
		self.all_occupied = []
		#change location
		self.x_pos = x_pos
		self.y_pos = y_pos
		#occupy new squares
		grid[x_pos][y_pos].is_occupied = True
		grid[x_pos +1][y_pos].is_occupied = True
		grid[x_pos][y_pos+1].is_occupied = True
		grid[x_pos+1][y_pos+1].is_occupied = True
		grid[x_pos][y_pos].unit = unit
		grid[x_pos +1][y_pos].unit = unit
		grid[x_pos][y_pos+1].unit = unit
		grid[x_pos+1][y_pos+1].unit =unit
		self.find_all_occupied(grid)
		for tile in self.all_occupied:
			print(tile.x_pos, tile.y_pos)

	def find_all_occupied(self, grid):
		self.all_occupied.append(grid[self.x_pos][self.y_pos])
		self.all_occupied.append(grid[self.x_pos+1][self.y_pos])
		self.all_occupied.append(grid[self.x_pos][self.y_pos+1])
		self.all_occupied.append(grid[self.x_pos+1][self.y_pos+1])
		x_pos = self.x_pos
		y_pos = self.y_pos
		grid[x_pos][y_pos].is_occupied = True
		grid[x_pos +1][y_pos].is_occupied = True
		grid[x_pos][y_pos+1].is_occupied = True
		grid[x_pos+1][y_pos+1].is_occupied = True
		grid[x_pos][y_pos].unit = self
		grid[x_pos +1][y_pos].unit = self
		grid[x_pos][y_pos+1].unit = self
		grid[x_pos+1][y_pos+1].unit = self

	def find_min_distance(self, point):
		minimum_distance = 100000
		for tile in self.all_occupied:
			minimum_distance = min(find_distance((tile.x_pos, tile.y_pos), point), minimum_distance)
		return minimum_distance
	def find_move_range(self, grid, current_square):
		Q = Queue.Queue()
		Q.put(current_square)
		while (not Q.empty()):
			current = Q.get()
			right = (current[0]+1, current[1])
			up = (current[0], current[1]+1)
			left = (current[0]-1, current[1])
			down =  (current[0], current[1]-1)
			#check if right is already highlighted
			if(not grid[right[0]][right[1]].is_move_highlighted):
				distance = self.find_min_distance(right)
				#check if right is in the move_range
				if (distance <= self.move_range):
					#highlight right and put in Queue
					grid[current[0]+1][current[1]].is_move_highlighted = True
					Q.put(right)
			#check if up is already highlighted
			if(not grid[up[0]][up[1]].is_move_highlighted):
				distance = self.find_min_distance(up)
				#check if up is in the move_range
				if (distance <= self.move_range):
					#highlight up and put in Queue
					grid[current[0]][current[1]+1].is_move_highlighted = True
					Q.put(up)
			#check if left is already highlighted
			if(not grid[left[0]][left[1]].is_move_highlighted):
				distance = self.find_min_distance(left)
				#check if left is in the move_range
				if (distance <= self.move_range):
					#highlight left and put in Queue
					grid[current[0]-1][current[1]].is_move_highlighted = True
					Q.put(left)
			if(not grid[down[0]][down[1]].is_move_highlighted):
				distance = self.find_min_distance(down)
				#check if down is in the move_range
				if (distance<= self.move_range):
					#highlight down and put in Queue
					grid[current[0]][current[1]-1].is_move_highlighted = True
					Q.put(down)
	def find_attack_range(self, grid, current_square):
		Q = Queue.Queue()
		Q.put(current_square)
		while (not Q.empty()):
			current = Q.get()
			right = (current[0]+1, current[1])
			up = (current[0], current[1]+1)
			left = (current[0]-1, current[1])
			down =  (current[0], current[1]-1)
			#check if right is already highlighted
			if(not grid[right[0]][right[1]].is_attack_highlighted):
				distance = self.find_min_distance(right)
				#check if right is in the attack_range
				if (distance <= self.attack_range):
					#highlight right and put in Queue
					grid[current[0]+1][current[1]].is_attack_highlighted = True
					Q.put(right)
			#check if up is already highlighted
			if(not grid[up[0]][up[1]].is_attack_highlighted):
				distance = self.find_min_distance(up)
				#check if up is in the attack_range
				if (distance <= self.attack_range):
					#highlight up and put in Queue
					grid[current[0]][current[1]+1].is_attack_highlighted = True
					Q.put(up)
			#check if left is already highlighted
			if(not grid[left[0]][left[1]].is_attack_highlighted):
				distance = self.find_min_distance(left)
				#check if left is in the attack_range
				if (distance <= self.attack_range):
					#highlight left and put in Queue
					grid[current[0]-1][current[1]].is_attack_highlighted = True
					Q.put(left)
			if(not grid[down[0]][down[1]].is_attack_highlighted):
				distance = self.find_min_distance(down)
				#check if down is in the attack_range
				if (distance<= self.attack_range):
					#highlight down and put in Queue
					grid[current[0]][current[1]-1].is_attack_highlighted = True
					Q.put(down)
	def unfind_move_range(self, grid, current_square):
			Q = Queue.Queue()
			Q.put(current_square)
			while (not Q.empty()):
				current = Q.get()
				right = (current[0]+1, current[1])
				up = (current[0], current[1]+1)
				left = (current[0]-1, current[1])
				down =  (current[0], current[1]-1)
				#check if right is already highlighted
				if(grid[right[0]][right[1]].is_move_highlighted):
					distance = self.find_min_distance(right)
					#check if right is in the move_range
					if (distance <= self.move_range):
						#highlight right and put in Queue
						grid[current[0]+1][current[1]].is_move_highlighted = False
						Q.put(right)
				#check if up is already highlighted
				if(grid[up[0]][up[1]].is_move_highlighted):
					distance = self.find_min_distance(up)
					#check if up is in the move_range
					if (distance <= self.move_range):
						#highlight up and put in Queue
						grid[current[0]][current[1]+1].is_move_highlighted = False
						Q.put(up)
				#check if left is already highlighted
				if(grid[left[0]][left[1]].is_move_highlighted):
					distance = self.find_min_distance(left)
					#check if left is in the move_range
					if (distance <= self.move_range):
						#highlight left and put in Queue
						grid[current[0]-1][current[1]].is_move_highlighted = False
						Q.put(left)
				if(grid[down[0]][down[1]].is_move_highlighted):
					distance = self.find_min_distance(right)
					#check if down is in the move_range
					if (distance <= self.move_range):
						#highlight down and put in Queue
						grid[current[0]][current[1]-1].is_move_highlighted = False
						Q.put(down)

	def unfind_attack_range(self, grid, current_square):
			Q = Queue.Queue()
			Q.put(current_square)
			while (not Q.empty()):
				current = Q.get()
				right = (current[0]+1, current[1])
				up = (current[0], current[1]+1)
				left = (current[0]-1, current[1])
				down =  (current[0], current[1]-1)
				#check if right is already highlighted
				if(grid[right[0]][right[1]].is_attack_highlighted):
					distance = self.find_min_distance(right)
					#check if right is in the attack_range
					if (distance <= self.attack_range):
						#highlight right and put in Queue
						grid[current[0]+1][current[1]].is_attack_highlighted = False
						Q.put(right)
				#check if up is already highlighted
				if(grid[up[0]][up[1]].is_attack_highlighted):
					distance = self.find_min_distance(up)
					#check if up is in the attack_range
					if (distance <= self.attack_range):
						#highlight up and put in Queue
						grid[current[0]][current[1]+1].is_attack_highlighted = False
						Q.put(up)
				#check if left is already highlighted
				if(grid[left[0]][left[1]].is_attack_highlighted):
					distance = self.find_min_distance(left)
					#check if left is in the attack_range
					if (distance <= self.attack_range):
						#highlight left and put in Queue
						grid[current[0]-1][current[1]].is_attack_highlighted = False
						Q.put(left)
				if(grid[down[0]][down[1]].is_attack_highlighted):
					distance = self.find_min_distance(right)
					#check if down is in the attack_range
					if (distance <= self.attack_range):
						#highlight down and put in Queue
						grid[current[0]][current[1]-1].is_attack_highlighted = False
						Q.put(down)

	def perform_targeted_attack(self, target_unit, skill):
		print(target_unit.hp)
		target_unit.hp -= self.profession.base_atk * skill.power_mult
		print(target_unit.hp)



class Skill(object):
	def __init__(self, name = "Skill", is_passive = False, energy_cost = 0, turn_time = 1, power_mult = 1, aoe = 0, statuses = [], 
	description = "", targets_friendly = False):
		self.name = name
		self.is_passive = is_passive
		self.energy_cost = energy_cost
		self.turn_time = turn_time
		self. power_mult = power_mult
		self.aoe = aoe
		self.statuses = statuses
		self.description = description
		self.targets_friendly = targets_friendly

default_skill = Skill()
test_unit = Unit()
test_unit.skill_list.append(default_skill)
test_unit.is_move_selected = True
test_unit.is_friendly = True
test_unit2 = Unit()
test_unit2.x_pos = 4
test_unit2.y_pos = 4
print(test_unit.profession.weight_class)
print(test_unit.x_pos)
#------------------------------Functions------------------------------
def scroll_map(keys, grid, update_needed, x_offset, y_offset):
	scroll_speed = 6
	if (keys[pygame.K_LEFT]):
		x_offset[0] -= scroll_speed
		update_needed = True
	if (keys[pygame.K_RIGHT]):
		x_offset[0] += scroll_speed
		update_needed = True
	if (keys[pygame.K_UP]):
		y_offset[0] -= scroll_speed
		update_needed = True
	if (keys[pygame.K_DOWN]):
		y_offset[0] += scroll_speed
		update_needed = True
	return update_needed
def is_in(point, rect):
	if (point[0] < rect.left + rect.width) and (point[0] > rect.left):
		if (point[1] > rect.top and point[1] < rect.top + rect.height):
			return True
	return False

def draw_units(mapWindow, unit_list):
	for unit in unit_list:
		mapWindow.blit(unit.sprite, (unit.x_pos*16,unit.y_pos*16), area=None, special_flags = BLEND_RGBA_ADD)

def draw_animation(grid, surface, animation_list, anim_count):
	for x_index, row in enumerate(grid):
		for y_index, tile in enumerate(row):
			if (y_index%2 == 0 and x_index%2 == 0):
				surface.blit(tile.terrain.sprite, (x_index*16,y_index*16))	
			if tile.is_move_highlighted:
				surface.blit(move_anims[anim_count%len(move_anims)], Rect(tile.x_pos*16, tile.y_pos*16, 16, 16), area = None, special_flags = BLEND_RGBA_ADD)
			elif tile.is_attack_highlighted:
				surface.blit(attack_anims[anim_count%len(move_anims)], Rect(tile.x_pos*16, tile.y_pos*16, 16, 16), area = None, special_flags = BLEND_RGBA_ADD)

def check_occupation(grid, tile, unit):
	tiles = []
	x_pos = tile.x_pos
	y_pos = tile.y_pos
	tiles.append(tile)
	tiles.append(grid[x_pos+1][y_pos])
	tiles.append(grid[x_pos][y_pos+1])
	tiles.append(grid[x_pos+1][y_pos+1])
	for tile in tiles:
		if tile.is_occupied:
			if tile.unit is not unit:
				return True
	return False

def find_distance(point1, point2):
	return (abs(point1[0] - point2[0]) + abs(point1[1] - point2[1]))

def will_fit(grid, x_pos, y_pos):
	will_fit = False
	selected = grid[x_pos][y_pos].is_move_highlighted
	right = grid[x_pos+1][y_pos].is_move_highlighted
	down = grid[x_pos][y_pos+1].is_move_highlighted
	diag = grid[x_pos+1][y_pos+1].is_move_highlighted
	if (selected and right and down and diag):
		will_fit = True
	return will_fit

def determine_mode(currently_selected_unit,keys,grid):
	if currently_selected_unit is not None:
			#if the a key is pressed, and the unit is not already attack selected
			if (keys[pygame.K_a] and currently_selected_unit.is_attack_selected == False):
				#the unit is now attack selected
				currently_selected_unit.is_attack_selected = True
				#if move selected, remove the current move range
				if currently_selected_unit.is_move_selected == True:
					print("unfinding move range")
					currently_selected_unit.unfind_move_range(grid, (currently_selected_unit.x_pos, currently_selected_unit.y_pos))
				#find the new attack range
				currently_selected_unit.find_attack_range(grid, (currently_selected_unit.x_pos, currently_selected_unit.y_pos))
				#set the move_selection to false
				currently_selected_unit.is_move_selected = False
				print("finding attack range")
			#otherwise, if the m key is pressed and the unit is not already move selected
			elif (keys[pygame.K_m] and currently_selected_unit.is_move_selected == False):
				if currently_selected_unit.is_attack_selected == True:
					print("unfinding move range")
					currently_selected_unit.unfind_attack_range(grid, (currently_selected_unit.x_pos, currently_selected_unit.y_pos))
				currently_selected_unit.is_attack_selected = False
				currently_selected_unit.is_move_selected = True
				currently_selected_unit.find_move_range(grid, (currently_selected_unit.x_pos, currently_selected_unit.y_pos))
def cancel_selection(currently_selected_unit, selected_space, grid):
	if ((currently_selected_unit is not None) and not (selected_space.is_move_highlighted)):
		if currently_selected_unit.is_move_selected:
			currently_selected_unit.unfind_move_range(grid, (currently_selected_unit.x_pos, currently_selected_unit.y_pos))
			currently_selected_unit.is_move_selected = False
		elif currently_selected_unit.is_attack_selected:
			currently_selected_unit.unfind_attack_range(grid, (currently_selected_unit.x_pos, currently_selected_unit.y_pos))
			currently_selected_unit.is_attack_selected = False
		currently_selected_unit = None
		return currently_selected_unit

def perform_move(currently_selected_unit, grid, selected_space):
	currently_selected_unit.unfind_move_range(grid, (currently_selected_unit.x_pos, currently_selected_unit.y_pos))
	distance = abs(currently_selected_unit.x_pos - selected_space.x_pos) + abs(currently_selected_unit.y_pos - selected_space.y_pos)
	currently_selected_unit.move(grid, selected_space.x_pos, selected_space.y_pos)
	print("current coordinates =", currently_selected_unit.x_pos, currently_selected_unit.y_pos)
	currently_selected_unit.move_range -= distance
	currently_selected_unit.find_move_range(grid, (currently_selected_unit.x_pos, currently_selected_unit.y_pos))

def find_appropriate_range(currently_selected_unit, grid):
	if currently_selected_unit.is_move_selected:
		currently_selected_unit.find_move_range(grid, (currently_selected_unit.x_pos, currently_selected_unit.y_pos))
	elif currently_selected_unit.is_attack_selected:
		currently_selected_unit.find_attack_range(grid, (currently_selected_unit.x_pos, currently_selected_unit.y_pos))

def check_aliveness(unit_list, grid):
	for unit in unit_list:
		if unit.hp <= 0:
			grid[unit.x_pos][unit.y_pos].is_occupied = False
			grid[unit.x_pos +1][unit.y_pos].is_occupied = False
			grid[unit.x_pos][unit.y_pos+1].is_occupied = False
			grid[unit.x_pos+1][unit.y_pos+1].is_occupied = False
	unit_list[:] = [unit for unit in unit_list if not (unit.hp <= 0)]

def draw_gui_upright(currently_selected_unit, grid, windowSurface, selected_space):
	right_gui = pygame.draw.rect(windowSurface, GREEN, Rect(GRID_SURFACE_WIDTH, 0, WIDTH - GRID_SURFACE_WIDTH, HEIGHT))
	if currently_selected_unit is not None:
		pygame.draw.rect(windowSurface, RED, Rect(GRID_SURFACE_WIDTH, 0, 32, 32))
		#-----------------------------------Hitpoints text--------------------------------------------------------------------------
		text_hp = newFont.render("HP: " + str(currently_selected_unit.hp) + "/" + str(currently_selected_unit.max_hp), 1, (10, 10, 10))
		textpos_hp = text_hp.get_rect()
		textpos_hp.x = right_gui.x
		textpos_hp.centery = right_gui.top + 80
		#this text is 80 pixels down and starts at the left edge of the Right GUI
		windowSurface.blit(text_hp, textpos_hp)
		#------------------------------------EP text--------------------------------------------------------------------------------
		text_ep = newFont.render("EP: " + str(currently_selected_unit.ep) + "/" + str(currently_selected_unit.max_ep), 1, (10, 10, 10))
		textpos_ep = text_ep.get_rect()
		textpos_ep.x = right_gui.x
		textpos_ep.centery = right_gui.top + 120
		#this text is 80 pixels down and starts at the left edge of the Right GUI
		windowSurface.blit(text_ep, textpos_ep)

def draw_gui_bottom(currently_selected_unit, grid, windowSurface, selected_space):
	bottom_gui = pygame.draw.rect(windowSurface, OFFRED, Rect(0, GRID_SURFACE_HEIGHT, WIDTH, 150))
	if selected_space is not None:
		text_evade = newFont.render("Evade: " + str(selected_space.terrain.evade), 1, (10, 10, 10))
		textpos_evade = text_evade.get_rect()
		textpos_evade.x = bottom_gui.x + 20
		textpos_evade.centery = bottom_gui.top + 20
		windowSurface.blit(text_evade, textpos_evade)





def battle_mouse_logic(grid_width, grid_height, grid, selected_space, currently_selected_unit):
	pos = pygame.mouse.get_pos()
	mouse_x = pos[0]
	mouse_y = pos[1]
	#check if the mouse is in the grid window
	if (mouse_x < GRID_SURFACE_WIDTH and mouse_y < GRID_SURFACE_HEIGHT):
		#----getting mouse position, grid location-----
		actual_x = mouse_x - x_offset[0]
		actual_y = mouse_y - y_offset[0]
		actuals = (actual_x, actual_y)
		grid_space = (actual_x/16, actual_y/16)
		#--------------------------debugging
		#--------------------------------if space is in the grid
		if (grid_space[0] < grid_width and grid_space[1] < grid_height):
			#assign selected space to grid tile
			selected_space = grid[grid_space[0]][grid_space[1]]
			#debugging
			print(grid[grid_space[0]][grid_space[1]].terrain.name)
			print("this space is occupied: ", selected_space.is_occupied)
			print("occupation_check:", check_occupation(grid,selected_space, currently_selected_unit))
			#if occupied, selected the unit in it
			if selected_space.is_occupied and currently_selected_unit == None:
				currently_selected_unit = selected_space.unit
				currently_selected_unit.is_move_selected = True
			else:
				#if selected unit and clicking on a non-highlighted space, cancel unit seleciton and move range display
				if ((currently_selected_unit is not None) and not (selected_space.is_move_highlighted or selected_space.is_attack_highlighted)):
					currently_selected_unit = cancel_selection(currently_selected_unit, selected_space, grid)
				#if selected unit is not none and space IS move highlighted and empty, move the unit
				elif ((currently_selected_unit is not None) and (selected_space.is_move_highlighted) and (check_occupation(grid, selected_space, currently_selected_unit) == False) and will_fit(grid, selected_space.x_pos, selected_space.y_pos)):
					perform_move(currently_selected_unit, grid, selected_space)
				elif((currently_selected_unit is not None) and (selected_space.is_attack_highlighted) and selected_space.is_occupied == True):
					currently_selected_unit.perform_targeted_attack(selected_space.unit, default_skill)

			#if the selected_unit isnt none, find its move range
			if currently_selected_unit is not None:
				find_appropriate_range(currently_selected_unit, grid)
		return currently_selected_unit
#------------------------------------Terrain Declarations---------------------------------
lava = Terrain("Lava", lava_sprite, traction = 0, evade = 10, phys = 0, nature = 0, energy = 0, phantasm = 0)
tree = Terrain("Tree", tree_sprite, traction = 20, evade = 20, phys = 20, nature = 20, energy = -20, phantasm = -25)
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
		x.append(Tile(pygame.Rect(i*GRID_SQUARE_SIZE,j*GRID_SQUARE_SIZE, GRID_SQUARE_SIZE, GRID_SQUARE_SIZE), i, j,False,True, (0,0,0)))
	grid.append(x)

print(pygame.font.get_fonts())
BLACK = (0,0,0)
WHITE = (255, 255, 255)
MYSTERY = (200, 100, 50)
GREEN = (0,255,0)
BLUE = (0, 0, 255, 128)
RED = (255, 0 , 0)
OFFRED = (170, 20, 40)
#font setup
basicFont = pygame.font.SysFont(None, 48)
basicFontSmall = pygame.font.SysFont(None, 16)
newFont = pygame.font.SysFont('dejavuserif', 16)
#text setup
windowSurface.fill(WHITE)
mapWindow.fill(WHITE)
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
			mapWindow.blit(terrain.sprite, (i*16,j*16))	
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
#-------------__TESTING__-----------
anim_count = 0
test_unit.find_all_occupied(grid)
test_unit.find_move_range(grid, (test_unit.x_pos, test_unit.y_pos))
draw_animation(grid, mapWindow, move_anims, anim_count)
pygame.draw.rect(mapWindow, RED, Rect(10*16, 10*16, 16, 16))
#Draw map onto grid, grid onto screen
#Grid surface contains the area where the grid is visible, map surface contains entire grid
friendly_units = []
friendly_units.append(test_unit)
for unit in friendly_units:
	unit.find_all_occupied(grid)
enemy_units = []
enemy_units.append(test_unit2)
for unit in enemy_units:
	unit.find_all_occupied(grid)
draw_units(mapWindow,friendly_units)
draw_units(mapWindow, enemy_units)
gridSurface.blit(mapWindow, (0,0))
windowSurface.blit(gridSurface, (0,0))
pygame.display.update()
#----------------------------------------------Game Loop-----------------------------------------------
x_offset = [0]
y_offset = [0]
currently_selected_unit = friendly_units[0]
selected_space = grid[0][0]
currently_selected_unit.is_move_selected = True
print(len(grid), "grid length")
print(len(grid[0]), "grid width")
while True:
#---------------------------------------------Player input----------------------------------------------
	for event in pygame.event.get():
		#Check for quit
		if event.type == QUIT:
			pygame.quit()
			sys.exit()
		keys = pygame.key.get_pressed()
		#if there is a unit selected
		determine_mode(currently_selected_unit, keys, grid)
		#---------------------------------------Get the mouse input-----------------------------------------------------
		if event.type == pygame.MOUSEBUTTONUP:
			currently_selected_unit = battle_mouse_logic(grid_width, grid_height, grid, selected_space, currently_selected_unit)
	#get array of keypresses
	#Variable to determine if background needs updating
	update_needed = False
	#Check for input to determine map scrolling
	update_needed = scroll_map(keys, grid, update_needed, x_offset, y_offset)
	#fill window background white
	#fill original screen black (in case of screen shake)
	#---------------------------------------------update the display-----------------------------------:
	windowSurface.fill(WHITE)
	gridSurface.fill(WHITE)
	mapWindow.fill(WHITE)
	draw_animation(grid, mapWindow, move_anims, anim_count)
	#draw units onto the grid
	draw_units(mapWindow,friendly_units)
	draw_units(mapWindow,enemy_units)
	#drawing the map surface to the grid window (the area in the upper left)
	gridSurface.blit(mapWindow, (x_offset[0],y_offset[0]))
	#Drawing the grid window to the entire window
	windowSurface.blit(gridSurface, (0,0))
	#update the display
	print(selected_space.x_pos, selected_space.y_pos, selected_space.terrain.name)
	draw_gui_upright(currently_selected_unit, grid, windowSurface, selected_space)
	draw_gui_bottom(currently_selected_unit, grid, windowSurface, selected_space)
	check_aliveness(friendly_units, grid)
	check_aliveness(enemy_units, grid)
	pygame.display.update()
	anim_count += 1
	if anim_count > (5000000):
		anim_count = 0
	#mapWindow contains grid, sprites should be blit to mapWindows
	#transparent sprites must be blit with BLEND_RGBA_MIN to achieve transparency
	#Drawing a sprite to the "map" surface
	#----------------------------------------------tick the clock----------------------------------------
	mainClock.tick(FPS)
