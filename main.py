from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from time import sleep, time
from math import sin, cos, pi
from random import randint

TITLE = "Reverse Fourier Visualisation"
WIDTH, HEIGHT = 1200, 600

class App:
    def __init__(self, title):
        self.title = title
        return

    def create_window(self,width, height, fullscreen=False):
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(width,height)
        glutCreateWindow(self.title.encode())
        self.width, self.height = width, height
        glEnable(GL_COLOR_MATERIAL)
        glShadeModel(GL_SMOOTH)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        glEnable (GL_BLEND)
        glBlendFunc (GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
        return

class Circle:
    def __init__(self,radius,speed,xy=(100,100),child=None):
        self.x,self.y = xy
        self.radius   = radius
        self.child    = child
        self.rotation = 0.
        self.pointerX = self.radius
        self.pointerY = 0.
        self.speed = 2*pi/(360./speed)
        return

    def display(self):
        # display self
        glBegin(GL_LINE_LOOP)
        for i in range(18):
            angle = i * 2*pi/18.
            x = self.radius * cos(angle)
            y = self.radius * sin(angle)
            glVertex2f(self.x+x,self.y+y)
        glEnd()
        glBegin(GL_LINE_LOOP)
        for i in range(6):
            angle = i * 2*pi/6.
            x = 2 * cos(angle)
            y = 2 * sin(angle)
            glVertex2f(self.x+self.pointerX+x,self.y+self.pointerY+y)
        glEnd()
        if self.child:
            self.child.display()
        return

    def setPos(self,x,y):
        self.x,self.y = x,y
        return
    
    def update(self):
        # increment angle
        self.rotation += self.speed
        self.pointerX = self.radius * cos(self.rotation)
        self.pointerY = self.radius * sin(self.rotation)
        if self.child:
            self.child.x = self.x+self.pointerX
            self.child.y = self.y+self.pointerY
            self.child.update()
        return

    @property
    def pointer(self):
        if self.child:
            return self.child.pointer
        else:
            return (self.x+self.pointerX,self.y+self.pointerY)
    
    def addChild(self,child):
        if self.child:
            self.child.addChild(child)
        else:
            self.child = child
        return

c = Circle(80,0.4)
c.addChild(Circle(40,0.3))
c.addChild(Circle(20,0.2))
c.setPos(WIDTH/4,HEIGHT/2)
line = []
waveStart = WIDTH/4+100
waveLength = 800

def main():
    def draw():
        global line
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glOrtho(0,WIDTH,HEIGHT,0,-1,1)

        glPushMatrix()
        # draw wheels
        c.update()
        c.display()

        # draw linking line
        newX, newY = c.pointer
        glBegin(GL_LINES)
        glVertex2f(newX,newY)
        glVertex2f(waveStart,newY)
        glEnd()
        
        # draw wave
        line.insert(0,newY)
        if len(line) > waveLength: line.pop()
        glPushMatrix()
        glTranslate(waveStart,0,0)
        glBegin(GL_LINES)
        for x,y in enumerate(line):
            glVertex2f(x,y)
        glEnd()
        glPopMatrix()
        
        glPopMatrix()
        glutSwapBuffers()
        return

    def keyboard_down(key, x, y):
        ''' Keyboard repeat is enabled by default '''
        ''' x and y represent the mouse position  '''
        if key == b'\x1b': # ESC key
            glutLeaveMainLoop()
        return
    
    app = App(TITLE)
    app.create_window(WIDTH,HEIGHT)
    glutDisplayFunc( draw )              
    glutIdleFunc( draw )
    glutKeyboardFunc( keyboard_down )   
    glClearColor(0,0,0,0);
    glutMainLoop()
    return

if __name__ == "__main__":
    main()
