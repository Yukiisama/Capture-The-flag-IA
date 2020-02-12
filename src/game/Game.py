#! /usr/bin/env python3

import sys

from ui.PygameFactory import PygameFactory
from model import *
from service.TimeManager import TimeManager
from service.Config import Config
from service.Physics import *

from time import sleep

class Game:
    def __init__(self, Player1, Player2):
        Config.Initialize()

        Physics.SetInstance(PythonPhysics())

        uiFactory = PygameFactory()

        self.View       = uiFactory.getView()
        self.Controller = uiFactory.getController()
        self.Model      = GameModel(Player1, Player2)


    def gameLoop(self):
        print("Game starting")
        
        running = True

        runningStopwatch = TimeManager()
        runningStopwatch.StartTimer()

        while running:

            deltaTime = runningStopwatch.NextFrame()
                
            runningStopwatch.Mark()

            self.Controller.tick(deltaTime)
            self.View.tick(deltaTime)

            # running = False # Game over

        runningStopwatch.StopTimer()

        print("Game closing")
        pass

# Make this an executable file
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("usage : ./Game.py <PlayerFile1> <PlayerFile2>")

    exec("import {} as PlayerPackage1".format(sys.argv[1]))
    exec("import {} as PlayerPackage2".format(sys.argv[2]))

    game = Game(PlayerPackage1.myPlayer,PlayerPackage2.myPlayer)
    game.gameLoop() 