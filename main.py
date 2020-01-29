  
import math
import pyxel 
import array
import random

SCREEN_WIDTH = 120
SCREEN_HEIGHT = 120
EMPTY = 0
VAPOR = 8
WATER = 5
SLIMECORE = 6
SLIME = 7
INVALID = -1
VALID = 0
SLIMETIMEMAX = 50
SLIMEMOVEMAX = 40
SLIMESIZE = 300

class Vec2:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.magnitude = math.sqrt(x * x + y * y) 
  def normalized(self):
    self.x = self.x / self.magnitude 
    self.y = self.y / self.magnitude
    self.magnitude = 1
    

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
    
  def get(self, x, y):
    if(x < 0 or x >= self.width or y < 0 or y >= self.height):
      return INVALID
    return self.map[y*self.width + x]
    
  def set(self, x, y, num):
    if(x < 0 or x >= self.width or y < 0 or y >= self.height):
      return INVALID
    self.map[y*self.width + x] = num
    return VALID
  
mapv2 = Map(SCREEN_WIDTH,SCREEN_HEIGHT)

class Vec2_normalized: 
  def __init__(self, x, y): 
    self.magnitude = math.sqrt(x * x + y * y) 
    self.x = x / self.magnitude 
    self.y = y / self.magnitude

    
