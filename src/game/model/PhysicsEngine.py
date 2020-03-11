from service.Physics import Physics
from service.Config import Config
from domain.Map import Map

class PhysicsEngine(Physics):
    """
    Methods used to apply physics to the game world

    Attributes:
        ruleset (Ruleset) : The set of rules needed to make objects behave
        map (Map) : The game world
        deltaTime (int) : Time in milliseconds since last tick
    """

    def __init__(self, ruleset, map_):
        self._ruleset = ruleset
        self._map = map_

        self.collisionsMaps = dict()
        self.collisionsMapsDividers = dict()


    def tick(self, deltaTime):
        """
        Update deltaTime
        """
        self.deltaTime = deltaTime

    def checkSpeed(self, bot, targetSpeed):
        """
        Checks whether a target speed is correct for a bot.

        Returns:
            targetSpeed (int) : A correct target speed for this bot.
        """
        maxSpeed = float(self._ruleset["SpeedMultiplier"]) * bot.maxSpeed

        if targetSpeed > maxSpeed:
            targetSpeed = maxSpeed
        if targetSpeed < 0:
            targetSpeed = 0

        return targetSpeed

    def checkAngle(self, bot, targetX, targetY):
        """
        Checks whether a target point is correct for a bot.

        Returns:
            target_angle (int) : A correct target angle for this bot.
        """
        newAngle = Physics.getAngle( bot.x, bot.y, targetX, targetY)

        deltaAngle = newAngle - bot.angle

        if deltaAngle > 180:
            deltaAngle = deltaAngle - 360

        elif deltaAngle < -180:
            deltaAngle = 360 + deltaAngle
        
        maxAngle = float(self._ruleset["RotationMultiplier"]) * bot.maxRotate
        maxAngle = maxAngle * self.getDeltaTimeModifier()

        if abs(deltaAngle) > maxAngle :
            deltaAngle = maxAngle if deltaAngle > 0 else -maxAngle
            
        return bot.angle + deltaAngle

    def getDeltaTimeModifier(self):
        """
        This is the multiplier for all physics operations, since deltaTime can be inconsistent.
        """
        return (self.deltaTime / (1000 / (30 * Config.TimeRate())))

    def checkCollision(self, collisionMap, x, y, targetX, targetY, capX, capY):
        """
        Checks whether a target's path collides with the map.

        Returns:
            position (int,int) : The first valid position.
        """
        
        dx = abs(targetX - x)
        dy = abs(targetY - y)

        currentX = x
        currentY = y

        lastX = x
        lastY = y

        n = int(1 + dx + dy)

        xInc = 1 if (targetX > x) else -1
        yInc = 1 if (targetY > y) else -1

        error = dx - dy

        dx *= 2
        dy *= 2
        
        for i in range(n, 0, -1):

            if capX != None and capY != None and capX == lastX and capY == lastY:
                return (lastX,lastY)
            
            if self.collisionsMaps[collisionMap][int(currentX // self.collisionsMapsDividers[collisionMap])][int(currentY // self.collisionsMapsDividers[collisionMap])]:
                return (lastX, lastY)

            lastX = currentX
            lastY = currentY

            if error > 0:
                currentX += xInc
                error -= dy
            elif error < 0:
                currentY += yInc
                error += dx
            elif error == 0:
                currentX += xInc
                currentY += yInc
                error -= dy
                error += dx
                n -= 1
                
        return (targetX, targetY)

    def checkVisible(self, x, y, target_x, target_y, max_distance = None):
        """
        Checks whether a target's path collides with the map.

        Returns:
            position (int,int) : The first valid position.
        """

        if max_distance != None and Physics.distance(x,target_x,y,target_y) > max_distance:
            return False
            
        dx = abs(target_x - x)
        dy = abs(target_y - y)

        current_x = x
        current_y = y

        last_x = x
        last_y = y

        n = int(1 + dx + dy)

        x_inc = 1 if (target_x > x) else -1
        y_inc = 1 if (target_y > y) else -1

        error = dx - dy

        dx *= 2
        dy *= 2
        
        for i in range(n, 1, -1):
            
            if not self._map.blocks[int(current_x // Map.BLOCKSIZE)][int(current_y // Map.BLOCKSIZE)].transparent:
                return False

            last_x = current_x
            last_y = current_y

            if error > 0:
                current_x += x_inc
                error -= dy
            elif error < 0:
                current_y += y_inc
                error += dx
            elif error == 0:
                current_x += x_inc
                current_y += y_inc
                error -= dy
                error += dx
                n -= 1
                
        return True

    def createCollisionMap(self, name, padding):

        divider = 10 # 1 / round(Map.BLOCKSIZE / padding)
        self.collisionsMapsDividers[name] = divider

        collisionsMapPadding = int(padding // (Map.BLOCKSIZE // divider))
        collisionsMapWidth = int(self._map.blockWidth * divider)
        collisionsMapHeight = int(self._map.blockHeight * divider)

        self.collisionsMaps[name] = [[False for i in range(0,collisionsMapHeight)] for j in range(0,collisionsMapWidth)]

        blockSizeFactored = int(Map.BLOCKSIZE // divider)

        (x,y) = (0,0)
        for blockline in self._map.blocks:
            for block in blockline:
                if block.solid:
                    for rx in range(- collisionsMapPadding, blockSizeFactored + collisionsMapPadding):
                        for ry in range(- collisionsMapPadding, blockSizeFactored + collisionsMapPadding):
                            nx = int(x + rx)
                            ny = int(y + ry)
                            
                            if nx >= 0 and ny >= 0 and nx < collisionsMapWidth and ny < collisionsMapHeight:
                                # print("{} {}".format(nx,ny))
                                self.collisionsMaps[name][nx][ny] = True

                y += blockSizeFactored
            y = 0
            x += blockSizeFactored

    def getBotVisibleCorners(self, bot):
        corners = self.GetAllNonTransparentCorners(int(bot.x // Map.BLOCKSIZE - bot.viewDistance // Map.BLOCKSIZE),
                                                        int(bot.y // Map.BLOCKSIZE - bot.viewDistance // Map.BLOCKSIZE),
                                                        int(bot.x // Map.BLOCKSIZE + bot.viewDistance // Map.BLOCKSIZE),
                                                        int(bot.y // Map.BLOCKSIZE + bot.viewDistance // Map.BLOCKSIZE),
                                                        c_x= bot.x, c_y= bot.y, c_r= bot.viewDistance)

        reached = list()

        for corner in corners:
            if self.checkVisible(bot.x, bot.y, corner[0], corner[1], bot.viewDistance):
                reached.append(corner)

        return reached

    def GetAllNonTransparentVertices(self, start_x = 0, start_y = 0, end_x = None, end_y = None, c_x = None, c_y = None, c_r = None):
        """
        """
        if end_x == None:
            end_x = self._map.blockWidth
        if end_y == None:
            end_y = self._map.blockHeight

        polygons = list()

        for line in self._map.blocks[start_x:end_x]:
            for block in line[start_y:end_y]:
                if c_r != None:
                    if Physics.distance(c_x, block.x,c_y, block.y) > c_r:
                        continue
                if not block.transparent:
                    vertices = list()
                    vertices.append((block.x,block.y,1))
                    vertices.append((block.x + Map.BLOCKSIZE,block.y,2))
                    vertices.append((block.x + Map.BLOCKSIZE,block.y + Map.BLOCKSIZE,0))
                    vertices.append((block.x,block.y + Map.BLOCKSIZE,0))
                    polygons.append(vertices)

        return polygons

    def GetAllNonTransparentCorners(self, start_x = 0, start_y = 0, end_x = None, end_y = None, c_x = None, c_y = None, c_r = None):
        """
        """

        if end_x == None or end_x > self._map.blockWidth:
            end_x = self._map.blockWidth
        if end_y == None or end_y > self._map.blockHeight:
            end_y = self._map.blockHeight

        if start_x < 0:
            start_x = 0
        if start_y < 0:
            start_y = 0

        corners = dict()

        for vertices in self.GetAllNonTransparentVertices(start_x, start_y, end_x, end_y, c_x, c_y, c_r):
            
            for point in vertices:
                coords = (point[0], point[1])
                (x,y) = (coords[0] // Map.BLOCKSIZE,coords[1] // Map.BLOCKSIZE)
                corners[coords] = corners.get(coords, 0) + 1

                # Might not be required
                # edgeCase = False
                # force = False

                # if point[2] == 1:
                #     if x > 0 and y > 0:
                #         D = self.blocks[x-1][y-1].transparent
                #         R = self.blocks[x][y-1].transparent
                #         L = self.blocks[x-1][y].transparent
                #         M = self.blocks[x][y].transparent

                #         edgeCase = (M == D and L == R and M != L)

                # if point[2] == 2:
                #     if x < self.blockWidth - 1 and y > 0:
                #         R = self.blocks[x+1][y-1].transparent
                #         L = self.blocks[x][y-1].transparent
                #         M = self.blocks[x+1][y].transparent
                #         D = self.blocks[x][y].transparent

                #         force = (M == D and L == R and M != L)

                if corners[coords] == 2: #and not edgeCase or force:
                    del corners[coords]
                    
        for point in corners.keys():
            if corners[point] % 2 != 0:
                corners[point]

        return corners