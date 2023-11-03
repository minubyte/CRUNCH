import pygame
import math

from utils import *

logo = outlined(load_img("crunch", 4))
logo_size = logo.get_size()

class Menu:
    def __init__(self, screen, gm):
        self.screen: pygame.Surface = screen
        self.gm = gm

    def run(self, dt, events):
        t = pygame.time.get_ticks()
        self.screen.fill("#272744")
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.gm.t.set("out")

        for i in range(10):
            pygame.draw.line(self.screen, "#494d7e", [screen_width/2+math.cos((t+i*300)/200)*10, screen_width/10*i], [screen_width/2+math.cos((t+i*300)/200)*10, screen_width/10*(i+1)], 8)
        self.screen.blit(logo, (screen_width/2-logo_size[0]/2, screen_height/2-logo_size[1]/2+math.cos(t/400)*10))
        draw_text(self.screen, "press [space] to start", screen_width/2, screen_height-200+math.cos(t/500)*5, outline=True, ofs=0.5)
        
        if self.gm.t.update(dt) == "out":
            self.gm.set("level")
        self.gm.t.draw(self.screen)