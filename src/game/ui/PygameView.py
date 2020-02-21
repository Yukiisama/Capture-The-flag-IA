from ui.View import View
from service.Config import Config

import pygame
import pygame.gfxdraw
from pygame.locals import *

from math import (ceil, floor, radians, cos, sin)

# Implements View using pygame
class PygameView(View):
    """
    Implements the Game View using the Pygame library.

    Attributes:
        model (Model)   : The data to represent.
        map (Map)       : The Map object from Model, for easier access.
    """

    DEBUG_COLLISIONMAP = 0
    DEBUG_CELL_COORDS = 1
    DEBUG_VERTICES = 2
    DEBUG_CORNERS = 3

    def __init__(self, model):
        """ 
        The constructor for PygameView.

        Stores necessary objects as attributes and computes different values used for displaying.
  
        Parameters: 
           model (Model): The data to represent.
        """
        
        self._model = model
        self._map = self._model.getMap()

        self._cell_size = min(Config.ResolutionWidth()//self._map.blockWidth, Config.ResolutionHeight()//self._map.blockHeight + 1)

        pygame.init()

        self._default_font_small = pygame.font.Font(pygame.font.get_default_font(), 24) 
        self._default_font_big = pygame.font.Font(pygame.font.get_default_font(), 64) 
        self._default_font_big_outline = pygame.font.Font(pygame.font.get_default_font(), 64) 

        self._window_rect = (self._map.blockWidth * self._cell_size, self._map.blockHeight * self._cell_size)

        self._window = pygame.display.set_mode(self._window_rect)
        self._surface = pygame.Surface(self._window_rect, pygame.SRCALPHA)

        self._mult_factor = self._cell_size/self._map.BLOCKSIZE

        self._refresh_map = True

        self.last_displayed_timer = None
        self.last_displayed_aimed = None

        self.debug = [False]*4


    def get_mult_factor(self):
        """ 
        Getter for mult_factor.

        The multiplication factor is used by the controller to determine the location of a block from a real coordinate.
  
        Returns: 
           mult_factor (double): Cellsize / Blocksize, computed during init.
        """
        return self._mult_factor

    def tick(self, deltaTime):
        """ 
        Called each tick to refresh the View.
  
        Parameters: 
           deltaTime (int): The time in milliseconds since the last call to this function.
        """
        self._display()

    def _display(self):
        """ 
        Updates the window with the current representation of the game.
        """
        self._surface.fill((0, 0, 0, 0))

        if self._refresh_map or self.debug[PygameView.DEBUG_COLLISIONMAP]:
            self._refresh_map = False

            self._display_map() 
                
        self._display_bots()
        self._display_flags()
        self._display_countdown()

        if self.debug[PygameView.DEBUG_COLLISIONMAP]:
            self.display_collision_map("RegularBot")
        if self.debug[PygameView.DEBUG_VERTICES]:
            self.display_vertices()
        if self.debug[PygameView.DEBUG_CORNERS]:
            bots = self._model.getBots()
            for bot_id in bots.keys():  
                bot = bots[bot_id] 
                self.display_corners(corners=self._model.getEngine().getBotVisibleCorners(bot))
        
        if self.debug[PygameView.DEBUG_CELL_COORDS]:
            self.display_aimed()

        self._window.blit(self._surface, (0, 0))
        pygame.display.flip()



    def _display_map(self):
        """ 
        Clears the window and draws all map blocks on screen.
        """
        pygame.draw.rect(self._window, pygame.Color(255, 255, 255, 255), pygame.Rect(0, 0, Config.ResolutionWidth(), Config.ResolutionHeight()))
        
        self._display_tiles(0,0,self._map.blockWidth - 1,self._map.blockHeight - 1)

    def _display_countdown(self):
        if self._model.cooldownremaining > 0:
            self.countdown_end = False
            to_display = ceil(self._model.cooldownremaining / 1000)

            # refresh timer surface only if it changes
            if self.last_displayed_timer != to_display: 
                to_display = '{}'.format(to_display)
                self.last_displayed_timer_text = self._default_font_big.render(to_display, True, (255,0,0,255))

                self.last_displayed_timer_text_outline = self._default_font_big_outline.render(to_display, True, (0,0,0,255))

                self.last_displayed_timer_text_rect = self.last_displayed_timer_text.get_rect()
                self.last_displayed_timer_text_outline_rect1 = self.last_displayed_timer_text.get_rect()
                self.last_displayed_timer_text_outline_rect2 = self.last_displayed_timer_text.get_rect()
                self.last_displayed_timer_text_outline_rect3 = self.last_displayed_timer_text.get_rect()
                self.last_displayed_timer_text_outline_rect4 = self.last_displayed_timer_text.get_rect()
                self.last_displayed_timer_text_outline_rect5 = self.last_displayed_timer_text.get_rect()
                self.last_displayed_timer_text_outline_rect6 = self.last_displayed_timer_text.get_rect()
                self.last_displayed_timer_text_outline_rect7 = self.last_displayed_timer_text.get_rect()
                self.last_displayed_timer_text_outline_rect8 = self.last_displayed_timer_text.get_rect()

                self.last_displayed_timer_text_rect.center = (self._window_rect[0] // 2, self._window_rect[1] // 2)

                outline_margin = 5
                self.last_displayed_timer_text_outline_rect1.center = (self._window_rect[0] // 2 + outline_margin, self._window_rect[1] // 2)
                self.last_displayed_timer_text_outline_rect2.center = (self._window_rect[0] // 2, self._window_rect[1] // 2 + outline_margin)
                self.last_displayed_timer_text_outline_rect3.center = (self._window_rect[0] // 2 - outline_margin, self._window_rect[1] // 2)
                self.last_displayed_timer_text_outline_rect4.center = (self._window_rect[0] // 2, self._window_rect[1] // 2 - outline_margin)
                self.last_displayed_timer_text_outline_rect5.center = (self._window_rect[0] // 2 + outline_margin, self._window_rect[1] // 2 + outline_margin)
                self.last_displayed_timer_text_outline_rect6.center = (self._window_rect[0] // 2 + outline_margin, self._window_rect[1] // 2 - outline_margin)
                self.last_displayed_timer_text_outline_rect7.center = (self._window_rect[0] // 2 - outline_margin, self._window_rect[1] // 2 + outline_margin)
                self.last_displayed_timer_text_outline_rect8.center = (self._window_rect[0] // 2 - outline_margin, self._window_rect[1] // 2 - outline_margin)

            self._window.blit(self.last_displayed_timer_text_outline, self.last_displayed_timer_text_outline_rect1)
            self._window.blit(self.last_displayed_timer_text_outline, self.last_displayed_timer_text_outline_rect2)
            self._window.blit(self.last_displayed_timer_text_outline, self.last_displayed_timer_text_outline_rect3)
            self._window.blit(self.last_displayed_timer_text_outline, self.last_displayed_timer_text_outline_rect4)
            self._window.blit(self.last_displayed_timer_text_outline, self.last_displayed_timer_text_outline_rect5)
            self._window.blit(self.last_displayed_timer_text_outline, self.last_displayed_timer_text_outline_rect6)
            self._window.blit(self.last_displayed_timer_text_outline, self.last_displayed_timer_text_outline_rect7)
            self._window.blit(self.last_displayed_timer_text_outline, self.last_displayed_timer_text_outline_rect8)
            self._window.blit(self.last_displayed_timer_text, self.last_displayed_timer_text_rect)
            self._refresh_map = True
        elif not self.countdown_end:
            self.countdown_end = True
            self._refresh_map = True
            
    def display_collision_map(self, name):
        try:

            self._window.blit(self.collision_surface, (0, 0))
        except:
            collision_map = self._model.getEngine().collisions_maps[name]
            divider = self._model.getEngine().collisions_maps_dividers[name]

            self.collision_surface = pygame.Surface(self._window_rect, pygame.SRCALPHA)

            (x,y) = (0,0)
            for line in collision_map:
                for dot in line:
                    if dot:

                        current_rect = pygame.Rect(
                            int(x * self._cell_size // divider),
                            int(y * self._cell_size // divider),
                            round(self._cell_size / divider),
                            round(self._cell_size / divider)
                        )
                        
                        (r, g, b, a) = (255,0,0,60)

                        pygame.draw.rect(self.collision_surface, pygame.Color(r, g, b, a), current_rect)
                    y += 1
                x += 1
                y = 0

    def display_vertices(self, start_x = 0, start_y = 0, end_x = None, end_y = None):
        """
        """
        if end_x == None:
            end_x = self._map.blockWidth
        if end_y == None:
            end_y = self._map.blockHeight

        polygons = self._model.getEngine().GetAllNonTransparentVertices(start_x, start_y, end_x, end_y)
        for vertices in polygons:
            
            current = 0
            for line in range(0,len(vertices)):
                A = vertices[current]
                B = vertices[current+1 if current != len(vertices)-1 else 0]
                pygame.draw.line(
                    self._window,
                    pygame.Color(255,0,0),
                    (A[0] * self.get_mult_factor(), A[1] * self.get_mult_factor()),
                    (B[0] * self.get_mult_factor(), B[1] * self.get_mult_factor())
                )

                current += 1

    def display_corners(self, start_x = 0, start_y = 0, end_x = None, end_y = None, corners = None):
        """
        """
        if end_x == None:
            end_x = self._map.blockWidth
        if end_y == None:
            end_y = self._map.blockHeight

        if corners == None:
            points = self._model._map.GetAllNonTransparentCorners(start_x, start_y, end_x, end_y)
        else:
            points = corners

        for point in points:

            pygame.gfxdraw.aacircle(
                self._window,
                int(point[0] * self.get_mult_factor()),
                int(point[1] * self.get_mult_factor()),
                5,
                pygame.Color(255,0,0)
            )

    def display_aimed(self):
        # refresh aimed cell only if changed
        to_display = (self._model.mouse_coords[0] // self._cell_size,self._model.mouse_coords[1] // self._cell_size)

        if self.last_displayed_aimed != to_display: 
            to_display = '(x{},y{})'.format(to_display[0],to_display[1])
            self.last_displayed_aimed_text = self._default_font_small.render(to_display, True, (0,0,0,255))

        self._window.blit(self.last_displayed_aimed_text, self.last_displayed_aimed_text.get_rect())
        



    def _display_tiles(self, start_x, start_y, end_x, end_y):
        """ 
        Draws map blocks contained in a rectangle selection.
  
        Parameters: 
           start_x (int): Top-left block X of the selection, X coordinate in blocks.
           start_y (int): Top-left block Y of the selection, Y coordinate in blocks.
           end_x (int): Bottom-right block of the selection, X coordinate in blocks.
           end_y (int): Bottom-right block of the selection, Y coordinate in blocks.
        """
        for y in range(start_y, end_y + 1):
            for x in range(start_x, end_x + 1):
                current_rect = pygame.Rect(
                    x * self._cell_size,
                    y * self._cell_size,
                    self._cell_size,
                    self._cell_size
                )
                
                (r, g, b, a) = self._map.blocks[x][y].color

                pygame.draw.rect(self._window, pygame.Color(r, g, b, a), current_rect)

    def _display_flags(self):
        """
        Draws flags. 

        Use only on a map that has flags.
        """

        for flag in self._map.flags:
            current_rect = pygame.Rect(
                flag.x * self._mult_factor - (self._cell_size - flag.width * self._mult_factor)//2,
                flag.y * self._mult_factor - (self._cell_size - flag.height * self._mult_factor)//2,
                flag.width * self._mult_factor,
                flag.height * self._mult_factor
            )
                
            (r, g, b, a) = flag.color
            pygame.draw.rect(self._window, pygame.Color(r, g, b, a), current_rect)

    def _display_bots(self):
        """ 
        Draws every bot from the model and updates their adjacent tiles as well.
        """
        bots = self._model.getBots()

        tiles_to_refresh = dict()

        for bot_id in bots.keys():  
            bot = bots[bot_id]  
            x_tile = int(bot.x // self._map.BLOCKSIZE)
            y_tile = int(bot.y // self._map.BLOCKSIZE)

            if not x_tile in tiles_to_refresh.keys():
                tiles_to_refresh[x_tile] = dict()
            tiles_to_refresh[x_tile][y_tile] = 1

        for x_tile in tiles_to_refresh.keys():
            for y_tile in tiles_to_refresh[x_tile].keys():

                start_x = x_tile - 5
                start_y = y_tile - 5
                end_x = x_tile + 5
                end_y = y_tile + 5

                if(start_x < 0):
                    start_x = 0
                if(start_y < 0):
                    start_y = 0
                if(end_x >= self._map.blockWidth):
                    end_x = self._map.blockWidth - 1
                if(end_y >= self._map.blockHeight):
                    end_y = self._map.blockHeight - 1

                self._display_tiles(start_x,start_y,end_x,end_y)

        for bot_id in bots.keys():  
            bot = bots[bot_id] 
            (r, g, b, a) = bot.color
            
            bot_radius = int(bot.radius * self._mult_factor)
            (x, y) = (bot.x, bot.y)

            x *= self._mult_factor
            y *= self._mult_factor

            self._draw_cone(
                x,
                y, 
                pygame.Color(r, g, b, 70),
                bot.view_distance * self._mult_factor,
                int(bot.angle - bot.fov),
                int(bot.angle + bot.fov),
                10
            )

            pygame.gfxdraw.aacircle(
                self._window,
                int(x),
                int(y),
                bot_radius,
                pygame.Color(r, g, b)
            )

            pygame.draw.line(
                self._window,
                pygame.Color(r, g, b),
                (int(x), int(y)),
                (
                    int(x + cos(radians(bot.angle)) * 1.5 * bot_radius),
                    int(y + sin(radians(bot.angle)) * 1.5 * bot_radius)
                )
            )

    def _draw_cone(self, x, y, color, length, angle_start, angle_end, step = 1):
        """ 
        Draws a cone.
  
        Parameters: 
           x (int): The screen x coordinate.
           y (int): The screen y coordinate.
           color (r,g,b,a): RGBA tuple.
           length (int): The diameter of the circle containing the cone.
           angle_start (int): The angle at which the cone starts within the circle.
           angle_end (int): The angle at which the cone ends within the circle.
           step (int): The cone is made of triangles, a lower step makes a more precise curve.
        """
        angle_start = float(angle_start)
        angle_end = float (angle_end)

        angle_step = 0 if step <= 0 else (angle_end -  angle_start)/step

        old_x = x
        old_y = y

        x = length
        y = length

        points = [(x, y), (x + cos(radians(angle_start)) * length, y + sin(radians(angle_start)) * length)]

        for i in range(step):
            points.append(
                (x + cos(radians(angle_start + angle_step * i)) * length, y + sin(radians(angle_start + angle_step * i)) * length)
            )

        points.append((x + cos(radians(angle_end)) * length, y + sin(radians(angle_end)) * length))
        points.append((x, y))

        self.cone_surface = pygame.Surface((length * 2, length * 2), pygame.SRCALPHA)

        pygame.draw.polygon(
            self.cone_surface,
            color,
            points
        )

        self._window.blit(self.cone_surface, (old_x - length, old_y - length))

    def debug_switch(self, debugmode):
        self.debug[debugmode] = not self.debug[debugmode]
        self._refresh_map = True
