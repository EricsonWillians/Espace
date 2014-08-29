"""
====================================================================

ERGAME
Copyright (C) <2014>  <Ericson Willians.>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

====================================================================
Engine written by Ericson Willians, a brazilian composer and programmer.

CONTACT: ericsonwrp@gmail.com
AS A COMPOSER: http://www.youtube.com/user/poisonewein
TWITTER: https://twitter.com/poisonewein

====================================================================
"""

import pygame
import pygame.mouse as pymo
import json
import os
from itertools import product

# EXCEPTIONS
# ======================================================== #

class ErgameError(Exception):
	
	def __init__(self, message):
		
		Exception.__init__(self, message)

class InvalidDirectionError(ErgameError):
	
	def __init__(self):
		
		ErgameError.__init__(self, "Only 0, 1, 2 and 3 are valid values as direction numbers.")

class NotMemberOfError(ErgameError):
	
	def __init__(self, _class):
		
		ErgameError.__init__(self, "The given direction object is not a member of the " + _class + " class(es).")
		
class FileNotFoundError(ErgameError):
	
	def __init__(self, _file):
		
		ErgameError.__init__(self, "The file " + _file + " could not be found.")

# CFG
# ======================================================== #

GRAPHICS_PATH = "EWG"
SOUNDS_PATH = "EWS"
MUSIC_PATH = "EWM"

# DATA MANIPULATION
# ======================================================== #

def loadSound(path, name):

	class NoneSound:
		def play(self): pass
	if not pygame.mixer:
		return NoneSound()
	fullname = os.path.join(path, name)
	try:
		sound = pygame.mixer.Sound(fullname)
	except pygame.error, message:
		print "Cannot load sound:", name
		raise SystemExit, message
	return sound
	
class EwSerializable:
	
	def __init__(self):
		
		self.file = None
		
	def serialize(self, path, mode):	
		try:
			self.file = open(path, mode)
		except:
			raise FileNotFoundError()
		if self.file is not None:
			return self.file
			self.file.close()

class EwData(EwSerializable):
	
	def __init__(self):
		
		EwSerializable.__init__(self)
		self.data = {}
		
	def __setitem__(self, key, value):
		self.data[key] = value
		
	def __getitem__(self, key):
		return self.data[key]
		
	def get_data(self):
		return self.data
		
	def write(self, path):
		self.serialize(path, "w").write(json.dumps(self.get_data()))
		
	def load(self, path):
		json_data = open(path, "r")
		self.data = json.load(json_data)
		json_data.close()
		return self.data

# EXECUTION
# ======================================================== #

pygame.mixer.pre_init(44100, -16, 2, 2048*2) 
pygame.init()
pygame.font.init()

class EwRunnable:

	def __init__(self, initial_state, FPS):
		
		self.state = initial_state
		self.FPS = FPS
		self.time_elapsed = 0
		self.clock = pygame.time.Clock()
		
	def __call__(self):
		self.state = True
		
	def run(self, f, *args):
		while self.state is not True:
			dt = self.clock.tick(self.FPS)
			self.time_elapsed += dt
			apply(f, args)
			pygame.display.flip()
			
	def watch_for_exit(self):
		
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				self()
		
