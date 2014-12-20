import matplotlib.pyplot as plt
fig = plt.figure()
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)
ax4 = fig.add_axes([0.1, 0.5, 0.9, 0.3], frameon = False, visible = True)
ax4.plot([1,2,3,4,5,6])
fig.subplots_adjust(top = 1, bottom = 0, hspace = 0)

#ax1 =  plt.subplot2grid((3, 3), (0, 0))
#ax2 =  plt.subplot2grid((3, 3), (0, 1), colspan = 2)
#ax3 =  plt.subplot2grid((3, 3), (1, 0), colspan = 2, rowspan = 2)
#ax4 =  plt.subplot2grid((3, 3), (1, 2), rowspan = 2)
#plt.subplots_adjust(top = 1, bottom = 0, hspace = 0)
#print len(ax4.figure.axes)


plt.show()
