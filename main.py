  
import math
import pyxel 
import array
import random

SCREEN_WIDTH = 40
SCREEN_HEIGHT = 120
EMPTY = 0
VAPOR = 8
WATER = 5
SLIMECORE = 6
SLIME = 7
class Map:
  INVALID = -1
  VALID = 0
  def __init__(self, width, height):
    self.map = [0 for x in range(height * width)]
    self.width = width
    self.height = height
    
  def get(self, x, y):
    if(x < 0 or x >= self.width or y < 0 or y >= self.height):
      return Map.INVALID
    return self.map[y*self.width + x]
    
  def set(self, x, y, num):
    if(x < 0 or x >= self.width or y < 0 or y >= self.height):
      return Map.INVALID
    self.map[y*self.width + x] = num
    #print("sets (" + str(x) + ", " + str(y) + ") to " + str(num)) 
    return Map.VALID
  
mapv2 = Map(SCREEN_WIDTH,SCREEN_HEIGHT)

class Vec2:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.magnitude = math.sqrt(x * x + y * y) 
  def normalized(self):
    self.x = self.x / self.magnitude 
    self.y = self.y / self.magnitude
    self.magnitude = 1
    
class Vec2_normalized: 
  def __init__(self, x, y): 
    self.magnitude = math.sqrt(x * x + y * y) 
    self.x = x / self.magnitude 
    self.y = y / self.magnitude

class Node:
    def __init__(self, cost, position):
        self.position = position
        self.cost = cost
        
def byCost(elem):
    return elem.cost
    
