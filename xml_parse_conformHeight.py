import bpy
import os
import math
import mathutils
from mathutils import Vector, Matrix
from math import radians


from xml.etree import ElementTree
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator





def conformHeight(tree):
    # retrieve float from UI
    threshold = bpy.data.scenes['Scene'].my_tool.conform_threshold

    tree_p = tree.getroot()

    #READ XML
    for venue in tree_p:

        for Sector in venue.findall('Sector'):

            for Seat in Sector:

                # Get Position Data
                posX, posY, posZ = float(Seat.get('px')), float(Seat.get('py')), float(Seat.get('pz'))
                rotY = radians(float(Seat.get('ry')))
                vec = mathutils.Vector((-posX,-posZ,posY))

                # vec.rotate(Matrix.Rotation(radians(180), 3, 'Z'))


                obj = bpy.context.object
                vecDir = mathutils.Vector((math.sin(rotY), math.cos(rotY), 0))
                origin = vec + (vecDir*(threshold))

                direction = Vector((0, 0, 1))
                direction.normalize()

                def ray_cast():
                   
                    sol = obj.ray_cast(origin + direction * 1000.0, -direction)
                    location = sol[1]

                    return  location
                
                ray_cast()


                loc = ray_cast()
                

                new_height = (loc[2])
                new_height_f = '{:.3f}'.format(new_height)  
                
                print(new_height_f)
                Seat.set('py', new_height_f)



def writeXML(tree, filename):

    # retrieve stringproperty(folder path) from UI
    path = bpy.data.scenes['Scene'].my_tool.path
    
    tree.write(path + filename + "_output" + '.xml', encoding='utf-8', xml_declaration=True, method="xml")


class XML_OT_conformheight(Operator, ImportHelper):
    bl_idname = "xml.conformheight"
    bl_label = "Conform Height"

    filter_glob : StringProperty(
        default='*.xml',
        options={'HIDDEN'}
    )

    some_boolean : BoolProperty(
        name='Do a thing',
        description='Do a thing with the file you\'ve selected',
        default=True,
    )

    def execute(self, context):
        """Do something with the selected file(s)."""

        file_root, extension = os.path.splitext(self.filepath)
        print(self.filepath)

        tree = ElementTree.parse(self.filepath)
        #tree_p = ElementTree.parse(self.filepath).getroot()
        filename = os.path.basename(file_root)
        conformHeight(tree)
        writeXML(tree,filename)

        print('Selected file:', self.filepath)
        print('File root:', file_root)
        print('File name:', filename)
        print('File extension:', extension)
        print('Some Boolean:', self.some_boolean)

        return {'FINISHED'}




classes = (XML_OT_conformheight,)

register, unregister = bpy.utils.register_classes_factory(classes)