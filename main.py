import math
import pyxel 
import array

BALL_SIZE = 2
BALL_SPEED = 2
SCREEN_WIDTH = 255 
SCREEN_HEIGHT = 120
map = [[0 for j in range(SCREEN_HEIGHT)] for i in range(SCREEN_WIDTH)]


class Vec2:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Vec2_normalized: 
    def __init__(self, x, y): 
        self.magnitude = math.sqrt(x * x + y * y) 
        self.x = x / self.magnitude * BALL_SPEED 
        self.y = y / self.magnitude * BALL_SPEED

class Ball:
    def __init__(self, px, py, vx, vy):
        self.position = Vec2(px, py)
        self.velocity = Vec2_normalized(vx, vy)
    
    def update(self):
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
    
        if self.position.y >= SCREEN_HEIGHT - BALL_SIZE:
            self.velocity.y = -self.velocity.y
    
        if self.position.y <= BALL_SIZE:
            self.velocity.y = -self.velocity.y
    
        if self.position.x >= SCREEN_WIDTH - BALL_SIZE:
            self.velocity.x = -self.velocity.x
    
        if self.position.x <= BALL_SIZE:
            self.velocity.x = -self.velocity.x
        
    def draw(self):
        pyxel.circ(self.position.x,self.position.y,BALL_SIZE,7)

class Pixel:
    def __init__(self, px, py):
        self.position = Vec2(px, py)
        map[self.position.x][self.position.y] = 1
    def draw(self):
        pyxel.pix(self.position.x,self.position.y,9 )
        
    def update(self):
    
        # if you aren't on ground
        if self.position.y + 1 < SCREEN_HEIGHT:
            ori_y = self.position.y
            ori_x = self.position.x
            
            #check if bottom is available
            if map[ori_x][ori_y + 1] == 0:
                self.position.y += 1
            #check if bottom left is available
            elif map[ori_x - 1][ori_y + 1] == 0:
                self.position.x -= 1
                self.position.y += 1
            #check if bottom right is available
            elif map[ori_x + 1][ori_y + 1] == 0:
                self.position.x += 1
                self.position.y += 1
                
            map[ori_x][ori_y] = 0
            map[self.position.x][self.position.y] = 1

        
class App: 
    def __init__(self): 
        pyxel.init(SCREEN_WIDTH, SCREEN_HEIGHT)
        # shows the mouse
        pyxel.mouse(True)
        self.ballarray = []
        pyxel.run(self.update, self.draw)
    
    def update(self): 
        if pyxel.btnp(pyxel.KEY_Q): 
            pyxel.quit()
        if pyxel.btnp(pyxel.MOUSE_LEFT_BUTTON, 1, 1):
            if(map[pyxel.mouse_x][pyxel.mouse_y] == 0):
                self.ballarray.append(Pixel(pyxel.mouse_x, pyxel.mouse_y))
        for x in self.ballarray:
            x.update()
        
    def draw(self):
        pyxel.cls(0)
        for x in self.ballarray:
            x.draw()
        
    
App()