class Pixel:
  def __init__(self, px, py, type):
    self.position = Vec2(px, py)
    self.type = type
    mapv2.set(self.position.x,self.position.y, type)
    if(type == SLIME):
        self.offset = Vec2(0,0)
    if(type == SLIMECORE):
        self.slimebod = [Pixel(px,py,SLIME) for x in range(25)]
    
  def draw(self):
    pyxel.pix(self.position.x,self.position.y, self.type)
    if(self.type == SLIMECORE):
        for x in self.slimebod:
            x.draw()
    
  def try_go_bottom_left(self):
    res = mapv2.get(self.position.x - 1, self.position.y + 1)
    if res == EMPTY:
      self.position.x -= 1
      self.position.y += 1
    return res
    
  def try_go_bottom_right(self):
    res = mapv2.get(self.position.x + 1, self.position.y + 1)
    if res == EMPTY:
      self.position.x += 1
      self.position.y += 1
    return res
    
  def try_go_top_left(self):
    res = mapv2.get(self.position.x - 1, self.position.y - 1)
    if res == EMPTY:
      self.position.x -= 1
      self.position.y -= 1
    return res
    
  def try_go_top_right(self):
    res = mapv2.get(self.position.x + 1, self.position.y - 1)
    if res == EMPTY:
      self.position.x += 1
      self.position.y -= 1
    return res
      
  def try_go_bottom(self):
    res = mapv2.get(self.position.x, self.position.y + 1)
    #print("old x: " + str(self.position.x) + " old y: " + str(self.position.y) + " res: " + str(res))
    if res == EMPTY:
      self.position.y += 1
    return res
    
  def try_go_left(self):
    res = mapv2.get(self.position.x - 1, self.position.y)
    if res == EMPTY:
      self.position.x -= 1
    return res
    
  def try_go_right(self):
    res = mapv2.get(self.position.x + 1, self.position.y)
    if res == EMPTY:
      self.position.x += 1
    return res
 
  def try_go_top(self):
    res = mapv2.get(self.position.x, self.position.y - 1)
    #print("old x: " + str(self.position.x) + " old y: " + str(self.position.y) + " res: " + str(res))
    if res == EMPTY:
      self.position.y -= 1
    return res
    
  ### this is the state machine for water sim ###
  # try go down
  def node_0(self):
    res = self.try_go_bottom()
    if res == Map.INVALID:
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
    res = self.try_go_bottom_left()
    return 4
  # bot right
  def node_3(self):
    res = self.try_go_bottom_right()
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
    res = self.try_go_left()
    return 7
  # right
  def node_6(self):
    res = self.try_go_right()
    return 7
  # setting positions in the map
  def node_7(self):
    mapv2.set(self.original_x,self.original_y, EMPTY)
    mapv2.set(self.position.x,self.position.y, self.type)
    self.updating = False
    return 0
  # go up
  def node_8(self):
    res = self.try_go_top()
    if res == Map.INVALID:
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
    res = self.try_go_top_left()
    return 4
  # top right
  def node_11(self):
    res = self.try_go_top_right()
    return 4
  
  FUNC_MAP = { 0: node_0, 1: node_1, 2: node_2, 3: node_3, 4: node_4, 5: node_5, 6: node_6, 7: node_7, 8: node_8, 9: node_9, 10: node_10, 11: node_11 }
  START_NODE = { WATER: 0, VAPOR: 8 , SLIMECORE: 7, SLIME: 7}
  
  def VAPOR_SPECIFIC_UPDATE(self):
    num = random.randint(0,200)
    if num == 5:
      if mapv2.get(self.position.x , self.position.y + 1) == EMPTY:
        num = mapv2.get(self.position.x - 1, self.position.y - 1) + \
                mapv2.get(self.position.x + 1, self.position.y - 1) + \
                mapv2.get(self.position.x, self.position.y - 1)
        if (num == 24):
            self.type = WATER
    #if(mapv2.get(self.position.x, self.position.y - 1) == Map.INVALID):
    #    self.type = WATER
        
  def WATER_SPECIFIC_UPDATE(self):
    num = random.randint(0,200)
    if num == 5:
      if mapv2.get(self.position.x , self.position.y - 1) == EMPTY:
        num = mapv2.get(self.position.x - 1, self.position.y + 1) + \
                mapv2.get(self.position.x + 1, self.position.y + 1) + \
                mapv2.get(self.position.x, self.position.y + 1)
        if (num == 15):
            self.type = VAPOR
    #if(mapv2.get(self.position.x, self.position.y + 1) == Map.INVALID):
    #    self.type = VAPOR
  
  def SLIMECORE_SPECIFIC_UPDATE(self):
    if pyxel.btnp(pyxel.KEY_A,1,1): 
        if(mapv2.get(self.position.x - 1,self.position.y) == EMPTY):
            mapv2.set(self.position.x, self.position.y, EMPTY)
            self.position.x -= 1
            mapv2.set(self.position.x, self.position.y, SLIMECORE)
    if pyxel.btnp(pyxel.KEY_D,1,1): 
        if(mapv2.get(self.position.x + 1,self.position.y) == EMPTY):
            mapv2.set(self.position.x, self.position.y, EMPTY)
            self.position.x += 1
            mapv2.set(self.position.x, self.position.y, SLIMECORE)
     
    for x in self.slimebod:
        x.position.x = self.position.x
        x.position.y = self.position.y
        x.offset.x += random.randint(-1,1)
        x.offset.y += random.randint(-1,1)
        x.update()
         
  def SLIME_SPECIFIC_UPDATE(self):
    if(abs(self.offset.x) + abs(self.offset.y) > 5):
        self.offset.x = random.randint(-1,1)
        self.offset.y = random.randint(-1,1)
        
    self.position.x += self.offset.x
    self.position.y += self.offset.y
  
  SPECIFIC_UPDATE = { 
    WATER: WATER_SPECIFIC_UPDATE, 
    VAPOR: VAPOR_SPECIFIC_UPDATE, 
    SLIMECORE: SLIMECORE_SPECIFIC_UPDATE, 
    SLIME: SLIME_SPECIFIC_UPDATE
    }
  
  def update(self):
    self.updating = True
    self.original_x = self.position.x
    self.original_y = self.position.y
    res = Pixel.START_NODE[self.type]
    
    while self.updating:
      res = Pixel.FUNC_MAP[res](self)

    Pixel.SPECIFIC_UPDATE[self.type](self)
    
pixelarray = []



class App: 
    def __init__(self): 
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT)
        # shows the mouse
        pyxel.mouse(True)
        self.sandarray = []
        self.Paused = False
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
        #if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON, 1, 1):
        #    for i in range(-5,5):
        #      for j in range(-5,5):
        #        if(mapv2.get(pyxel.mouse_x + i,pyxel.mouse_y + j) == EMPTY):
        #            pixelarray.append(Pixel(pyxel.mouse_x + i, pyxel.mouse_y + j, VAPOR) )
        
        if pyxel.btnp(pyxel.KEY_P):
            self.Paused = not self.Paused
        
        if self.Paused == False:
            for y in pixelarray:
                y.update()

    def draw(self):
        pyxel.cls(0)
        for y in pixelarray:
            y.draw()
    
App()
