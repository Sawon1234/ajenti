import platform

from ajenti.com import Interface
from ajenti.ui import *
from ajenti import version
from ajenti.utils import detect_distro, detect_platform
from ajenti.api import *

from api import *


class Dashboard(CategoryPlugin):
    text = 'Dashboard'
    icon = '/dl/dashboard/icon_small.png'
    folder = 'top'

    widgets = Interface(IDashboardWidget)

    def on_session_start(self):
        self._left = []
        self._right = []
        if self.app.config.has_section('dashboard'):
            for k,v in self.app.config.items('dashboard'):
                v = v.split(',')
                (self._left if v[0] == 'left' else self._right).append((k,v[1]))
        self._left = [x[0] for x in sorted(self._left, key=lambda y: y[1])]                
        self._right= [x[0] for x in sorted(self._right,key=lambda y: y[1])]                

    def get_ui(self):
        li = []
        ri = []
        for wgt in self.app.grab_plugins(IDashboardWidget):
            (li if wgt.plugin_id in self._left else ri).append(wgt)
        li = sorted(li, key=lambda x: self._left.index(x.plugin_id))
        ri = sorted(ri, key=lambda x: self._right.index(x.plugin_id))
        
        lc = UI.VContainer(*[UI.Widget(x.get_ui(), pos='l', title=x.title, id=x.plugin_id) for x in li])
        rc = UI.VContainer(*[UI.Widget(x.get_ui(), pos='r', title=x.title, id=x.plugin_id) for x in ri])
        w = UI.HContainer(lc, rc)
        
        u = UI.PluginPanel(
                UI.Label(text=detect_distro()), 
                w, 
                title=platform.node(), 
                icon='/dl/dashboard/distributor-logo-%s.png'%detect_platform(mapping=False)
            )
        return u

    @event('widget/move')
    def on_move(self, event, params, vars=None):
        if params[1] == 'left':
            self._right.remove(params[0])
            self._left.append(params[0])
        if params[1] == 'right':
            self._left.remove(params[0])
            self._right.append(params[0])
        if params[1] == 'up':
            a = self._left if params[0] in self._left else self._right
            idx = a.index(params[0])
            if idx > 0:
                a[idx], a[idx-1] = a[idx-1], a[idx]
        if params[1] == 'down':
            a = self._left if params[0] in self._left else self._right
            idx = a.index(params[0])
            if idx < len(a)-1:
                a[idx], a[idx+1] = a[idx+1], a[idx]
                
        for w in self._left:
            self.app.config.set('dashboard', w, 'left,'+ str(self._left.index(w)))
        for w in self._right:
            self.app.config.set('dashboard', w, 'right,'+str(self._right.index(w)))
        self.app.config.save()
        