class EwApp(EwRunnable, EwData):

	def __init__(self, title, w, h, FPS, fullscreen=False, state=False):

		EwRunnable.__init__(self, state, FPS)
		EwData.__init__(self)
		
		if os.path.isfile("conf.edt"):
			self["TITLE"] = self.load("conf.edt")["TITLE"]
			self["SCREEN_WIDTH"] = self.load("conf.edt")["SCREEN_WIDTH"]
			self["SCREEN_HEIGHT"] = self.load("conf.edt")["SCREEN_WIDTH"]
			self["FPS"] = self.load("conf.edt")["FPS"]
			self["FULLSCREEN"] = self.load("conf.edt")["FULLSCREEN"]
			print "Configuration dictionary loaded:\n===============================\n"
			for item in self.data.items():
				print "{}: {}".format(str(item[0]), str(item[1]))
		else:
			self["TITLE"] = title
			self["SCREEN_WIDTH"] = w
			self["SCREEN_HEIGHT"] = h
			self["FPS"] = FPS
			self["FULLSCREEN"] = fullscreen
			self.write("conf.edt")
			print "Configuration dictionary saved."
		
		if self["FULLSCREEN"] == True:
			self.screen = pygame.display.set_mode((self["SCREEN_WIDTH"], self["SCREEN_HEIGHT"]), pygame.DOUBLEBUF | pygame.FULLSCREEN)
		else:
			self.screen = pygame.display.set_mode((self["SCREEN_WIDTH"], self["SCREEN_HEIGHT"]))
		pygame.display.set_caption(self["TITLE"])
		

	def check_if_time_has_elapsed_in_milliseconds(self, milliseconds):
		if self.time_elapsed > milliseconds:
			self.time_elapsed = 0
			return True
		else:
			return False
			
	def check_if_time_has_elapsed_in_seconds(self, seconds):
		if self.time_elapsed > seconds*1000:
			self.time_elapsed = 0
			return True
		else:
			return False
			
	def check_if_time_has_elapsed_in_minutes(self, minutes):
		if self.time_elapsed > minutes*60000:
			self.time_elapsed = 0
			return True
		else:
			return False
			
	def get_center_x(self, width):
		return (self["SCREEN_WIDTH"]/2)-(width/2)
		
	def get_center_y(self, height):
		return (self["SCREEN_HEIGHT"]/2)-(height/2)

# POSITIONS AND DIMENSIONS
# ======================================================== #
		
class EwPos:
	
	def __init__(self, x, y):
		
		self.x = x
		self.y = y
		
	def __getitem__(self, key):
		
		if key == "x":
			return self.x
		elif key == "y":
			return self.y
		elif key == "(xy)":
			return (self.x, self.y)
		elif key == "[xy]":
			return [self.x, self.y]
		
	def __setitem__(self, key, value):
		
		if key == "x":
			self.x = value
		elif key == "y":
			self.y = value
		
	def __call__(self):
		return (self.x, self.y)
		
	def get_x(self):
		return self.x
		
	def set_x(self, value):
		self.x = value
		
	def get_y(self):
		return self.y

	def set_y(self, value):
		self.y = value

class EwDirection:
	
	DIRECTIONS = ["NORTH", "SOUTH", "WEST", "EAST"]
	
	def __init__(self, value=0):
		
		self.value = value
		
		if isinstance(self.value, basestring):
			if self.value.upper() in ["UP", "DOWN", "LEFT", "RIGHT"]:
				if self.value.upper() == "UP":
					self.value = "NORTH"
				elif self.value.upper() == "DOWN":
					self.value = "SOUTH"
				elif self.value.upper() == "LEFT":
					self.value = "WEST"
				elif self.value.upper() == "RIGHT":
					self.value = "EAST"
		else:
			if self.value in range(0, 3):
				if self.value == 0:
					self.value = "NORTH"
				elif self.value == 1:
					self.value = "SOUTH"
				elif self.value == 2:
					self.value = "WEST"
				elif self.value == 3:
					self.value = "EAST"
				
	def __call__(self):
		return self.value
		
	def get(self):
		return self.value

class EwMovable(EwPos):
	
	def __init__(self, x, y):
		
		EwPos.__init__(self, x, y)
	
	def move(self, condition, direction=0, step=1):
		if isinstance(direction, EwDirection):
			self.direction = direction
		else:
			direction = EwDirection(direction)
		if condition:
			if direction() == 0 or direction() == "NORTH":
				self.y -= step
			if direction() == 1 or direction() == "SOUTH":
				self.y += step
			if direction() == 2 or direction() == "WEST":
				self.x -= step
			if direction() == 3 or direction() == "EAST":
				self.x += step
	
	def teleport(self, condition, new_x, new_y):
		if condition:
			self.x = new_x
			self.y = new_y
		
	def get_direction(self):
		return self.direction
		
	def set_direction(self, value):
		self.direction = value
	
	def get_step(self):
		return self.step
		
	def set_step(self, value):
		self.step = value
			
