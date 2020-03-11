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

        self._cellSize = min(Config.ResolutionWidth()//self._map.blockWidth, Config.ResolutionHeight()//self._map.blockHeight + 1)

        pygame.init()

        self._default_font_small = pygame.font.Font(pygame.font.get_default_font(), 24) 
        self._default_font_big = pygame.font.Font(pygame.font.get_default_font(), 64) 
        self._defaultFontBigOutline = pygame.font.Font(pygame.font.get_default_font(), 64) 

        self._windowRect = (self._map.blockWidth * self._cellSize, self._map.blockHeight * self._cellSize)

        self._window = pygame.display.set_mode(self._windowRect)
        self._surface = pygame.Surface(self._windowRect, pygame.SRCALPHA)

        self._multFactor = self._cellSize/self._map.BLOCKSIZE

        self._refreshMap = True

        self._texts = dict()

        self.last_displayed_timer = None
        self.last_displayed_aimed = None

        self.countdownEnd = None
        self.debug = [False]*4


    def getMultFactor(self):
        """ 
        Getter for multFactor.

        The multiplication factor is used by the controller to determine the location of a block from a real coordinate.
  
        Returns: 
           multFactor (double): Cellsize / Blocksize, computed during init.
        """
        return self._multFactor

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

        if self._refreshMap or self.debug[PygameView.DEBUG_COLLISIONMAP]:
            self._refreshMap = False

            self._displayMap() 
                
        self._displayBots()
        self._displayFlags()
        self._displayCountdown()

        if self.debug[PygameView.DEBUG_COLLISIONMAP]:
            self.displayCollisionMap("RegularBot")
        if self.debug[PygameView.DEBUG_VERTICES]:
            self.displayVertices()
        if self.debug[PygameView.DEBUG_CORNERS]:
            bots = self._model.getBots()
            for bot_id in bots.keys():  
                bot = bots[bot_id] 
                self.displayCorners(corners=self._model.getEngine().getBotVisibleCorners(bot))
        
        if self.debug[PygameView.DEBUG_CELL_COORDS]:
            self.displayAimed()

        self._window.blit(self._surface, (0, 0))
        pygame.display.flip()



    def _displayMap(self):
        """ 
        Clears the window and draws all map blocks on screen.
        """
        pygame.draw.rect(self._window, pygame.Color(255, 255, 255, 255), pygame.Rect(0, 0, Config.ResolutionWidth(), Config.ResolutionHeight()))
        
        self._displayTiles(0,0,self._map.blockWidth - 1,self._map.blockHeight - 1)

    def _displayGameOver(self):
        """
        Displays the winner in the middle of the screen.
        """
        if self._model.game_over and self._model.winner != None:
            self._displayOutlinedText("game_over", "Red wins !" if self._model.winner == 1 else "Blue wins !", 5, (255,0,0,255) if self._model.winner == 1 else (0,0,255,255))

    def _displayOutlinedText(self, id, text, outline, color):
        """
        Displays a text with an outline and creates it if not already created.
        """
        if not id in self._texts.keys():
            self._texts[id] = { "text" : None, "outline" : None, "color" : None, "displays" : dict()}

        outlines = 8

        toDisplay = '{}'.format(text)
        if self._texts[id]["text"] != toDisplay or self._texts[id]["outline"] != outline or self._texts[id]["color"] != color:
            self._texts[id]["text"] = toDisplay
            self._texts[id]["outline"] = outline
            self._texts[id]["color"] = color

            self._texts[id]["displays"]["main"] = self._default_font_big.render(self._texts[id]["text"], True, self._texts[id]["color"])
            self._texts[id]["displays"]["main_rect"] = self._texts[id]["displays"]["main"].get_rect()
            self._texts[id]["displays"]["main_rect"].center = (self._windowRect[0] // 2, self._windowRect[1] // 2)

            self._texts[id]["displays"]["outline"] = self._defaultFontBigOutline.render(self._texts[id]["text"], True, (0,0,0,255))
            
            self._texts[id]["displays"]["outline_rects"] = []
            for i in range(0,outlines):
                new_rect = self._texts[id]["displays"]["main"].get_rect()
                new_rect.center = (self._windowRect[0] // 2, self._windowRect[1] // 2)
                self._texts[id]["displays"]["outline_rects"].append(new_rect)

            for i in range(0,outlines):
                if i < 3:
                    self._texts[id]["displays"]["outline_rects"][i].x += self._texts[id]["outline"]
                    if i == 0:
                        self._texts[id]["displays"]["outline_rects"][i].y += self._texts[id]["outline"]
                    elif i == 1:
                        self._texts[id]["displays"]["outline_rects"][i].y -= self._texts[id]["outline"]
                        
                elif i < 6:
                    self._texts[id]["displays"]["outline_rects"][i].x -= self._texts[id]["outline"]
                    if i == 3:
                        self._texts[id]["displays"]["outline_rects"][i].y += self._texts[id]["outline"]
                    elif i == 4:
                        self._texts[id]["displays"]["outline_rects"][i].y -= self._texts[id]["outline"]
                        
                else:
                    if i == 6:
                        self._texts[id]["displays"]["outline_rects"][i].y += self._texts[id]["outline"]
                    else:
                        self._texts[id]["displays"]["outline_rects"][i].y -= self._texts[id]["outline"]

        for rect in self._texts[id]["displays"]["outline_rects"]:
            self._window.blit(self._texts[id]["displays"]["outline"], rect)
        self._window.blit(self._texts[id]["displays"]["main"], self._texts[id]["displays"]["main_rect"])


    def _displayCountdown(self):
        """
        Displays the remaining countdown time in seconds in the middle of the screen.
        """
        if self._model.countdownremaining > 0:
            self.countdownEnd = False
            toDisplay = ceil(self._model.countdownremaining / 1000)

            self._displayOutlinedText("countdown", toDisplay, 5, (255,0,255,255))
            self._refreshMap = True
        elif not self.countdownEnd:
            self.countdownEnd = True
            self._refreshMap = True
            
    def displayCollisionMap(self, name):
        try:

            self._window.blit(self.collision_surface, (0, 0))
        except:
            collision_map = self._model.getEngine().collisionsMaps[name]
            divider = self._model.getEngine().collisionsMapsDividers[name]

            self.collision_surface = pygame.Surface(self._windowRect, pygame.SRCALPHA)

            (x,y) = (0,0)
            for line in collision_map:
                for dot in line:
                    if dot:

                        current_rect = pygame.Rect(
                            int(x * self._cellSize // divider),
                            int(y * self._cellSize // divider),
                            round(self._cellSize / divider),
                            round(self._cellSize / divider)
                        )
                        
                        (r, g, b, a) = (255,0,0,60)

                        pygame.draw.rect(self.collision_surface, pygame.Color(r, g, b, a), current_rect)
                    y += 1
                x += 1
                y = 0

    def displayVertices(self, start_x = 0, start_y = 0, end_x = None, end_y = None):
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
                    (A[0] * self.getMultFactor(), A[1] * self.getMultFactor()),
                    (B[0] * self.getMultFactor(), B[1] * self.getMultFactor())
                )

                current += 1

    def displayCorners(self, start_x = 0, start_y = 0, end_x = None, end_y = None, corners = None):
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
                int(point[0] * self.getMultFactor()),
                int(point[1] * self.getMultFactor()),
                5,
                pygame.Color(255,0,0)
            )

    def displayAimed(self):
        # refresh aimed cell only if changed
        to_display = (self._model.mouse_coords[0] // self._cellSize,self._model.mouse_coords[1] // self._cellSize)

        if self.last_displayed_aimed != to_display: 
            to_display = '(x{},y{})'.format(to_display[0],to_display[1])
            self.last_displayed_aimed_text = self._default_font_small.render(to_display, True, (0,0,0,255))

        self._window.blit(self.last_displayed_aimed_text, self.last_displayed_aimed_text.get_rect())
        



    def _displayTiles(self, startX, startY, endX, endY):
        """ 
        Draws map blocks contained in a rectangle selection.
  
        Parameters: 
           startX (int): Top-left block X of the selection, X coordinate in blocks.
           startY (int): Top-left block Y of the selection, Y coordinate in blocks.
           endX (int): Bottom-right block of the selection, X coordinate in blocks.
           endY (int): Bottom-right block of the selection, Y coordinate in blocks.
        """
        for y in range(startY, endY + 1):
            for x in range(startX, endX + 1):
                currentRect = pygame.Rect(
                    x * self._cellSize,
                    y * self._cellSize,
                    self._cellSize,
                    self._cellSize
                )
                
                (r, g, b, a) = self._map.blocks[x][y].color

                pygame.draw.rect(self._window, pygame.Color(r, g, b, a), currentRect)

    def _displayFlags(self):
        """
        Draws flags. 

        Use only on a map that has flags.
        """

        for flag in self._map.flags:
            currentRect = pygame.Rect(
                flag.x * self._multFactor - (self._cellSize - flag.width * self._multFactor)//2,
                flag.y * self._multFactor - (self._cellSize - flag.height * self._multFactor)//2,
                flag.width * self._multFactor,
                flag.height * self._multFactor
            )
                
            (r, g, b, a) = flag.color
            pygame.draw.rect(self._window, pygame.Color(r, g, b, a), currentRect)

    def _displayBots(self):
        """ 
        Draws every bot from the model and updates their adjacent tiles as well.
        """
        bots = self._model.getBots()

        tilesToRefresh = dict()

        for botId in bots.keys():  
            bot = bots[botId]  
            xTile = int(bot.x // self._map.BLOCKSIZE)
            yTile = int(bot.y // self._map.BLOCKSIZE)

            if not xTile in tilesToRefresh.keys():
                tilesToRefresh[xTile] = dict()
            tilesToRefresh[xTile][yTile] = 1

        for xTile in tilesToRefresh.keys():
            for yTile in tilesToRefresh[xTile].keys():

                startX = xTile - 5
                startY = yTile - 5
                endX = xTile + 5
                endY = yTile + 5

                if(startX < 0):
                    startX = 0
                if(startY < 0):
                    startY = 0
                if(endX >= self._map.blockWidth):
                    endX = self._map.blockWidth - 1
                if(endY >= self._map.blockHeight):
                    endY = self._map.blockHeight - 1

                self._displayTiles(startX,startY,endX,endY)

        for botId in bots.keys():  
            bot = bots[botId] 
            (r, g, b, a) = bot.color
            
            botRadius = int(bot.radius * self._multFactor)
            (x, y) = (bot.x, bot.y)

            x *= self._multFactor
            y *= self._multFactor
            
            self._drawCone(
                x,
                y, 
                pygame.Color(r, g, b, 70),
                bot.viewDistance * self.getMultFactor(),
                int(bot.angle - bot.fov),
                int(bot.angle + bot.fov),
                10
            )

            pygame.gfxdraw.aacircle(
                self._window,
                int(x),
                int(y),
                botRadius,
                pygame.Color(r, g, b)
            )

            pygame.draw.line(
                self._window,
                pygame.Color(r, g, b),
                (int(x), int(y)),
                (
                    int(x + cos(radians(bot.angle)) * 1.5 * botRadius),
                    int(y + sin(radians(bot.angle)) * 1.5 * botRadius)
                )
            )

    def _drawCone(self, x, y, color, length, angleStart, angleEnd, step = 1):
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
        angleStart = float(angleStart)
        angleEnd = float (angleEnd)

        angleStep = 0 if step <= 0 else (angleEnd -  angleStart)/step

        oldX = x
        oldY = y

        x = length
        y = length

        points = [(x, y), (x + cos(radians(angleStart)) * length, y + sin(radians(angleStart)) * length)]

        for i in range(step):
            points.append(
                (x + cos(radians(angleStart + angleStep * i)) * length, y + sin(radians(angleStart + angleStep * i)) * length)
            )

        points.append((x + cos(radians(angleEnd)) * length, y + sin(radians(angleEnd)) * length))
        points.append((x, y))

        self.coneSurface = pygame.Surface((length * 2, length * 2), pygame.SRCALPHA)

        pygame.draw.polygon(
            self.coneSurface,
            color,
            points
        )
        
        self._window.blit(self.coneSurface, (oldX - length, oldY - length))

    def debug_switch(self, debugmode):
        self.debug[debugmode] = not self.debug[debugmode]
        self._refreshMap = True

    def debug_switch(self, debugmode):
        self.debug[debugmode] = not self.debug[debugmode]
        self._refreshMap = True