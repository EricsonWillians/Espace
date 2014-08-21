"""
====================================================================

ESPACE
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
Game written by Ericson Willians, a brazilian composer and programmer.

CONTACT: ericsonwrp@gmail.com
AS A COMPOSER: http://www.youtube.com/user/poisonewein
TWITTER: https://twitter.com/poisonewein

====================================================================
"""

import os
import pygame
import ergame as er
from random import randrange
from random import uniform

if __name__ == "__main__":

	SCREEN_WIDTH = 1024
	SCREEN_HEIGHT = 768
	DISTANCE_LIMIT = 2048

	app = er.EwApp("Espace", SCREEN_WIDTH, SCREEN_HEIGHT, 300, True)
	
	if not os.path.isfile("hs"):
		open("hs", "w")
	
	plot = er.EwPlot(["MAIN_MENU", "GAME", "HIGHSCORE", "PAUSE" "GAME_OVER"])
	
	pygame.mixer.music.load(os.path.join(er.MUSIC_PATH, "ewm.ogg"))
#	pygame.mixer.music.play(-1)
		
	fire_sound = pygame.mixer.Sound(os.path.join(er.SOUNDS_PATH, "fire.ogg"))
	fire_sound.set_volume(0.3)
	
	kill = pygame.mixer.Sound(os.path.join(er.SOUNDS_PATH, "kill.ogg"))
	kill.set_volume(0.5)
	
	raid_sound = pygame.mixer.Sound(os.path.join(er.SOUNDS_PATH, "raid.ogg"))
	lost_sound = pygame.mixer.Sound(os.path.join(er.SOUNDS_PATH, "lost.ogg"))
	game_over_sound = pygame.mixer.Sound(os.path.join(er.SOUNDS_PATH, "game_over.ogg"))

	bg = er.EwScrollingImage(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, "bg.png", er.EwDirection("SOUTH"))
	
	class HealthBar(er.EwRect):
		
		def __init__(self, x, y, w, h, value):
			
			self.value = value
			self.green = 255
			self.red = 0
			self.number = er.EwFont(x+(w/2)-(w/5)/2, y, w/5, h, None, str(self.value), (255, 255, 255))
			er.EwRect.__init__(self, x, y, w, h, (self.red, self.green, 0), 0)
			
		def subtract_health(self, damage):
			
			self.value -= damage
			if self.green > 0:
				self.green -= 255/self.value
			if self.red < 255:
				self.red += 255/self.value
			if self.green >= 0 and self.red <= 255:
				self.color = (self.red, self.green, 0)
	
	PLAYER_SIZE = 64
	PLAYER_COLOR = (255, 255, 255)
	PLAYER_SPEED = 1
	PLAYER_BOOST = 1.8
	
	player = er.EwImage(((SCREEN_WIDTH/2)-(PLAYER_SIZE/2)), 768-PLAYER_SIZE*2, PLAYER_SIZE+32, PLAYER_SIZE, "Player.png")
	player["Health"] = 20
	player["Ammo"] = []
	player["Health Bar"] = HealthBar((SCREEN_WIDTH/2)-player.w/2, SCREEN_HEIGHT-player.h/2, player.w, player.h/3, 20)

	tlost_green = 255
	tlost_red = 0
	
	class Bullet(er.EwRect):
		
		def __init__(self, x, y, w, h, color, thickness, speed):
			
			self.speed = speed
			er.EwRect.__init__(self, x, y, w, h, color, thickness)

	class PlayerBullet(Bullet):
		
		def __init__(self, x, y, speed):

			Bullet.__init__(self, x+((PLAYER_SIZE/2)/2), y-PLAYER_SIZE/2, PLAYER_SIZE/2 + 32, PLAYER_SIZE/2, (50, 50, 255), 2, speed)
			
	class EnemyBullet(Bullet):
		
		def __init__(self, x, y, w, h, color, speed):

			Bullet.__init__(self, x, y, w, h, color, 0, speed)

	frags = 0
	lost = 0
	LOST_LIMIT = 10
	
	class Enemy(er.EwImage):
		
		SIZES = [x for x in range(0, 128, 16)]
		FILENAMES = ["Spaceship-Drakir" + str(x) + ".png" for x in range(1, 8)]

		def __init__(self, speed_range):

			self.health = randrange(5, 20)
			self.speed = uniform(0.2, speed_range)
			
			w = randrange(64, Enemy.SIZES[len(Enemy.SIZES)-1])
			h = randrange(16, Enemy.SIZES[len(Enemy.SIZES)-1])
			x = randrange(8, SCREEN_WIDTH-w)
			y = -randrange(h, DISTANCE_LIMIT)
			er.EwImage.__init__(self, x, y, w, h, Enemy.FILENAMES[randrange(0, len(Enemy.FILENAMES)-1)])
			self.health_bar = HealthBar(x, y-h/2, w, h/3, self.health)
			
		def translate(self):
			self.y += self.speed
			self.health_bar.y += self.speed
			self.health_bar.number.y += self.speed
			
	class Raid:
		
		def __init__(self, spawn_number, speed_range):

			self.spawn = [Enemy(speed_range) for x in range(1, spawn_number)]
			for enemy in self.spawn:
				enemy["Ammo"] = []
			
		def draw(self):
			[x.draw(app.screen) for x in self.spawn]
			[x.health_bar.draw(app.screen) for x in self.spawn]
			[x.health_bar.number.draw(app.screen) for x in self.spawn]
			[x.health_bar.number.update(str(x.health)) for x in self.spawn]
			[x.translate() for x in self.spawn]
			
		def check_col(self):
			for en in self.spawn:
				for bullet in player["Ammo"]:
					if er.EwCol(bullet, en)():
						if en.health <= 0:
							kill.play()
							self.spawn.pop(self.spawn.index(en))
							global frags
							frags += 1
						en.health -= 1
						en.health_bar.subtract_health(1)
						player["Ammo"].pop(player["Ammo"].index(bullet))
				for bullet in en["Ammo"]:
					if er.EwCol(bullet, player)():
						random_damage = randrange(1, 4)
						player["Health"] -= random_damage
						player["Health Bar"].subtract_health(random_damage)
						en["Ammo"].pop(en["Ammo"].index(bullet))
			
	class RaidManager:
		
		def __init__(self):
			
			self.counter = 1
			self.spawn_number = randrange(5, 9)
			self.speed_range = 0.4
			self.raid = Raid(self.spawn_number, self.speed_range)
			
		def manage(self):
			
			if len(self.raid.spawn) > 0:
				self.raid.draw()
				self.raid.check_col()
			else:
				raid_sound.play()
				self.spawn_number += randrange(1, 4)
				self.speed_range += 0.05
				self.raid = Raid(self.spawn_number, self.speed_range)
				self.counter += 1
				bg.scroll_speed += 0.5
			
	RM = RaidManager()
	
	def default():
		
		global tlost_green
		tlost_green = 255
		global tlost_red
		tlost_red = 0
		global frags
		frags = 0
		global lost
		lost = 0
		player.x = ((SCREEN_WIDTH/2)-(PLAYER_SIZE/2))
		player.y = 768-PLAYER_SIZE*2
		player["Health"] = 20
		player["Ammo"] = []
		player["Health Bar"] = HealthBar((SCREEN_WIDTH/2)-player.w/2, SCREEN_HEIGHT-player.h/2, player.w, player.h/3, 20)
		global RM
		RM = RaidManager()
	
	def end_game():
		
		for en in RM.raid.spawn:
			if en.y > SCREEN_HEIGHT+en.h:
				lost_sound.play()
				global lost
				lost += 1
				RM.raid.spawn.pop(RM.raid.spawn.index(en))
				global tlost_green
				global tlost_red
				tlost_green -= 255/LOST_LIMIT
				tlost_red += 255/LOST_LIMIT
			if er.EwCol(player, en)() or lost >= 10 or player["Health"] <= 0:
				if os.path.isfile("hs"):
					hs = 0
					hs_file_r = open("hs", "r")
					for n in hs_file_r.read():
						hs = int(n)
					hs_file_r.close()
				if hs < frags:
					hs_file_w = open("hs", "w")
					hs_file_w.write(str(frags))
					hs_file_w.close()
				plot.change_scene("GAME_OVER")
				game_over_sound.play()
	
	def organize_bullets():

		if pygame.key.get_pressed()[pygame.K_SPACE]:
			if app.check_if_time_has_elapsed_in_milliseconds(80):
				fire_sound.play()
				if len(player["Ammo"]) < 16:
					player["Ammo"].append(PlayerBullet(player.x, player.y, 2))
				else:
					for bullet in player["Ammo"]:
						if bullet.y < -bullet.h:
							player["Ammo"].pop(player["Ammo"].index(bullet))    
				
		if len(player["Ammo"]) > 0:
			for bullet in player["Ammo"]:
				bullet.y -= bullet.speed
				bullet.draw_ellipse(app.screen)
				
		if len(RM.raid.spawn) > 0:
			for enemy in RM.raid.spawn:
				if len(enemy["Ammo"]) < 1:
					enemy["Ammo"].append(EnemyBullet(enemy.x+(enemy.w/2)-4, enemy.y+(enemy.h+4), 8, 8, (255, 255, 255), uniform(0.3, 2.2)))
				else:
					for bullet in enemy["Ammo"]:
						if bullet.y > SCREEN_HEIGHT + bullet.h:
							enemy["Ammo"].pop(enemy["Ammo"].index(bullet))
							
				if len(enemy["Ammo"]) > 0:
					for bullet in enemy["Ammo"]:
						bullet.y += bullet.speed
						bullet.draw_ellipse(app.screen)
		
