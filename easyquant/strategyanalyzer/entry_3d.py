#import xlrd
#data = xlrd.open_workbook('1.xls')
#table = data.sheets()[0]
#for i in range(table.nrows):
    #print table.row_values(i)

import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib
matplotlib.use("TKAgg")
import matplotlib.pyplot as plt
from itertools import groupby
from pprint import pprint
from matplotlib.widgets import Cursor
fname = raw_input("Please input file name:  ")
data2 = pd.read_csv(fname)
data2 = data2.ix[:, 2:-1]
def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]


#def group(ylist, dist=0):
    #'''''' 
    #ylist.sort()
    #groups = { }
    #uni = sorted(list(set(ylist)))
    #uni = list(chunks(uni, 5))
    #found = False
    #gd = []
    #preseed = uni[0][len(uni[0])/2]
    #for d in ylist:
        #for g in uni:
            ## find the right group
            #if d in g:
                #seed = g[len(g)/2]
                #if preseed != seed:
                    #groups[preseed] = gd
                    #gd = []
                #gd.append(d)
                #preseed = seed
                #break
    #groups[seed] = gd
    #return groups


def process(data2):
    '''docstring for process''' 
    xlist = []
    ylist = []
    zlist = []
    #print groups.keys()
    for i in range(len(data2.columns)):
        zi = data2.ix[:, i]
        #groups = group(zi.tolist())
        n, bins = np.histogram(zi.tolist(), 40)
        xlist.append(i+1)
        ylist.append(bins[:-1])
        zlist.append(n)
    return xlist, ylist, zlist


fig = plt.figure()
ax = fig.add_subplot(211, projection='3d')
ax2 = fig.add_subplot(212)
ax2.autoscale_view()

#x = data2.c.astype(float).tolist()
#y = data2.b.astype(float).tolist()
#z = data2.k.astype(float).tolist()
x, y, z = process(data2)
lines = []
l2d, = ax2.plot([0]*0)

def on_pick(event):
    '''docstring for on_motion''' 
    global l2d
    for i,line in enumerate(lines):
        # code...
        if line != event.artist:
            line.set_visible(False)
        else:
            w = i

    ax2.set_xlabel("%s"%(w+1))
    l2d.remove()
    l2d, = ax2.plot(y[w], z[w], 'ko')
    fig.canvas.draw_idle()
    print str(event.mouseevent.xdata)

def on_button_release(event):
    for line in lines:
        line.set_visible(True)
    fig.canvas.draw_idle()

for i in range(len(x)):
    lines.append(ax.scatter([x[i]]*len(y[i]), y[i], z[i], color=['red']*len(y[i]), picker=1))

fig.canvas.mpl_connect('pick_event', on_pick)
fig.canvas.mpl_connect('button_release_event', on_button_release)
c1 = Cursor(ax2, useblit=True, color='red', linewidth=1, vertOn = True, horizOn = True)

#ax.set_ylim3d(min(y), max(y))
#ax.set_zlim3d(min(z), max(z))
#ax.set_xticklabels(range(len(data2.columns)+1))

plt.show()

