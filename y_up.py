import bpy
import bmesh
import mathutils
import math


class LynchOperator(bpy.types.Operator):
    """Tooltip"""       
    bl_idname = "object.y_up"
    bl_label = "Y UP"

    def execute(self, context):
        y_rotation()
        return {'FINISHED'}

def y_rotation():
    for ob in  bpy.context.selected_objects:
        # Get the active mesh
        me = bpy.context.object.data


        # Get a BMesh representation
        bm = bmesh.new()   # create an empty BMesh
        bm.from_mesh(me)   # fill it in from a Mesh


        # Modify the BMesh, can do anything here...
        bmesh.ops.rotate(bm, cent=(0.0, 0.0, 0.0), matrix=mathutils.Matrix.Rotation(math.radians(-90.0), 3, 'X'), verts=bm.verts)


        # Finish up, write the bmesh back to the mesh
        bm.to_mesh(me)
        bm.free()  # free and prevent further access

        # Rotate object back -90
        bpy.ops.transform.rotate(value=1.5708, orient_axis='X', orient_type='LOCAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='LOCAL', constraint_axis=(True, False, False), mirror=True, use_proportional_edit=False, proportional_edit_falloff='RANDOM', proportional_size=9.84974, use_proportional_connected=False, use_proportional_projected=False)
        print("test");



classes = (LynchOperator,)

register, unregister = bpy.utils.register_classes_factory(classes)
