import matplotlib.pyplot as plt
fig = plt.figure()
ax1 = fig.add_subplot(311, rowspan = 2)
ax2 = fig.add_subplot(312)
fig.subplots_adjust(top = 1, bottom = 0, hspace = 0)

#ax1 =  plt.subplot2grid((3, 3), (0, 0))
#ax2 =  plt.subplot2grid((3, 3), (0, 1), colspan = 2)
#ax3 =  plt.subplot2grid((3, 3), (1, 0), colspan = 2, rowspan = 2)
#ax4 =  plt.subplot2grid((3, 3), (1, 2), rowspan = 2)
#plt.subplots_adjust(top = 1, bottom = 0, hspace = 0)
#print len(ax4.figure.axes)


plt.show()
