from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *

from math import sin, cos, pi

TITLE = "Fourier Series Visualisation"
WIDTH, HEIGHT = 1200, 600
FPS = 28 # estimate

def use_color(r, g, b):  #this is a decorator
    def func_wrapper(drawfunc):
        def a(*args, **kwargs):
            glColor3f(r, g, b)
            drawfunc(*args, **kwargs)
            glColor3f(1., 1., 1.)
        return a
    return func_wrapper

def text(string, x, y, size, color=(1,1,1)):
    def linetext(text,x,y,size,color=(0,0,0)):
        @use_color(*color)
        def wrapper():
            glPushMatrix()
            glRotate(180,1,0,0)
            glTranslate(x,y,0)
            default = 120.
            glScale(size/default, size/default, size/default)
            for c in text:
                glutStrokeCharacter(GLUT_STROKE_MONO_ROMAN,ord(c))
            glPopMatrix()
            return
        return wrapper()
    y = -y
    lines = string.split("\n")
    for i, line in enumerate(lines):
        offset = size+ (size + 10) * i
        linetext(line, x, y-offset, size, color=color)
    return

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
        glShadeModel(GL_FLAT)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glDisable(GL_DEPTH_TEST)
        glMatrixMode(GL_MODELVIEW)
        return

class Circle:
    def __init__(self,radius,freq,xy=(100,100),child=None):
        self.x,self.y = xy
        self.radius   = radius
        self.child    = child
        self.rotation = 0.
        self.pointerX = self.radius
        self.pointerY = 0.
        self.speed = freq/FPS
        self.frequency = freq
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

    @property
    def maxAmplitude(self):
        if self.child:
            return self.child.maxAmplitude + self.radius
        return self.radius

    @property
    def numOfChildren(self):
        if self.child:
            return self.child.numOfChildren + 1
        return 1

    def updateFrequency(self,newFreq):
        ''' Updates frequency of only the top wheel '''
        self.frequency = newFreq
        self.speed = newFreq/FPS

    def decreaseChildren(self):
        if self.child.child == None:
            self.child = None
        else:
            self.child.decreaseChildren()
        return

class SquareWave(Circle):
    def __init__(self,acc,amp,freq):
        Circle.__init__(self,amp,freq)
        for i in range(1,acc):
            freq += 2 * self.frequency
            self.addChild(Circle(amp*self.frequency/freq,freq))
        return

    def updateFrequency(self,newFreq):
        Circle.updateFrequency(self,newFreq)
        c = self
        i = 1
        while c.child != None:
            c.child.updateFrequency(newFreq + newFreq*2*i)
            i += 1
            c = c.child
        return

    def increaseChildren(self):
        freq = self.frequency + self.frequency * self.numOfChildren * 2
        self.addChild(Circle(self.radius*self.frequency/freq,freq))
        self.rotation = 0
        c= self
        while c.child != None:
            c.child.rotation = 0
            c = c.child
        return
    
line = []
waveStart = WIDTH/4+100
waveLength = 800

# define wave
freq = 0.5
acc = 3
amp = 100
wave = SquareWave(acc,amp,freq)
wave.setPos(WIDTH/4,HEIGHT/2)
# example of basic use
#c = Circle(80,0.1)
#c.addChild(Circle(70,0.3))

def main():
    def draw():
        global line
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glOrtho(0,WIDTH,HEIGHT,0,-1,1)

        glPushMatrix()
        # draw wheels
        wave.update()
        wave.display()

        # draw linking line
        newX, newY = wave.pointer
        glBegin(GL_LINES)
        glVertex2f(newX,newY)
        glVertex2f(waveStart,newY)
        glEnd()
        
        # draw wave
        line.insert(0,newY)
        if len(line) > waveLength: line.pop()
        glPushMatrix()
        glTranslate(waveStart,0,0)
        glLineWidth(1)
        glBegin(GL_POINTS)
        for x,y in enumerate(line):
            glVertex2f(x,y)
        glEnd()
        glPopMatrix()

        # draw info
        text("Frequency: {}Hz   Max Amplitude: {}   Num of Waves: {}".format(
            round(wave.frequency,2), round(wave.maxAmplitude,2), wave.numOfChildren),0,0,16)
        text("Decrease Frequency: -   Increase Frequency: +/=\nDecrease number of waves: [   Increase number of waves: ]",
             0,20,16)
        
        glPopMatrix()
        glutSwapBuffers()
        return

    def keyboard_down(key, x, y):
        ''' Keyboard repeat is enabled by default '''
        ''' x and y represent the mouse position  '''
        global wave; global freq;
        if key == b'\x1b': # ESC key
            glutLeaveMainLoop()
        if key == b'-':
            wave.updateFrequency(wave.frequency-0.1)
        if key == b'=':
            wave.updateFrequency(wave.frequency+0.1)
        if key == b'[':
            wave.decreaseChildren()
        if key == b']':
            wave.increaseChildren()
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
