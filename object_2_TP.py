from numpy import *
import numpy as np
import pylab as p
import matplotlib.axes as a
import mpl_toolkits.mplot3d.axes3d as a3d
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


#open a obj file and read faces and vertices
vertices = []
faces = []
material = None
 
read_f = ("python.obj")
for i, line in enumerate(open(read_f, "r")):
    if line.startswith('#'): continue
    values = line.split()
    if not values: continue
    if values[0] == 'v':
        v = map(float, values[1:4])
        vertices.append(v)
    elif values[0] == 'f':
        face = []
        texcoords = []
        norms = []
        for v in values[1:]:
            w = v.split('/')
            face.append(int(w[0]))
        faces.append(face)  
        
print vertices             
'''
all_v = []
for v in faces:
    for w in v:
        all_v.append(w)
print all_v
v_set = (set(all_v))
print v_set
per = []   
for f in v_set:
    per.append(vertices[f-1])
print per
'''
xs,ys,zs=[],[],[] 
xs1,ys1,zs1=[],[],[] 

for x1,y1,z1  in (vertices):
    xs.append(x1)
    ys.append(y1) 
    zs.append(z1)   

    

quad = [] 
for f in (faces):
    quad.append([vertices[v - 1] for v in f])
print quad
   
def pointdistance(p1,p2):
    #print "p1,p2",p1,p2
    p1=p1[:3]
    p2=p2[:3]
    x,y,z = [list(a) for a in zip(p1, p2)]
    xd = x[1]-x[0]
    yd = y[1]-y[0]
    zd = z[1]-z[0]
    distance = math.sqrt((xd*xd) + (yd*yd) + (zd*zd))
    return distance

def save_obj(xs,ys,zs):
    write_f = open('C:/Users/Phil Williammee/Desktop/pyjunk/pyout.obj', 'w+')   
    for xx,yy,zz in zip(xs,ys,zs):
            line = "v "+str(xx)+" "+str(yy)+" "+str(zz)+"\n"
            write_f.write(line)
    write_f.close()   
               
x=[]
y=[]
z=[]   
b=[]
last_v= [0,0,0] 
    
def filter(i,v):
    b.append((i,v))
    
    x.append(vertices[i-1][0])
    y.append(vertices[i-1][1])
    z.append(80)
    
    x.append(v[0])
    y.append(v[1])
    z.append(80)
    
    x.append(v[0])
    y.append(v[1])
    z.append(60.55)
    
def search():
    found=[]
    bad =       [0, 360, 366, 372, 1142, 1160, 1179, 1683, 1689, 1695, 1696, 1701, 1707, 1719, 1731]
    some_good = [0, 99, 360, 366, 367, 372, 950, 1142, 1160, 1179, 1491, 1683, 1689, 1690, 1695, 1696, 1701, 1702, 1707, 1709, 1719, 1720, 1721, 1731]
    for g in some_good:
        if g not in bad:
            found.append(g)
    print "good?",found

def draw_vert():
    global last_v
    skip=[1, 361, 373, 1684, 1708, 1749]
    for i, v in enumerate(vertices):
        distance = pointdistance(v, last_v)
        if distance > 33.0 and i not in skip:
            filter(i,v)
        else:
            x.append(v[0])
            y.append(v[1])
            z.append(60.55)
            
        last_v = v
    a=[b1[0] for b1 in b]
    print "bad", a
    search()

def draw_faces(offset=[0,0,0], d0_pounce=True, pounce =[0.0, 0.0, 10.0]):
    for i, v in enumerate(vertices):
        for xx,yy,zz in v:
            x.append(xx)
            y.append(yy)
            zz=60.5
            z.append(zz+offset[2])
        #move tool up
        x.append(xx+pounce[0])
        y.append(yy+pounce[1])
        z.append(zz+pounce[2]+offset[2])
        #move up and over
        if i < len(quad)-1:
            print quad[i+1][0][0]
            x.append((quad[i+1][0][0])+pounce[0])
            y.append((quad[i+1][0][1])+pounce[1])
            z.append((quad[i+1][0][2])+pounce[2]+offset[2])
line =[]          
for q in quad:
    if q in quad:
        continue
    else:
        line.append(q)
        
print line
 
def draw_faces2(offset=[0,0,0], do_pounce=True, pounce =[0.0, 0.0, 10.0]):

    start=[vertices[0][0], vertices[0][1]]
    print start
    for i, v in enumerate(vertices):
        fin = [v[len(v)-1],v[len(v)-2]]
        for xx,yy,zz in v:
            x.append(xx)
            y.append(yy)
            z.append(zz+offset[2])
        #move up and over
        if start==fin and pounce is not False and (i < len(vertices)-1) :
            print "finished vertices" 
            start=[vertices[i+1][0], vertices[i+1][1]]
            #move tool up
            x.append(xx+pounce[0])
            y.append(yy+pounce[1])
            z.append(zz+pounce[2]+offset[2])
            #move over to next point
            x.append((vertices[i+1][0][0])+pounce[0])
            y.append((vertices[i+1][0][1])+pounce[1])
            z.append((vertices[i+1][0][2])+pounce[2]+offset[2])


#draw_faces2()
#print len(x)#8764

#draw_vert()
print len(x)#1765
'''
xval = set(x)
yval = set(y)
zval = set(z)
print xval
print yval
print zval
'''
'''
xmax = max(x) 
xmin = min(x)
ymax = max(y) 
ymin = min(y)
zmax = max(z) 
zmin = min(z)
'''
# Create main figure
fig=p.figure()
fig.suptitle('Object', fontsize=14, fontweight='bold')
#ax = a3d.Axes3D(fig)

ax = Axes3D(fig)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.plot3D(xs,zs,ys, 'r-')
for v in (quad):
    x,y,z=[],[],[]
    for xx,yy,zz in v:
        x.append(xx)
        y.append(yy)
        z.append(zz)
    verts = [zip(x,y,z)]
    #ax.plot3D(xs1,ys1,zs1, 'r-')
    #ax.add_collection3d(Poly3DCollection(verts))
'''  
for i in  xrange(0,(len(x)-1),4):
    print i
    if i < len(x)-4:
        x0 = x[i]
        x1 = x[i+4]
        xs1.append((x0+x1)/2.0)
        y0 = y[i]
        y1 = y[i+4]
        ys1.append((y0+y1)/2.0)
        z0 = x[i]
        z1 = x[i+4]
        zs1.append((z0+z1)/2.0)
print xs1
print ys1
print zs1
ax.plot3D(xs1,ys1,zs1, 'r-')   

ax.set_xlim(xmin, xmax)  # comment this to see full plot
ax.set_ylim(ymin, ymax)  # comment this to see full plot
ax.set_zlim(zmin, zmax)  # comment this to see full plot
'''
p.show()

