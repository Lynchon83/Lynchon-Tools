import bpy
import os
import bmesh
import math
import mathutils


from xml.etree import ElementTree
from bpy.props import StringProperty, BoolProperty
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator



def createLowPolyVenue(tree, filename):

    for estadio in tree:
        #Create Venue parent
        O = bpy.data.collections.new(filename)
        
        bpy.context.scene.collection.children.link(O)
        O = bpy.data.collections[filename]

        for Sector in estadio.findall('Sector'):

            # Create Tiers
            tier = str(Sector.get('tier'))
            tier = tier.replace('T_0', '_TIER')
            tier = "00_LODs-" +filename.split("_")[1].split("-")[3]+ tier
            

            if bpy.data.collections.get(tier) is None:
                """ global tier_O """
                tier_O =  bpy.data.collections.new(tier)
                bpy.data.collections[O.name].children.link(bpy.data.collections[tier_O.name])         

            else:
                tier_O = bpy.data.collections[tier]
                

            #Create Sector
            mesh = bpy.data.meshes.new('mesh')
            sector = bpy.data.objects.new(Sector.get('id'), mesh)
            
            bpy.context.view_layer.objects.active = sector
            bm = bmesh.new()

            total_seats = 0


            # Parent sector to venue empty
            bpy.data.collections[tier_O.name].objects.link(sector)

            for Seat in Sector:

                # Get Position Data
                posX, posY, posZ = float(Seat.get('px')), float(Seat.get('py')), float(Seat.get('pz'))
                rotX, rotY, rotZ = float(Seat.get('rx')), float(Seat.get('ry')), float(Seat.get('rz'))

                #Total number of seats for each sector
                total_seats = total_seats + 1
                #Create vertex and face for each position and orient it
                v1 = bm.verts.new((-posX-0.01, -posZ, posY-0.01))
                v2 = bm.verts.new((-posX+0.01, -posZ, posY-0.01))
                v3 = bm.verts.new((-posX, -posZ, posY+0.01))
                f1 = bm.faces.new([v1,v2,v3])

                vert_list = [v1,v2,v3]
                mat_rot = mathutils.Matrix.Rotation(math.radians(-rotY+180), 3, 'Z')
                bmesh.ops.rotate(bm, cent= (-posX, -posZ, posY), matrix = mat_rot, verts= vert_list)



                #Detect seat and change name to convention while adding description from the seat model

                seat_type_lower = str(Seat.get('prefab')[2:9])
                seat_type = seat_type_lower.upper()
                seat_type = seat_type.replace('-','_')

                for obj in bpy.data.collections['seats_lp'].objects:

                    if obj.name[0:7] == seat_type:
                        seat_type = seat_type + obj.name[7:]

                #Create vertex group and assign vertices to vertex group

                dl = bm.verts.layers.deform.verify()
                seatID = str(Seat.get('name'))

                
                for v in f1.verts:
                    if sector.vertex_groups.get(seat_type) is None:
                        group = sector.vertex_groups.new(name=seat_type)
                        v[dl][group.index] = 1.0    

                    else:
                        group = sector.vertex_groups.find(seat_type)
                        v[dl][group] = 1.0
                        
                    
                    if sector.vertex_groups.get(seatID) is None:
                        group_seatID = sector.vertex_groups.new(name = seatID)
                        v[dl][group_seatID.index] = 1.0
                    
                    else:
                        group_seatID = sector.vertex_groups.find(seatID)
                        v[dl][group_seatID] = 1.0

            bm.to_mesh(mesh)
            bm.free()

            bpy.context.view_layer.objects.active = sector

            for vg in range(len(sector.vertex_groups)):


                bpy.context.view_layer.objects.active = sector
                sector_name = bpy.context.active_object.name
                vg_name =bpy.data.objects[sector_name].vertex_groups[vg].name

                if "SEAT" in vg_name:           

                    #Create particle system

                    sector.modifiers.new(name=seat_type, type = 'PARTICLE_SYSTEM')

                    part = sector.particle_systems[vg]

                    part.settings.emit_from = 'FACE'
                    part.settings.userjit = 1
                    part.settings.physics_type = 'NO'
                    part.settings.frame_start = 1.0
                    part.settings.frame_end = 1.0
                    part.settings.render_type = 'OBJECT'
                    part.settings.particle_size = 1
                    part.settings.use_emit_random = False

                    #Count number of vertices in each vertex group
                    o = bpy.context.object
                    vs = [v for v in o.data.vertices if vg in [vg.group for vg in v.groups]]
                    part.settings.count = len(vs) / 3 

                    part.settings.use_rotations = True
                    part.settings.rotation_mode = 'VEL'
                    part.settings.phase_factor = 0
                    part.settings.use_even_distribution = False

                    #Assign vertex group(seat type) to particle system
                    part.vertex_group_density = vg_name
                    #Assign seat model to particle system
                    part.settings.instance_object = bpy.data.collections['seats_lp'].objects[vg_name]

selection = []           

def getChildren():

    # x = bpy.ops.object.select_grouped(type='COLLECTION')
    x = bpy.context.collection

    print (x.objects)
    
    sel_obj = bpy.context.selected_objects
    
    for obj in x.objects:
        selection.append(obj)

    print(selection, sep="\n")
    return sel_obj

def convert_to_mesh():
    
    
    
    # bpy.ops.object.select_all(action='TOGGLE')

    for ob in selection:
        ob.select_set(state=True)
        bpy.ops.object.duplicates_make_real(use_base_parent=True, use_hierarchy=False)
        bpy.context.view_layer.objects.active = ob
        x = bpy.ops.object.select_grouped(type='CHILDREN_RECURSIVE')
        print (x, 'hola')
        ob.select_set(state=True)
        bpy.context.view_layer.objects.active = ob
        bpy.ops.object.join()
        ob.modifiers.clear()
        ob.select_set(state=False)
    del selection[:]



class XML_OT_lowPolyGeneratorParticles(Operator, ImportHelper):
    bl_idname = "xml.lowpolygeneratorparticles"
    bl_label = "Low poly venue Particles"

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
        tree = ElementTree.parse(self.filepath).getroot()
        filename = os.path.basename(file_root)
        createLowPolyVenue(tree, filename)

        print('Selected file:', self.filepath)
        print('File root:', file_root)
        print('File name:', filename)
        print('File extension:', extension)
        print('Some Boolean:', self.some_boolean)

        return {'FINISHED'}
class XML_OT_conformLpVenue(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "xml.conform_lp_venue"
    bl_label = "Collapse lp venue"

    def execute(self, context):
        getChildren()
        convert_to_mesh()
        return {'FINISHED'}

classes = (XML_OT_lowPolyGeneratorParticles, XML_OT_conformLpVenue,)

register, unregister = bpy.utils.register_classes_factory(classes)
 