class EwResizable:
	
	def __init__(self, w, h):
		
		self.w = w
		self.h = h
		
	def __getitem__(self, key):
		
		if key == "w":
			return self.w
		elif key == "h":
			return self.h
		elif key == "(wh)":
			return (self.w, self.h)
		elif key == "[wh]":
			return [self.w, self.h]
		
	def __setitem__(self, key, value):
		
		if key == "w":
			self.w = value
		elif key == "h":
			self.h = value
		
	def get_w(self):
		return self.w
		
	def set_w(self, value):
		self.w = value
		
	def get_h(self):
		return self.h
		
	def set_h(self, value):
		self.h = value
		
class EwPositioningSystem(EwResizable):
	
	def __init__(self, option, sharpness=1):
		
		CONST_SHARPNESS = 16
		
		if option == 0:
			w = 640
			h = 480
		elif option == 1:
			w = 800
			h = 600
		elif option == 2:
			w = 1024
			h = 768
		elif option == 3:
			w = 1280
			h = 1024
		elif option == 4:
			w = 1680
			h = 1050
		
		if sharpness != 0:
			sh = CONST_SHARPNESS*sharpness
		else:
			sh = CONST_SHARPNESS*1
	
		EwResizable.__init__(self, w, h)
		
		self.key_positions = [[x for x in range(sh)], [y for y in range(sh)]]
		self.x = dict(zip([x for x in self.key_positions[0]], [x for x in range(0, w, w/sh)]))
		self.y = dict(zip([y for y in self.key_positions[1]], [y for y in range(0, h, h/sh)]))
		self.coords = list(product(self.y.keys(), self.x.keys()))
		self.sh = sh
		
# Object Manipulation
# ======================================================== #

class EwDrawable:
	
	def __init__(self):
		
		pass
		
	def draw(self, destination_surface):
		pass

class EwObject(EwDrawable, EwData, EwMovable, EwResizable):
	
	def __init__(self, x, y, w, h):
		
		EwData.__init__(self)
		EwMovable.__init__(self, x, y)
		EwResizable.__init__(self, w, h)
		
	def __call__(self):
		return (self.x, self.y, self.w, self.h)
		
class EwImage(EwObject):
	
	def __init__(self, x, y, w, h, filename, alpha=255):
		
		EwObject.__init__(self, x, y, w, h)
		
		self.filename = filename
		self.alpha = alpha
		
		if ".png" not in self.filename:
			self.image = pygame.image.load(os.path.join(GRAPHICS_PATH, filename)).convert()
		else:
			self.image = pygame.image.load(os.path.join(GRAPHICS_PATH, filename)).convert_alpha()
		
		self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)
		self.transform()
			
	def transform(self):
		self.image = pygame.transform.scale(self.image, (self.w, self.h))
		
	def transform_freely(self, w, h):
		self.image = pygame.transform.scale(self.image, (w, h))
		
	def fade_in(self, speed, limit=255):
		if (self.alpha < limit) and (self.alpha < 255):
			self.alpha += speed
			self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)
		
	def fade_out(self, speed, limit=0):
		if (self.alpha > limit) and (self.alpha > 0):
			self.alpha -= speed
			self.image.fill((255, 255, 255, self.alpha), None, pygame.BLEND_RGBA_MULT)
			
	def is_faded_in(self, value=255):
		if self.alpha >= value:
			return True
		else:
			return False 
			
	def is_faded_out(self, value=0):
		if self.alpha <= value:
			return True
		else:
			return False 
			
	def draw(self, destination_surface):
		destination_surface.blit(self.image, (self.x, self.y))
		
