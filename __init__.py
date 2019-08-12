# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Lynchon Tools 2.80",
    "author" : "Lynchon",
    "description" : "",
    "version" : (1,0,3), 
    "blender" : (2, 81, 0),
    "location" : "",
    "warning" : "",
    "category" : "MMC"
}

import bpy
import sys
import importlib
from . import addon_updater_ops
#'Hidesato Offset Edges'
modulesNames = ['UI','y_up','xml_parse_particles', 'xml_parse_conformHeight', 'metal_compiler','edit_pivot','uv_tube_unwrap','Hidesato Offset Edges','fillet_280',]


 
modulesFullNames = {}
for currentModuleName in modulesNames:
    modulesFullNames[currentModuleName] = ('{}.{}'.format(__name__, currentModuleName))
 
for currentModuleFullName in modulesFullNames.values():
    if currentModuleFullName in sys.modules:
        importlib.reload(sys.modules[currentModuleFullName])
    else:
        globals()[currentModuleFullName] = importlib.import_module(currentModuleFullName)
        setattr(globals()[currentModuleFullName], 'modulesNames', modulesFullNames)
 
def register():
    
    addon_updater_ops.register(bl_info)

    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'register'):
                sys.modules[currentModuleName].register()
                
 
def unregister():

    addon_updater_ops.unregister()
    
    for currentModuleName in modulesFullNames.values():
        if currentModuleName in sys.modules:
            if hasattr(sys.modules[currentModuleName], 'unregister'):
                sys.modules[currentModuleName].unregister()
 
