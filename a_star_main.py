  
import math
import pyxel 
import array
import random
import queue
import copy
from heapq import heappush, heappop

# doesn't work well with high numbers
SCREEN_WIDTH = 5
SCREEN_HEIGHT = 5
EMPTY = 0
DEFAULT = 8
INVALID = -1
VALID = 0
PLAYER=10
DESTINATION=11
SCALE = 30
STEP_COST = 1



class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.magnitude = math.sqrt(x * x + y * y)
        
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __add__(self, other):
        return Vec2(self.x + other.x, self.y + other.y)

class node:
    def __init__(self):
        self.total_cost = 9000
        self.curr_cost = 0
        self.pos = Vec2(-1,-1)
        self.prev_index = -1
        self.visited = False
        
class Map:
  TOPLEFT = Vec2(-1,-1)
  TOPRIGHT = Vec2(1,-1)
  TOP = Vec2(0,-1)
  LEFT = Vec2(-1,0)
  RIGHT = Vec2(1,0)
  BOTLEFT = Vec2(-1,1)
  BOTRIGHT = Vec2(1,1)
  BOT = Vec2(0,1)
  def __init__(self, width, height):
    self.map = [0 for x in range(height * width)]
    self.width = width
    self.height = height
    self.area = width*height
    
  def getmodifiedindex_fromIndex(self, pos, mod):
    x = pos.x + mod.x
    y = pos.y + mod.y
    if(x < 0 or x >= self.width or y < 0 or y >= self.height):
      return INVALID
    return y*self.width + x
    
  def getmodifiedindex(self,index,mod):
    num = index + mod.x + mod.y * self.width
    if num >= self.area:
        return INVALID
    if num < 0:
        return INVALID
    return num
  
  def setFromIndex(self,index, num):
    self.map[index] = num
    
  def get_index_from_Vec2(self,pos):
    x = pos.x
    y = pos.y
    if(x < 0 or x >= self.width or y < 0 or y >= self.height):
      return INVALID
    return y*self.width + x
    
  def get_from_Vec2(self, pos):
    return self.get(pos.x,pos.y)
    
  def set_from_Vec2(self, pos, num):
    return self.set(pos.x,pos.y, num)
    
  def get(self, x, y):
    if(x < 0 or x >= self.width or y < 0 or y >= self.height):
      return INVALID
    return self.map[y*self.width + x]
    
  def set(self, x, y, num):
    if(x < 0 or x >= self.width or y < 0 or y >= self.height):
      return INVALID
    self.map[y*self.width + x] = num
    return VALID
    
  def draw(self):
    for y in range(0,self.height):
        for x in range(0,self.width):
            pyxel.pix(x,y,self.map[y*self.width + x])
  
  def showmap(self):
    res = ""
    for y in range(0,self.height):
      for x in range(0,self.width):
        res += str(self.map[y*self.width + x]) + " "
      res += "\n"
    print(res)
    
  def resetmap(self):
    self.map = [0 for x in range(self.area)]
  
mapv2 = Map(SCREEN_WIDTH,SCREEN_HEIGHT)
mapv2.map = [
  0,9,0,0,0,
  0,9,0,9,0,
  0,0,0,9,0,
  0,9,5,0,0,
  0,9,0,0,0
]

restart_find_path = True
directionArr = [Map.TOP,Map.BOT,Map.LEFT,Map.RIGHT]
map = copy.deepcopy(mapv2)
nodearray = []
foundendnode = False
STEP_BY_STEP = True
qq = []
def find_path(start,end):
    global restart_find_path
    global directionArr
    global map
    global nodearray
    global foundendnode
    global STEP_BY_STEP
    global qq
    if restart_find_path == True:
        restart_find_path = False
        # make a copy of the map for us to edit to show the final path
        map = copy.deepcopy(mapv2)
        # check if search is valid
        if map.get_from_Vec2(start) == INVALID:
            print("Invalid start position")
            return -1
        if map.get_from_Vec2(end) == INVALID:
            print("Invalid end position")
            return -1
        
        # creates a bunch of nodes based on map.size
        nodearray = [node() for x in range(map.area)]
    
        # set the node costs
        for i in range(map.area):
            nodearray[i].curr_cost = map.map[i]
        # creates the queue 
        qq = []
        foundendnode = False
        
    # sets up the start node and end node
    end_index = map.get_index_from_Vec2(end)
    start_index = map.get_index_from_Vec2(start)
    start_node = nodearray[start_index] 
    start_node.pos = start
    if(len(qq) == 0):
        heappush(qq,(0,start_index))
        
    while len(qq) > 0:
        curr_node_data = heappop(qq)
        curr_node_index = curr_node_data[1]
        curr_node = nodearray[curr_node_index]
        curr_node.total_cost = curr_node_data[0]
        # marking node to be visited
        curr_node.visited = True
        
        # have we found the endnode? If we have, we can exit immediately because of the priority queue. 
        # whatever path that led to this node must be the cheapest
        if(curr_node_index == end_index):
            restart_find_path = True
            foundendnode = True
            break
        
        for direction in directionArr:
            # this is to get the index of the node that I am checking
            dir_index = map.getmodifiedindex_fromIndex(curr_node.pos,direction)
            # if the node is not out of bounds
            if(dir_index != INVALID):
                # this is the node from the array of nodes with information stored inside
                possible_dir_node = nodearray[dir_index]
                if(possible_dir_node.visited == False):
                    # first set the position of the current node into here, makes for easier directi
                    possible_dir_node.pos = curr_node.pos + direction
                    # check if the new proposed cost is cheaper than what's already there
                    # STEP_COST is needed otherwise becuase we want the search area to focus from the inital starting position
                    # if there is no STEP_COST, the search algo can just keep going off in one direction
                    new_total_cost = curr_node.total_cost + possible_dir_node.curr_cost + STEP_COST
                    if(new_total_cost < possible_dir_node.total_cost):
                        possible_dir_node.prev_index = curr_node_index
                        heappush(qq,(new_total_cost,dir_index))
        if STEP_BY_STEP == True:
            break
            
    #currIndex = end_index
    #map.showmap()
    #while(currIndex != -1):
    #    map.setFromIndex(currIndex,1)
    #    currIndex = nodearray[currIndex].prev_index
    #    map.showmap()
      