class EwScrollingImage(EwImage):
	
	def __init__(self, x, y, w, h, filename, scroll_direction=0, scroll_speed=1):
		
		EwImage.__init__(self, x, y, w, h, filename)
		
		if isinstance(scroll_direction, EwDirection):
			self.scroll_direction = scroll_direction
		else:
			raise NotMemberOfError("EwDirection")
		self.scroll_speed = scroll_speed
		self.default_scroll_speed = self.scroll_speed
		self.initial_y = self.y
		self.y0_reset_point = self.initial_y - self.h
		self.y1_reset_point = self.initial_y + self.h
		self.initial_x = self.x
		self.x2_reset_point = self.initial_x - self.w
		self.x3_reset_point = self.initial_x + self.w
		
	def draw(self, destination_surface):
		if self.scroll_direction() == 0 or self.scroll_direction() == "NORTH":
			self.y -= self.scroll_speed
			if self.y < self.y0_reset_point:
				self.y = self.initial_y
			destination_surface.blit(self.image, (self.x, self.y))
			destination_surface.blit(self.image, (self.x, self.y+self.h))
		if self.scroll_direction() == 1 or self.scroll_direction() == "SOUTH":
			self.y += self.scroll_speed
			if self.y > self.y1_reset_point:
				self.y = self.initial_y
			destination_surface.blit(self.image, (self.x, self.y))
			destination_surface.blit(self.image, (self.x, self.y-self.h))
		if self.scroll_direction() == 2 or self.scroll_direction() == "WEST":
			self.x -= self.scroll_speed
			if self.x < self.x2_reset_point:
				self.x = self.initial_x
			destination_surface.blit(self.image, (self.x, self.y))
			destination_surface.blit(self.image, (self.x+self.w, self.y))
		if self.scroll_direction() == 3 or self.scroll_direction() == "EAST":
			self.x += self.scroll_speed
			if self.x > self.x3_reset_point:
				self.x = self.initial_x
			destination_surface.blit(self.image, (self.x, self.y))
			destination_surface.blit(self.image, (self.x-self.w, self.y))
			
	def get_scroll_direction(self):
		return self.scroll_direction
		
	def set_scroll_direction(self, value):
		self.scroll_direction = value
		
	def get_scroll_speed(self):
		return self.scroll_speed
		
	def set_scroll_speed(self, value):
		self.scroll_speed = value
		
	def reset_scroll_speed(self):
		self.scroll_speed = self.default_scroll_speed
			
class EwFont(EwObject):
	
	def __init__(self, x, y, w, h, filename, text, color, bold=False):
		
		EwObject.__init__(self, x, y, w, h)
		
		self.filename = filename
		self.text = text
		self.color = color
		if self.filename is not None:
			self.font = pygame.font.Font(os.path.join(GRAPHICS_PATH, filename), self.w+self.h*2)
		else:
			self.font = pygame.font.Font(None, self.w+self.h)
		if bold:
			self.font.set_bold(True)
		self.image = self.font.render(self.text, 1, self.color)
		self.transform()
		
	def transform(self):
		self.image = pygame.transform.scale(self.image, (self.w, self.h))
		
	def draw(self, destination_surface):
		destination_surface.blit(self.image, (self.x, self.y))
		
	def get_text(self):
		return self.text
	
	def update(self, value):
		self.text = value
		self.image = self.font.render(self.text, 1, self.color)
		self.transform()
	
	def __call__(self, value):
		self.text = value
		self.image = self.font.render(self.text, 1, self.color)
		self.transform()
	
	def set_text(self, value):
		self.text = value
   
	def get_color(self):
		return self.color
		
	def set_color(self, value):
		self.color = value
		
def draw_mouse_coordinates(destination_surface, w=None, h=None, color=(255,0,0)):
	if w is None or h is None:
		w = 64
		h = 16
	pos = EwFont(pymo.get_pos()[0]+16, pymo.get_pos()[1], w, h, None, str((pymo.get_pos()[0], pymo.get_pos()[1])), color)
	pos.draw(destination_surface)

class EwShape(EwObject):
	
	def __init__(self, x, y, w, h, color, thickness):
		
		EwObject.__init__(self, x, y, w, h)
		
		self.color = color
		self.thickness = thickness
		
	def __call__(self):
		return (self.x, self.y, self.w, self.h, self.color, self.thickness)
		
	def get_color(self):
		return self.color
		
	def set_color(self, value):
		self.color = value
		
	def get_thickness(self):
		return self.thickness
		
	def set_thickness(self, value):
		self.thickness = value
		
