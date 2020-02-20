from domain.Map import Map
from domain.GameObject.Block import *
from domain.GameObject.Flag import Flag
from random import *

class RegularMap(Map):
    """
    Implements Map.
    """

    def __init__(self, mapData):
        """
        Initialize the Map according to mapData.

        Parameters:
            inside mapData :
            width (int):        Width in real coordinates
            height (int):       Height in real coordinates
            blockWidth (int):   Width in amount of blocks
            blockHeight (int):  Height in amount of blocks
            blocks (list):      2 dimensional array containing the map blocks
            flags (list):       List of Flag objects
            spawns (list):      List of Spawn objects
        """
        self.blockHeight = mapData["blockHeight"]
        self.blockWidth = mapData["blockWidth"]
        self.height = mapData["height"]
        self.width = mapData["width"]
        self.blocks = mapData["blocks"]
        self.flags = mapData["flags"]
        self._spawns = mapData["spawns"]
        self._bots = list()

    @staticmethod
    def loadMapData(filename):
        """
        Constructs the map data for Init. See its description above.
        """

        # To use for the 'mapData' parameter in constructor
        data = {
            "height": None,         # Real height (set by model)
            "width": None,          # Real width (set by model)
            "blockHeight": None,    # The height of the map in blocks
            "blockWidth": None,     # The width of the map in blocks
            "blocks": None,         # A two dimensionnal array for storing blocks
            "flags": None,          # The flags for each team to obtain
            "spawns": None,         # Remember the spawn locations for each team
        }

        # The format character for each tile and it's constructor call
        blocks = {
            '#': 'Wall({},{})',
            '-': 'WallTransparent({},{})',
            ' ': 'Empty({},{})',
            '1': 'Spawn(1,{},{})',
            '2': 'Spawn(2,{},{})'
        }

        data["spawns"] = { 1: [], 2: [] } # Spawn blocks for each team

        with open(filename, "r") as file:
            lines = file.readlines()

            mapDefinitionLines = 2 # The amount of lines before the map tiling

            data["blockWidth"] = int(lines[0].split(":")[1])
            data["blockHeight"] = int(lines[1].split(":")[1])

            data["height"] = data["blockHeight"] * Map.BLOCKSIZE
            data["width"] = data["blockWidth"] * Map.BLOCKSIZE

            # The file lines that contains the map tiling
            # Used to fill 'data["blocks"]' according to 'blocks'
            mapLines = lines[mapDefinitionLines : data["blockHeight"] + mapDefinitionLines]

            data["blocks"] = [[None for i in range(data["blockHeight"])] for i in range(data["blockWidth"])]

            for y in range(data["blockHeight"]):
                for x in range(data["blockWidth"]):
                    if mapLines[y][x] not in blocks.keys():
                        continue

                    # See definition of 'blocks' for explanation
                    data["blocks"][x][y] = eval(blocks[mapLines[y][x]].format(x * Map.BLOCKSIZE,y * Map.BLOCKSIZE))

                    if(type(data["blocks"][x][y]).__name__ == "Spawn"):
                        # If this is a spawn block, add it to it's team's spawn blocks
                        data["spawns"][data["blocks"][x][y].team].append(data["blocks"][x][y]) 

            data["flags"] = list()

            # Read the remaining info in the file
            # starts after the map tiling
            for line in lines[data["blockHeight"] + mapDefinitionLines :]:
                # Get the attribute and it's value without '\n' (:-1)
                attributes = line[:-1].split(':')

                # flag: team, blockX, blockY
                if attributes[0] == "flag":
                    info = attributes[1].split(',')

                    # Create the new flag while converting the block X and Y to real coordinates
                    data["flags"].append(Flag(int(info[0]), int(info[1]) * Map.BLOCKSIZE, int(info[2]) * Map.BLOCKSIZE))

                    continue

        return data

    def GetRandomPositionInSpawn(self, team, margin = 0):
        """
        Parameters:
            team (int): The team number.

        Returns:
            point (x,y): A point located in the spawn of a said team.
        """
        return Map.GetRandomPositionInBlock(choice(self._spawns[team]), margin)

    def GetAllNonTransparentVertices(self, start_x = 0, start_y = 0, end_x = None, end_y = None):
        """
        """
        if end_x == None:
            end_x = self.blockWidth
        if end_y == None:
            end_y = self.blockHeight

        polygons = list()

        for line in self.blocks[start_x:end_x]:
            for block in line[start_y:end_y]:
                if not block.transparent:
                    vertices = list()
                    vertices.append((block.x,block.y,1))
                    vertices.append((block.x + Map.BLOCKSIZE,block.y,2))
                    vertices.append((block.x + Map.BLOCKSIZE,block.y + Map.BLOCKSIZE,0))
                    vertices.append((block.x,block.y + Map.BLOCKSIZE,0))
                    polygons.append(vertices)

        return polygons

    def GetAllNonTransparentCorners(self, start_x = 0, start_y = 0, end_x = None, end_y = None):
        """
        """
        if end_x == None:
            end_x = self.blockWidth
        if end_y == None:
            end_y = self.blockHeight

        corners = dict()

        for vertices in self.GetAllNonTransparentVertices(start_x, start_y, end_x, end_y):
            
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