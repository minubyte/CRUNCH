import pygame
import math
import random

from utils import *

unit = 24
gravity = 0.7

tile_img = pygame.Surface((unit, unit))
tile_img.fill("#494d7e")

def sign(num):
    if num > 0:
        return 1
    elif num < 0:
        return -1
    return 0

class Particle:
    def __init__(self, x, y, size, angle, speed, color="#fbf5ef", outline=0):
        self.rect = pygame.FRect(x-size/2, y-size/2, size, size)
        self.angle = math.radians(angle)
        self.speed = speed
        self.color = color
        self.outline = outline
    
    def update(self, dt):
        self.rect.x += math.cos(self.angle)*self.speed
        self.rect.y += math.sin(self.angle)*self.speed
        self.speed *= 0.9**dt
        self.rect.w *= 0.9**dt
        self.rect.h *= 0.9**dt

class Player:
    def __init__(self, pos):
        self.img = pygame.Surface((unit, unit))
        self.img.fill("#f2d3ab")
        self.rect = self.img.get_frect(topleft=pos)
        self.speed = 7
        self.jump_force = 11.5
        self.jump_length = 7
        self.jump_timer = 0
        self.jump_early = 0
        self.falling = 0
        self.movement = [0, 0]
        self.last_x = 0

    def update(self, dt, tiles, particles):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_d] and not keys[pygame.K_a]:
            self.movement[0] += (1-self.movement[0])/7*dt
        elif keys[pygame.K_a] and not keys[pygame.K_d]:
            self.movement[0] += (-1-self.movement[0])/7*dt
        else:
            self.movement[0] += -self.movement[0]/5*dt

        self.movement[1] += gravity
        self.movement[1] = max(self.movement[1], -15)

        self.rect.x += self.movement[0]*self.speed*dt
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.movement[0] > 0:
                    self.rect.right = tile.left
                elif self.movement[0] < 0:
                    self.rect.left = tile.right

        self.rect.y += self.movement[1]*dt
        for tile in tiles:
            if self.rect.colliderect(tile):
                if self.movement[1] > 0:
                    self.rect.bottom = tile.top
                    self.falling = 0
                    self.movement[1] = 0
                elif self.movement[1] < 0: 
                    self.rect.top = tile.bottom
                    self.movement[1] = 0

        self.falling += dt

        if self.jump_early > 0:
            self.jump_early -= dt
            if self.falling < 6:
                self.jump()

        if not keys[pygame.K_SPACE]:
            self.jump_timer = 99
        elif self.jump_timer < self.jump_length:
            self.movement[1] = -self.jump_force
            self.jump_timer += dt
        
        if abs(self.last_x-self.rect.x) > 10 and self.falling < 6:
            self.last_x = self.rect.x
            particles.append(Particle(self.rect.centerx, self.rect.bottom, random.randint(5, 7), random.randint(-15, 15)+(sign(self.movement[0])+1)*90, random.randint(2, 2+int(abs(self.movement[0]*5)))))

    def jump(self):
        if self.falling < 6:
            self.falling = 99
            self.movement[1] = -self.jump_force
            self.jump_timer = 0
        else:
            self.jump_early = 6

def rect_ofs(rect: pygame.Rect, pos):
    return rect.copy().move(pos)

class Level:
    def __init__(self, screen, gm):
        self.screen = screen
        self.gm = gm
        self.tiles = []
        self.particles = []

        self.cam_offset = [0, 0]

        self.paused = False
        self.pause_t = 0

        level_img = pygame.image.load("data/level.png").convert()
        level_img_size = level_img.get_size()
        self.level_size = [level_img_size[0]*unit, level_img_size[1]*unit]
        self.player_y = 0
        self.player = None
        for x in range(level_img_size[0]):
            for y in range(level_img_size[1]):
                pixel = level_img.get_at((x, y))
                if pixel == (0, 0, 0, 255):
                    self.tiles.append(pygame.Rect(x*unit, y*unit, unit, unit))
                elif pixel == (255, 0, 0, 255):
                    self.player = Player([x*unit, y*unit])
                    self.player_y = y*unit

    def run(self, dt, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if not self.paused:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                        for i in range(4):
                            self.particles.append(Particle(self.player.rect.centerx, self.player.rect.bottom, random.randint(5, 10), random.randint(-30, 30)-90, random.randint(2, 5)))
                if event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
                    self.pause_t = 0

        self.screen.fill("#272744")
        self.gm.t.update(dt)

        for i in range(0, self.level_size[0], 120):
            pygame.draw.line(self.screen, light_color, [i+self.cam_offset[0]/2, 0], [i+self.cam_offset[0]/2, screen_height], 40)
        for i in range(0, screen_height, 120):
            pygame.draw.line(self.screen, light_color, [0, i+self.cam_offset[1]/2], [screen_width, i+self.cam_offset[1]/2], 40)

        for tile in self.tiles:
            self.screen.blit(tile_img, rect_ofs(tile, self.cam_offset))
        self.screen.blit(self.player.img, rect_ofs(self.player.rect, self.cam_offset))
                    
        if not self.paused:
            self.cam_offset[0] += (screen_width/2-(self.player.rect.x+self.player.movement[0]*self.player.speed*6)-self.cam_offset[0])/5*dt
            self.cam_offset[1] += (self.level_size[1]-screen_height+self.player_y-self.player.rect.y-self.cam_offset[1])/50*dt

            self.cam_offset[0] = max(min(self.cam_offset[0], -unit), screen_width-self.level_size[0]+unit)
            self.cam_offset[1] = max(self.cam_offset[1], self.level_size[1]-screen_height)

            for particle in reversed(self.particles):
                if particle.rect.w <= 0.1:
                    self.particles.remove(particle)
                pygame.draw.rect(self.screen, particle.color, rect_ofs(particle.rect, self.cam_offset), particle.outline)
                particle.update(dt)
            self.player.update(dt, self.tiles, self.particles)
        else:
            self.screen.blit(dim, (0, 0))
            if self.pause_t < 60:
                self.pause_t += dt
            ofs = e_out(self.pause_t/60)*20
            draw_text(self.screen, "PAUSED", 200+ofs, 200, font=font48_b, outline=True)
            draw_text(self.screen, "options", 200+ofs, 200+80)
            draw_text(self.screen, "exit", 200+ofs, 200+120)
    
        self.gm.t.draw(self.screen)