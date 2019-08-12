import bpy
import bmesh
import itertools
import mesh_f2
from bpy.types import Operator, AddonPreferences
from bpy.props import StringProperty
from functools import reduce
from bpy_extras.view3d_utils import region_2d_to_location_3d, region_2d_to_vector_3d
from mathutils import Vector
import math


class SimpleEditPivot(bpy.types.Operator):
	bl_idname = "mesh.simple_edit_pivot"
	bl_label = "Simple Edit Pivot"
	bl_description = "Edit pivot position and scale"
	bl_options = {'REGISTER', 'UNDO'}

	def create_pivot(self, context, obj):
		bpy.ops.object.empty_add(type='ARROWS', location= obj.location)
		pivot = bpy.context.active_object
		pivot.name = obj.name + ".PivotHelper"
		pivot.location = obj.location
		print("Pivot")

	def get_pivot(self,context, obj):
		pivot = obj.name + ".PivotHelper"
		if bpy.data.objects.get(pivot) is None:
			return False
		else:
			bpy.data.objects[obj.name].select_set(False)
			bpy.data.objects[pivot].select_set(True)
			context.view_layer.objects.active = bpy.data.objects[pivot]
			return True

	def apply_pivot(self,context, pivot):
		obj = bpy.data.objects[pivot.name[:-12]]
		piv_loc = pivot.location
		#I need to create piv as it seem like the pivot location is passed by reference? Still no idea why this happens
		cl = context.scene.cursor.location
		piv = (cl[0],cl[1],cl[2])
		context.scene.cursor.location = piv_loc
		bpy.context.view_layer.objects.active = obj
		bpy.data.objects[obj.name].select_set(True)
		bpy.ops.object.origin_set(type='ORIGIN_CURSOR', center='MEDIAN')
		context.scene.cursor.location = (piv[0],piv[1],piv[2])
		#Select pivot, delete it and select obj again
		bpy.data.objects[obj.name].select_set(False)
		bpy.data.objects[pivot.name].select_set(True)
		bpy.ops.object.delete()
		bpy.data.objects[obj.name].select_set(True)
		context.view_layer.objects.active = obj

	def execute(self, context):
		obj = bpy.context.active_object
		if  obj.name.endswith(".PivotHelper"):
			self.apply_pivot(context, obj)
		elif self.get_pivot(context, obj):
			piv = bpy.context.active_object
		else:
			self.create_pivot(context,obj)
		return{'FINISHED'}

classes = (SimpleEditPivot,)

register, unregister = bpy.utils.register_classes_factory(classes)