class Pixel:
  def __init__(self, px, py, type):
    self.position = Vec2(px, py)
    self.type = type
    self.moved = False
    mapv2.set(self.position.x,self.position.y, type)
    
  def draw(self):
    pyxel.pix(self.position.x,self.position.y, self.type)
    
  def peek(self, num):
    res = mapv2.get(self.position.x + num.x, self.position.y + num.y)
    return res
  
  def try_teleport(self, pos):
    res = mapv2.get(pos.x , pos.y )
    if res == EMPTY:
        mapv2.set(self.position.x, self.position.y, EMPTY)
        self.position.x = pos.x
        self.position.y = pos.y
        mapv2.set(self.position.x, self.position.y, self.type)
        self.moved = True
    return res
  
  def try_go(self,num):
    res = mapv2.get(self.position.x + num.x, self.position.y + num.y)
    if res == EMPTY:
        mapv2.set(self.position.x, self.position.y, EMPTY)
        self.position.x += num.x
        self.position.y += num.y
        mapv2.set(self.position.x, self.position.y, self.type)
        self.moved = True
    return res
    
    
  ### this is the state machine  ###
  def node_0(self):
    self.updating = False
    pass
 
  def endNode(self):
    self.updating = False
    
  FUNC_MAP = { 0: node_0 }
  START_NODE = { 
  DEFAULT: 0,
  DESTINATION: 0,
  PLAYER: 0
  }

  
  def DEFAULT_SPECIFIC_UPDATE(self):
    pass
        
  def DEFAULT_POST_UPDATE(self):
    pass
    
  SPECIFIC_UPDATE = { 
    DEFAULT: DEFAULT_SPECIFIC_UPDATE,
    DESTINATION: DEFAULT_SPECIFIC_UPDATE,
    PLAYER: DEFAULT_SPECIFIC_UPDATE
    }
    
  POST_SPECIFIC_UPDATE = { 
    DEFAULT:         DEFAULT_POST_UPDATE,
    DESTINATION: DEFAULT_POST_UPDATE,
    PLAYER: DEFAULT_POST_UPDATE
    }
  
  def update(self):
    self.updating = True
    self.moved = False
    Pixel.SPECIFIC_UPDATE[self.type](self)
    res = Pixel.START_NODE[self.type]
    while self.updating:
      res = Pixel.FUNC_MAP[res](self)
    Pixel.POST_SPECIFIC_UPDATE[self.type](self)
    
pixelarray = []




class App: 
    def __init__(self): 
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT, scale=SCALE)
        # shows the mouse
        pyxel.mouse(True)
        self.Paused = True
        #self.player = Pixel(int(SCREEN_WIDTH/2),int(SCREEN_HEIGHT/2),PLAYER)
        #self.destination = Pixel(int(SCREEN_WIDTH/2),int(SCREEN_HEIGHT/2),DESTINATION)
        pyxel.run(self.update, self.draw)
    
    def update(self): 
        if pyxel.btnp(pyxel.KEY_Q): 
            pyxel.quit()
        #if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
        #    self.destination.position = Vec2(pyxel.mouse_x, pyxel.mouse_y)
        
        if pyxel.btnp(pyxel.KEY_P):
            self.Paused = not self.Paused
            
        if pyxel.btnp(pyxel.KEY_C):
            start = Vec2(0,0)
            end = Vec2(3,4)
            find_path(start,end)
            
        
        if self.Paused == False:
            pass
            #mapv3.showmap()
            #self.destination.update()
            #self.player.update()
        
    def draw(self):
        pyxel.cls(0)
            
        for node in nodearray:
            if node.visited == True:
                pyxel.pix(node.pos.x,node.pos.y, 1)               
        #self.destination.draw()
        #self.player.draw()
    
App()
