import pygame
import math
from easing_functions import *

screen_width, screen_height = 1280, 720

dim = pygame.Surface((screen_width, screen_height))
dim.set_alpha(100)

q_out = QuadEaseOut()
q_in = QuadEaseIn()

e_out = ElasticEaseOut()
e_in = ElasticEaseIn()

def stack_colors(bg, fg, a=100):
    bg_img = pygame.Surface((1, 1))
    bg_img.fill(bg)
    fg_img = pygame.Surface((1, 1))
    fg_img.fill(fg)
    fg_img.set_alpha(a)
    bg_img.blit(fg_img, (0, 0))
    return bg_img.get_at([0, 0])

light_color = stack_colors("#272744", "#494d7e", 50)

font24 = pygame.font.Font("data/Galmuri7.ttf", 24)
font48_b = pygame.font.Font("data/Galmuri11-Bold.ttf", 48)

def draw_text(screen, text, x=100, y=100, color="#fbf5ef", ofs=0, outline=False, font=font24):
    render = font.render(text, False, color)
    if outline:
        render = outlined(render)
    screen.blit(render, (x-render.get_width()*ofs, y)) 

def load_img(name, scale=1):
    img = pygame.image.load(f"data/{name}.png")
    img.set_colorkey("#000000")
    return pygame.transform.scale_by(img, scale)

def outlined(img, color="#494d7e"):
    width = 4
    base_img = pygame.Surface((img.get_width()+4, img.get_height()+4))
    mask = pygame.mask.from_surface(img).to_surface(setcolor=color)
    mask.set_colorkey("#000000")
    for x in [-width, 0, width]:
        for y in [-width, 0, width]:
            base_img.blit(mask, (x+width, y+width))
    base_img.blit(img, (width, width))
    base_img.set_colorkey("#000000")
    return base_img

mult = math.dist((0, 0), (screen_width, screen_height))

class Transition:
    def __init__(self):
        self.t = 0
        self.type = "none"
        
    def update(self, dt):
        if self.type == "out":
            self.t += dt
            if self.t >= 30:
                self.type = "in"
                return "out"
        elif self.type == "in":
            self.t -= dt
            if self.t <= 0:
                self.type = "none"
                return "in"
    
    def draw(self, screen):
        pygame.draw.line(screen, "#000000", [0, 0], [screen_width, screen_height], int(q_out(self.t/30)*mult))

    # def get(self):
    #     return self.t

    def set(self, type):
        self.type = type