class EwRect(EwShape):
	
	def __init__(self, x, y, w, h, color=(255,255,255), thickness=1):
		
		EwShape.__init__(self, x, y, w, h, color, thickness)
		
	def draw(self, destination_surface):
		pygame.draw.rect(destination_surface, self.color, (self.x, self.y, self.w, self.h), self.thickness)
		
	def draw_ellipse(self, destination_surface):
		pygame.draw.ellipse(destination_surface, self.color, (self.x, self.y, self.w, self.h), self.thickness)
		
class EwPolygon(EwShape):
	
	def __init__(self, pointlist, color=(255,255,255), thickness=1):
		
		EwShape.__init__(self, None, None, None, None, color, thickness)
		self.pointlist = pointlist
		
	def draw(self, destination_surface):
		pygame.draw.polygon(destination_surface, self.color, self.pointlist, self.thickness)
		
class EwCircle(EwShape):
	
	def __init__(self, x, y, radius, color=(255,255,255), thickness=1):
		
		EwShape.__init__(self, x, y, radius*2, radius*2, color, thickness)
		self.radius = radius
		
	def draw(self, destination_surface):
		pygame.draw.circle(destination_surface, self.color, (self.x, self.y), self.radius, self.thickness)
		
	def get_radius(self):
		return self.radius
		
class EwEllipse(EwRect):
	
	def __init__(self, x, y, w, h, color=(255,255,255), thickness=1):
		
		EwRect.__init__(self, x, y, w, h, color, thickness)
		
	def draw(self, destination_surface):
		pygame.draw.ellipse(destination_surface, self.color, (self.x, self.y, self.w, self.h), self.thickness)
		
class EwArc(EwShape):
	
	def __init__(self, x, y, w, h, start_angle, stop_angle, color=(255,255,255), thickness=1):
		
		EwShape.__init__(self, x, y, w, h, color, thickness)
		self.start_angle = start_angle
		self.stop_angle = stop_angle
		
	def draw(self, destination_surface):
		pygame.draw.arc(destination_surface, self.color, (self.x, self.y, self.w, self.h), self.start_angle, self.stop_angle, self.thickness)
		
	def get_start_angle(self):
		return self.start_angle
		
	def get_stop_angle(self):
		return self.stop_angle

class EwLine(EwShape):
	
	def __init__(self, start_pos, end_pos, color=(255,255,255), thickness=1):
	
		EwShape.__init__(self, None, None, None, None, color, thickness)
		self.start_pos = start_pos
		self.end_pos = end_pos
		
	def draw(self, destination_surface):
		pygame.draw.line(destination_surface, self.color, self.start_pos, self.end_pos, self.thickness)
		
class EwLines:
	
	def __init__(self, lines):

		self.lines = lines
	
	def draw(self, destination_surface):
		
		if len(self.lines) > 0:
			for line in self.lines:
				if isinstance(line, EwLine):
					line.draw(destination_surface)
				else:
					raise NotMemberOfError("EwLine")
					
	def __call__(self):
		return self.lines
		
	def get_lines(self):
		return self.lines

# Collision Detection
# ======================================================== #

class EwCol:
	
	def __init__(self, o, oo):
		
		self.o = o
		self.oo = oo
		self.ox = self.o.x
		self.oy = self.o.y
		self.ow = self.o.w
		self.oh = self.o.h
		self.oox = self.oo.x
		self.ooy = self.oo.y
		self.oow = self.oo.w
		self.ooh = self.oo.h
		
	def __call__(self):
		
		if ((((self.ox + self.ow) > self.oox) and (self.ox < (self.oox + self.oow))) and (((self.oy + self.oh) > self.ooy) and (self.oy < (self.ooy + self.ooh)))):
			return True
		else:
			return False
			
class EwMouseCol:
	
	def __init__(self, o, oo):
		
		self.o = o
		self.oo = oo
		self.ox = self.o[0]
		self.oy = self.o[1]
		self.oox = self.oo.x
		self.ooy = self.oo.y
		self.oow = self.oo.w
		self.ooh = self.oo.h
		
	def __call__(self):
		
		if (((self.ox > self.oox) and (self.ox < (self.oox + self.oow))) and ((self.oy > self.ooy) and (self.oy < (self.ooy + self.ooh)))):
			return True
		else:
			return False

