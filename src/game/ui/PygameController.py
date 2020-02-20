from ui.Controller import Controller

import pygame, sys

from pygame.locals import *

# Implements Controller
class PygameController(Controller):

    def __init__(self, model, view):
        self._model = model
        self._view =  view

    def tick(self, deltaTime):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
        
            elif event.type == pygame.MOUSEMOTION:
                self._model.mouse_coords = pygame.mouse.get_pos()
                (x,y) = (self._model.mouse_coords[0],self._model.mouse_coords[1])
                self.current_mousex = int(x//self._view.get_mult_factor())
                self.current_mousey = int(y//self._view.get_mult_factor())