# Buttons:

	BUTTON_WIDTH = 128
	BUTTON_HEIGHT = 64
	BUTTON_COLOR = (50, 50, 50)
	BUTTON_THICKNESS = 5
	CENTER_X = (SCREEN_WIDTH/2)-(BUTTON_WIDTH/2)
	CENTER_Y = (SCREEN_HEIGHT/2)-(BUTTON_HEIGHT/2)

	start_game = er.EwRectButton(CENTER_X, CENTER_Y-(BUTTON_HEIGHT*2), 
		BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, 
		BUTTON_THICKNESS, BUTTON_WIDTH-16, 
		BUTTON_HEIGHT-16, "Squares Bold Free.otf", "Start Game", (255, 255, 255))
		
	resume_game = er.EwRectButton(CENTER_X, CENTER_Y-(BUTTON_HEIGHT*2), 
		BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, 
		BUTTON_THICKNESS, BUTTON_WIDTH-16, 
		BUTTON_HEIGHT-16, "Squares Bold Free.otf", "Resume", (255, 255, 255))
	
	highscore = er.EwRectButton(CENTER_X, (CENTER_Y-BUTTON_HEIGHT)+BUTTON_THICKNESS, 
		BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, 
		BUTTON_THICKNESS, BUTTON_WIDTH-16, 
		BUTTON_HEIGHT-16, "Squares Bold Free.otf", "Highscore", (255, 255, 255))
		
	_exit = er.EwRectButton(CENTER_X, CENTER_Y+BUTTON_THICKNESS*2, 
		BUTTON_WIDTH, BUTTON_HEIGHT, BUTTON_COLOR, 
		BUTTON_THICKNESS, BUTTON_WIDTH-16, 
		BUTTON_HEIGHT-16, "Squares Bold Free.otf", "Exit", (255, 255, 255))
		
	def glow(button):
		
		if button.hover(pygame.mouse.get_pos()):
			button.color = (50, 50, 255)
		else:
			button.color = BUTTON_COLOR
			
	buttons = [start_game, highscore, resume_game, _exit]

