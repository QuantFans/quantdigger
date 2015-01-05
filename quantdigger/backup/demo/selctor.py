from matplotlib.widgets import  RectangleSelector
from pylab import *

def onselect(eclick, erelease):
  'eclick and erelease are matplotlib events at press and release'
  print ' startposition : (%f, %f)' % (eclick.xdata, eclick.ydata)
  print ' endposition   : (%f, %f)' % (erelease.xdata, erelease.ydata)
  print ' used button   : ', eclick.button

def toggle_selector(event):
    print ' Key pressed.'
    if event.key in ['Q', 'q'] and toggle_selector.RS.active:
        print ' RectangleSelector deactivated.'
        toggle_selector.RS.set_active(False)
    if event.key in ['A', 'a'] and not toggle_selector.RS.active:
        print ' RectangleSelector activated.'
        toggle_selector.RS.set_active(True)

x = arange(100)/(99.0)
y = sin(x)
fig = figure
ax = subplot(111)
ax.plot(x,y)

toggle_selector.RS = RectangleSelector(ax, onselect, drawtype='line')
connect('key_press_event', toggle_selector)
show()
