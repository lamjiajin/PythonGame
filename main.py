  
import math
import pyxel 
import array
import random

SCREEN_WIDTH = 255 
SCREEN_HEIGHT = 120
EMPTY = 0
SAND = 1
WATER = 2
BIRD = 3

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
    return self.map[y*self.height + x]
    
  def set(self, x, y, num):
    if(x < 0 or x >= self.width or y < 0 or y >= self.height):
      return Map.INVALID
    self.map[y*self.height + x] = num
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


    
class Water:
  def __init__(self, px, py):
    self.position = Vec2(px, py)
    mapv2.set(self.position.x,self.position.y, WATER)
    
  def draw(self):
    pyxel.pix(self.position.x,self.position.y,5 )
    
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
      
  def try_go_bottom(self):
    res = mapv2.get(self.position.x, self.position.y + 1)
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
 
  ### this is the state machine for water sim ###
  # initial node [ check if can go down ] if cannot, try other nodes
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
    self.tried_botleft = True
    if self.tried_botright == True:
      return 4
    else:
      return 3
  # bot right
  def node_3(self):
    res = self.try_go_bottom_right()
    self.tried_botright = True
    if self.tried_botleft == True:
      return 4
    else:
      return 2
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
    self.tried_left = True
    if self.tried_right == True:
      return 7
    else:
      return 6
  # right
  def node_6(self):
    res = self.try_go_right()
    self.tried_right = True
    if self.tried_left == True:
      return 7
    else:
      return 5
  # setting positions in the map
  def node_7(self):
    mapv2.set(self.original_x,self.original_y, EMPTY)
    mapv2.set(self.position.x,self.position.y, WATER)
    self.updating = False
    return 0
    
  FUNC_MAP = { 0: node_0, 1: node_1, 2: node_2, 3: node_3, 4: node_4, 5: node_5, 6: node_6, 7: node_7 }
 
  def update(self):
    self.updating = True
    self.tried_botleft = False
    self.tried_botright = False
    self.tried_left = False
    self.tried_right = False
    self.original_x = self.position.x
    self.original_y = self.position.y
    res = 0
    while self.updating:
      res = self.FUNC_MAP[res](self)

class App: 
    def __init__(self): 
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT)
        # shows the mouse
        pyxel.mouse(True)
        self.sandarray = []
        self.waterarray = []
        pyxel.run(self.update, self.draw)
    
    def update(self): 
        if pyxel.btnp(pyxel.KEY_Q): 
            pyxel.quit()
                
        if pyxel.btnp(pyxel.MOUSE_RIGHT_BUTTON, 1, 1):
            for i in range(-1,1):
              for j in range(-1,1):
                if(mapv2.get(pyxel.mouse_x + i,pyxel.mouse_y + j) == EMPTY):
                  self.waterarray.append(Water(pyxel.mouse_x+ i, pyxel.mouse_y + j))
                

        for y in self.waterarray:
            y.update()

    def draw(self):
        pyxel.cls(0)
        for y in self.waterarray:
            y.draw()
    
App()
