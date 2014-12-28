import numpy as np
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title('click on points')
line, = ax.plot(np.random.rand(100), 'o', picker=5) # 5 points tolerance
print id(line)
display = True


def enter_axes(event):
    """docstring for enter_axes""" 
    print "hello" 

def onpick(event):
    global display
    thisline = event.artist  # == line
    print id(thisline)
    xdata = thisline.get_xdata() # Point Set
    ydata = thisline.get_ydata()
    if display:
        ax.set_visible(False)
        display = False
    else:
        ax.set_visible(True)
        display = True
    ind = event.ind
    fig.canvas.draw()
    print 'onpick points:', zip(xdata[ind], ydata[ind])

fig.canvas.mpl_connect('pick_event', onpick)
fig.canvas.mpl_connect('axes_enter_event', enter_axes)

plt.show()