# Screen Management
# ======================================================== #

class EwScene:
	
	def __init__(self, scene):
		
		if isinstance(scene, basestring):
			self.scene = scene
		else:
			raise NotMemberOfError("basestring")
		
class EwPlot:
	
	def __init__(self, scenes):
		
		self.data = scenes
		if len(self.data) > 0:
			
			self.current = self.data[0]
	
	def __call__(self):
		return self.current
	
	def get_scene(self):
		return self.current
	
	def change_scene(self, new_scene):
		self.current = new_scene
		
	def next(self):
		if self.data.index(self.current) != len(self.data)-1:
			self.change_scene(self.data[self.data.index(self.current)+1])
		else:
			self.change_scene(self.data[0])
			
	def previous(self):
		if self.data.index(self.current) != 0:
			self.change_scene(self.data[self.data.index(self.current)-1])
		else:
			self.change_scene(self.data[len(self.data)-1])
		
def get_standard_plot():

	scene = [EwScene("S"+str(x)) for x in range(999)]
	opt = [EwScene("OPT"+str(x)) for x in range(999)]
	inv = [EwScene("INV"+str(x)) for x in range(999)]
	l = []
	l.append(EwScene("MAIN"))
	l.extend(scene)
	l.extend(opt)
	l.extend(inv)
	return EwPlot(l)

# GUI
# ======================================================== #

class EwAbstractButton:
	
	def __init__(self, x, y, font_width, font_height, font_filename, text, font_color, bold=False):
		
		self.font = EwFont(x, y, font_width, font_height, font_filename, text, font_color, bold)
	
	def hover(self, mouse_pos):
		if EwMouseCol(mouse_pos, self)():
			return True
		if not EwMouseCol(mouse_pos, self)():
			return False
				
	def press(self, mouse_pos, mouse_button, key=None):
		if EwMouseCol(mouse_pos, self)() and pygame.mouse.get_pressed()[mouse_button]:
			return True
		if not EwMouseCol(mouse_pos, self)() and pygame.mouse.get_pressed()[mouse_button]:
			return False
		if key is not None:
			if pygame.key.get_pressed()[key]:
				return True
			if not pygame.key.get_pressed()[key]:
				return False
		
	def get_font_size(self):
		return self.font_size
		
	def set_font_size(self, value):
		self.font_size = value
		
	def get_font(self):
		return self.font
		
	def set_font(self, new_font):
		self.font = new_font
		
class EwButton(EwAbstractButton, EwImage):
	
	def __init__(self, x, y, w, h, filename, font_width, font_height, font_filename, text, font_color, bold=False):
		
		EwAbstractButton.__init__(self, x+font_width/2, y+font_height/2, font_width, font_height, font_filename, text, font_color, bold)
		EwImage.__init__(self, x, y, w, h, filename)
		
class EwRectButton(EwAbstractButton, EwRect):
	
	def __init__(self, x, y, w, h, color, thickness, font_width, font_height, font_filename, text, font_color, bold=False):
		
		EwAbstractButton.__init__(self, x+(w/2)-(font_width/2), y+(h/2)-(font_height/2), font_width, font_height, font_filename, text, font_color, bold)
		EwRect.__init__(self, x, y, w, h, color, thickness)
		
# Environment
# ======================================================== #

class EwEnvironment(EwData):
	
	def __init__(self):
		
		EwData.__init__(self)

# Game-Specific
# ======================================================== #

class HealthBar(EwRect):
		
	def __init__(self, x, y, w, h, value):
			
		self.value = value
		self.green = 255
		self.red = 0
		self.number = EwFont(x+(w/2)-(w/5)/2, y, w/5, h, None, str(self.value), (255, 255, 255))
		EwRect.__init__(self, x, y, w, h, (self.red, self.green, 0), 0)
			
	def subtract_health(self, damage):
			
		self.value -= damage
		if self.green > 0:
			self.green -= 255/self.value
		if self.red < 255:
			self.red += 255/self.value
		if self.green >= 0 and self.red <= 255:
			self.color = (self.red, self.green, 0)
