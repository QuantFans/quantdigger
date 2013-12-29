# -*- coding: gbk -*-
import matplotlib
matplotlib.use("TKAgg")
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm
import matplotlib.pyplot as plt
import numpy as np

import pandas as pd


fname = raw_input("Please input file name:  ")
fname = "c:\\TB输出文件\\"  + fname
data2 = pd.read_csv(fname)
data2 = data2.ix[1:, :]

fig = plt.figure()
ax = fig.gca(projection='3d')
X = data2.c.astype(float).tolist()
Y = data2.b.astype(float).tolist()
Z = data2.k.astype(float).tolist()

print "******************" 
#ax.plot_surface(xx, yy, Z, rstride=8, cstride=8, alpha=0.3)
#cset = ax.contourf(xx, yy, Z, zdir='z', offset=-100, cmap=cm.coolwarm)
#cset = ax.contourf(xx, yy, Z, zdir='x', offset=-40, cmap=cm.coolwarm)
#cset = ax.contourf(xx, yy, Z, zdir='y', offset=40, cmap=cm.coolwarm)
ax.set_xlabel('X')
#ax.set_xlim(-40, 40)
ax.set_ylabel('Y')
#ax.set_ylim(-40, 40)
ax.set_zlabel('Z')
#ax.set_zlim(-100, 100)

#lines = []
#l2d, = ax2.plot([0]*0)

#def on_pick(event):
    #'''docstring for on_motion''' 
    #global l2d
    #for i,line in enumerate(lines):
        ## code...
        #if line != event.artist:
            #line.set_visible(False)
        #else:
            #w = i

    #ax2.set_xlabel("%s"%(w+1))
    #l2d.remove()
    #l2d, = ax2.plot(y[w], z[w], 'ko')
    #fig.canvas.draw_idle()

#def on_button_release(event):
    #for line in lines:
        #line.set_visible(True)
    #fig.canvas.draw_idle()

#for i in range(len(x)):
    #lines.append(ax.scatter([x[i]]*len(y[i]), y[i], z[i], color=['red']*len(y[i]), picker=1))

#fig.canvas.mpl_connect('pick_event', on_pick)
#fig.canvas.mpl_connect('button_release_event', on_button_release)
#c1 = Cursor(ax2, useblit=True, color='red', linewidth=1, vertOn = True, horizOn = True)

#ax.set_ylim3d(min(y), max(y))
#ax.set_zlim3d(min(z), max(z))
#ax.set_xticklabels(range(len(data2.columns)+1))



ax.plot_trisurf(X, Y, Z, cmap=cm.jet, linewidth=0.2)
ax.scatter(X, Y, Z, color='k')

plt.show()