class Pixel:
  def __init__(self, px, py, type):
    self.position = Vec2(px, py)
    self.type = type
    self.moved = False
    mapv2.set(self.position.x,self.position.y, type)
    if(type == SLIME):
        self.corepos = Vec2(0,0)
        self.offset = Vec2(0,0)
        self.state = 0
        self.timeleft = 0
        self.movesleft = 0
    if(type == SLIMECORE):
        self.slimebod = [Pixel(px,py,SLIME) for x in range(SLIMESIZE)]
    
  def draw(self):
    pyxel.pix(self.position.x,self.position.y, self.type)
    if(self.type == SLIMECORE):
        for x in self.slimebod:
            x.draw()
    
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
    
    
  ### this is the state machine for water sim ###
  
  # try go down then bot left or bot right
  def node_0(self):
    res = self.try_go(Map.BOT)
    if res == INVALID:
      return 4
    elif res == EMPTY:
      return 7
    else:
      return 1
  # rand for bot left / bot right
  def node_1(self):
    num = random.randint(0, 1)
    if num == 1:
      return 2
    else:
      return 3
  #bot left
  def node_2(self):
    res = self.try_go(Map.BOTLEFT)
    return 4
  # bot right
  def node_3(self):
    res = self.try_go(Map.BOTRIGHT)
    return 4
  # rand for left / right
  def node_4(self):
    num = random.randint(0, 2)
    if num == 1:
      return 5
    elif num == 2:
      return 6
    else:
      return 7
  # left
  def node_5(self):
    res = self.try_go(Map.LEFT)
    return 7
  # right
  def node_6(self):
    res = self.try_go(Map.RIGHT)
    return 7
  # setting positions in the map
  def node_7(self):
    self.updating = False
    return 0
  # go up
  def node_8(self):
    res = self.try_go(Map.TOP)
    if res == INVALID:
      return 4
    elif res == EMPTY:
      return 7
    else:
      return 9
  # rand for top left / top right
  def node_9(self):
    num = random.randint(0, 1)
    if num == 1:
      return 10
    else:
      return 11
  # top left
  def node_10(self):
    res = self.try_go(Map.TOPLEFT)
    return 4
  # top right
  def node_11(self):
    res = self.try_go(Map.TOPRIGHT)
    return 4
  
  def node_12(self):
    if self.peek(Map.TOP) != EMPTY:
        res = self.try_go(Map.BOT)
        if res == EMPTY:
            return 7
        else:
            return 4
    return 7
    
  # try go down then  left or right
  def node_13(self):
    res = self.try_go(Map.BOT)
    if res == EMPTY:
      return 7
    else:
      return 4
    
    
  FUNC_MAP = { 0: node_0, 1: node_1, 2: node_2, 3: node_3, 4: node_4, 5: node_5, 6: node_6, 7: node_7, 8: node_8, 9: node_9, 10: node_10, 11: node_11, 12: node_12, 13: node_13 }
  START_NODE = { WATER: 13, VAPOR: 8 , SLIMECORE: 7, SLIME: 13}
  
  def VAPOR_SPECIFIC_UPDATE(self):
    num = random.randint(0,200)
    if num == 5:
      if mapv2.get(self.position.x , self.position.y + 1) == EMPTY:
        num = mapv2.get(self.position.x - 1, self.position.y - 1) + \
                mapv2.get(self.position.x + 1, self.position.y - 1) + \
                mapv2.get(self.position.x, self.position.y - 1)
        if (num == 24):
            self.type = WATER
        
  def WATER_SPECIFIC_UPDATE(self):
    num = random.randint(0,200)
    if num == 5:
      if mapv2.get(self.position.x , self.position.y - 1) == EMPTY:
        num = mapv2.get(self.position.x - 1, self.position.y + 1) + \
                mapv2.get(self.position.x + 1, self.position.y + 1) + \
                mapv2.get(self.position.x, self.position.y + 1)
        if (num == 15):
            self.type = VAPOR
  
  def SLIMECORE_SPECIFIC_UPDATE(self):
  
    for x in self.slimebod:
        mapv2.set(x.position.x, x.position.y, EMPTY)
        
    if pyxel.btnp(pyxel.KEY_A,1,1): 
        self.try_go(Map.LEFT)
    if pyxel.btnp(pyxel.KEY_D,1,1): 
        self.try_go(Map.RIGHT)
    if pyxel.btnp(pyxel.KEY_W,1,1): 
        self.try_go(Map.TOP)
    if pyxel.btnp(pyxel.KEY_S,1,1): 
        self.try_go(Map.BOT)
        
    for x in self.slimebod:
        mapv2.set(x.position.x, x.position.y, SLIME)
     
    mapv2.set(self.position.x, self.position.y, SLIMECORE)
    
    for x in self.slimebod:
        x.corepos.x = self.position.x
        x.corepos.y = self.position.y
        x.update()
         
  def SLIME_SPECIFIC_UPDATE(self):
    self.updating = True
    
    if self.timeleft <= 0 or self.movesleft <= 0:
        pos = Vec2(0,0)
        pos.x = self.corepos.x + random.randint(-2,2)
        pos.y = self.corepos.y + random.randint(-3,5)
        if self.try_teleport(pos) == EMPTY:
            self.timeleft = SLIMETIMEMAX
            self.movesleft = SLIMEMOVEMAX
        
  def WATER_POST_UPDATE(self):
    pass
    
  def VAPOR_POST_UPDATE(self):
    pass
  
  def SLIMECORE_POST_UPDATE(self):
    pass
    
  def SLIME_POST_UPDATE(self):
    if self.moved:
        self.movesleft -= 1
    self.timeleft -=1
    
  SPECIFIC_UPDATE = { 
    WATER: WATER_SPECIFIC_UPDATE, 
    VAPOR: VAPOR_SPECIFIC_UPDATE, 
    SLIMECORE: SLIMECORE_SPECIFIC_UPDATE, 
    SLIME: SLIME_SPECIFIC_UPDATE
    }
    
  POST_SPECIFIC_UPDATE = { 
    WATER:         WATER_POST_UPDATE, 
    VAPOR:         VAPOR_POST_UPDATE, 
    SLIMECORE: SLIMECORE_POST_UPDATE, 
    SLIME:         SLIME_POST_UPDATE
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
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT)
        # shows the mouse
        pyxel.mouse(True)
        self.sandarray = []
        self.Paused = True
        pyxel.run(self.update, self.draw)
    
    def update(self): 
        if pyxel.btnp(pyxel.KEY_Q): 
            pyxel.quit()
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON):
            pixelarray.append(Pixel(pyxel.mouse_x, pyxel.mouse_y, SLIMECORE))
        #if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON, 1, 1):
        #    for i in range(-5,5):
        #      for j in range(-5,5):
        #        if(mapv2.get(pyxel.mouse_x + i,pyxel.mouse_y + j) == EMPTY):
        #            pixelarray.append(Pixel(pyxel.mouse_x + i, pyxel.mouse_y + j, WATER) )
        if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON, 1, 1):
            for i in range(-5,5):
              for j in range(-5,5):
                if(mapv2.get(pyxel.mouse_x + i,pyxel.mouse_y + j) == EMPTY):
                    pixelarray.append(Pixel(pyxel.mouse_x + i, pyxel.mouse_y + j, WATER) )
        
        if pyxel.btnp(pyxel.KEY_P):
            self.Paused = not self.Paused
        
        if self.Paused == False or pyxel.btnp(pyxel.KEY_C):
            for y in pixelarray:
                y.update()

    def draw(self):
        pyxel.cls(0)
        for y in pixelarray:
            y.draw()
    
App()