# Text:

	tfrags = er.EwFont(16, 16, 128+16, 16, "Squares Bold Free.otf", "Frags: " + str(frags), (255, 255, 255))
	tlost = er.EwFont(16, 16*2, 128+16, 16, "Squares Bold Free.otf", "Lost: " + str(lost), (0, 255, 0))
	traid = er.EwFont(16, 16*3, 128+16, 16, "Squares Bold Free.otf", "Raid: " + str(RM.counter), (255, 255, 255))
	tespace = er.EwFont((SCREEN_WIDTH/2)-128, 64, 256, 128, "Squares Bold Free.otf", "ESPACE", (150, 255, 255))
	tpaused = er.EwFont((SCREEN_WIDTH/2)-256, SCREEN_HEIGHT-320, 512, 256, "Squares Bold Free.otf", "PAUSED", (255, 255, 255))
	tover = er.EwFont((SCREEN_WIDTH/2)-256, SCREEN_HEIGHT-320, 512, 256, "Squares Bold Free.otf", "GAME OVER", (255, 255, 255))
	tcredits = er.EwFont((SCREEN_WIDTH/2)-256, SCREEN_HEIGHT-32, 512, 32, "Squares Bold Free.otf", "A game written by Ericson Willians.", (255, 255, 255))

	hud = [tfrags, tlost, traid]
	
	previous_screen = ""

	def update():
		
		pygame.display.flip()
		bg.draw(app.screen)
		
		if plot() == "MAIN_MENU":
			
			if start_game.press(pygame.mouse.get_pos(), 0, pygame.K_RETURN):
				plot.change_scene("GAME")
				
			if highscore.press(pygame.mouse.get_pos(), 0, pygame.K_h):
				global previous_screen
				previous_screen = "MAIN_MENU"
				plot.change_scene("HIGHSCORE")
				
			if _exit.press(pygame.mouse.get_pos(), 0):
				app.state = True

			[b.draw(app.screen) for b in buttons if b != resume_game]
			[b.font.draw(app.screen) for b in buttons if b != resume_game]
			[glow(b) for b in buttons]
			
			tespace.draw(app.screen)
			tcredits.draw(app.screen)
				
		if plot() == "HIGHSCORE":
			
			try:
				if os.path.isfile("hs"):
					hs = ""
					hs_file_r = open("hs", "r")
					hs = int("".join(hs_file_r.read()))
					hs_file_r.close()
			except:
				hs = 0
			
			er.EwFont((SCREEN_WIDTH/2)-(SCREEN_WIDTH-256)/2, (SCREEN_HEIGHT/2)-(SCREEN_HEIGHT-256)/2, SCREEN_WIDTH-256, SCREEN_HEIGHT-256, "Squares Bold Free.otf", str(hs), (150, 255, 255)).draw(app.screen)
	
			if pygame.key.get_pressed()[pygame.K_ESCAPE]:
				if previous_screen == "MAIN_MENU":
					plot.change_scene("MAIN_MENU")
				if previous_screen == "PAUSE":
					plot.change_scene("PAUSE")
				if previous_screen == "GAME_OVER":
					plot.change_scene("GAME_OVER")
	
		if plot() == "GAME":

			# Text <<
			
			tfrags("Frags: " + str(frags))
			tlost("Lost: " + str(lost))
			tlost.color = (tlost_red, tlost_green, 0)
			traid("Raid: " + str(RM.counter))
			
			[t.draw(app.screen) for t in hud]
			
			# Players, enemies and stuff <<
			player.draw(app.screen)
			player["Health Bar"].draw(app.screen)
			player["Health Bar"].number.update(str(player["Health"]))
			player["Health Bar"].number.draw(app.screen)
			organize_bullets()
			RM.manage()
			end_game()

			if not pygame.key.get_pressed()[pygame.K_LSHIFT]:
				player.move(pygame.key.get_pressed()[pygame.K_UP], er.EwDirection("NORTH"), PLAYER_SPEED)
				player.move(pygame.key.get_pressed()[pygame.K_w], er.EwDirection("NORTH"), PLAYER_SPEED)
				player.move(pygame.key.get_pressed()[pygame.K_DOWN], er.EwDirection("SOUTH"), PLAYER_SPEED)
				player.move(pygame.key.get_pressed()[pygame.K_s], er.EwDirection("SOUTH"), PLAYER_SPEED)
				player.move(pygame.key.get_pressed()[pygame.K_LEFT], er.EwDirection("WEST"), PLAYER_SPEED)
				player.move(pygame.key.get_pressed()[pygame.K_a], er.EwDirection("WEST"), PLAYER_SPEED)
				player.move(pygame.key.get_pressed()[pygame.K_RIGHT], er.EwDirection("EAST"), PLAYER_SPEED)
				player.move(pygame.key.get_pressed()[pygame.K_d], er.EwDirection("EAST"), PLAYER_SPEED)
			else:
				player.move(pygame.key.get_pressed()[pygame.K_UP], er.EwDirection("NORTH"), PLAYER_BOOST)
				player.move(pygame.key.get_pressed()[pygame.K_w], er.EwDirection("NORTH"), PLAYER_BOOST)
				player.move(pygame.key.get_pressed()[pygame.K_DOWN], er.EwDirection("SOUTH"), PLAYER_BOOST)
				player.move(pygame.key.get_pressed()[pygame.K_s], er.EwDirection("SOUTH"), PLAYER_BOOST)
				player.move(pygame.key.get_pressed()[pygame.K_LEFT], er.EwDirection("WEST"), PLAYER_BOOST)
				player.move(pygame.key.get_pressed()[pygame.K_a], er.EwDirection("WEST"), PLAYER_BOOST)
				player.move(pygame.key.get_pressed()[pygame.K_RIGHT], er.EwDirection("EAST"), PLAYER_BOOST)
				player.move(pygame.key.get_pressed()[pygame.K_d], er.EwDirection("EAST"), PLAYER_BOOST)
				
			if pygame.key.get_pressed()[pygame.K_p]:
				plot.change_scene("PAUSE")
			
		if plot() == "PAUSE":
			
			tpaused.draw(app.screen)
			
			if resume_game.press(pygame.mouse.get_pos(), 0, pygame.K_ESCAPE):
				plot.change_scene("GAME")
				
			if highscore.press(pygame.mouse.get_pos(), 0, pygame.K_h):
				previous_screen = "PAUSE"
				plot.change_scene("HIGHSCORE")
			
			if _exit.press(pygame.mouse.get_pos(), 0):
				app.state = True

			[b.draw(app.screen) for b in buttons if b != start_game]
			[b.font.draw(app.screen) for b in buttons if b != start_game]
			[glow(b) for b in buttons]
			
		if plot() == "GAME_OVER":
			
			tfrags("Frags: " + str(frags))
			tlost("Lost: " + str(lost))
			tlost.color = (tlost_red, tlost_green, 0)
			traid("Raid: " + str(RM.counter))
			
			[t.draw(app.screen) for t in hud]
			
			tover.draw(app.screen)
			
			if start_game.press(pygame.mouse.get_pos(), 0, pygame.K_RETURN):
				default()
				plot.change_scene("GAME")
				
			if highscore.press(pygame.mouse.get_pos(), 0, pygame.K_h):
				previous_screen = "GAME_OVER"
				plot.change_scene("HIGHSCORE")
				
			if _exit.press(pygame.mouse.get_pos(), 0):
				app.state = True
			
			[b.draw(app.screen) for b in buttons if b != resume_game]
			[b.font.draw(app.screen) for b in buttons if b != resume_game]
			[glow(b) for b in buttons]
			
		for e in pygame.event.get():
			if e.type == pygame.QUIT:
				app.state = True

	app.run(update)
