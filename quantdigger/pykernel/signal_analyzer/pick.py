import numpy as np
import matplotlib.pyplot as plt
fig = plt.figure()
ax = fig.add_subplot(111)
ax.set_title('click on points')
line, = ax.plot(np.random.rand(100), 'o', picker=5) # 5 points tolerance
def onpick(event):
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    print 'onpick points:', zip(xdata[ind], ydata[ind])
fig.canvas.mpl_connect('pick_event', onpick)
plt.show()
