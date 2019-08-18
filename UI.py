
import bpy
from bpy.props import (StringProperty,
                   BoolProperty,
                   IntProperty,
                   FloatProperty,
                   EnumProperty,
                   PointerProperty
                   )
from bpy.types import (Panel,
                   Operator,
                   PropertyGroup
                   )
from . import addon_updater_ops

class MySettings(PropertyGroup):

    path : StringProperty(
        name="path",
        description="Path to Directory",
        default="",
        maxlen=1024,
        subtype='DIR_PATH')

    conform_threshold : FloatProperty(
        name="conform_threshold",
        description="A float property",
        default=0.1,
        min=-5,
        max=30.0)

    invert : BoolProperty(
        name="Enable or Disable",
        description="A simple bool property",
        default = False) 

class UI_PT_LynchonPanel(bpy.types.Panel):
    """Las super herramientas de Juan"""
    bl_idname = 'UI_PT_LynchonPanel'
    bl_label = "Lynchon Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Lynchon Tools"
    
    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("object.y_up") 
        row = layout.row()
        row.operator("mesh.simple_edit_pivot") 
        
        row = layout.row()
        row.operator("uv.tube_uv_unwrap") 

        split = layout.split()

       
        # First column
        col = split.column()
        col.operator("mesh.hidesato_offset_edges", text='Offset').geometry_mode='offset' 
        col = split.column(align=True)
        # Second column
        col.operator("mesh.hidesato_offset_edges", text='Offset Extrude').geometry_mode='extrude' 
        col = split.column(align=True)
        col.operator("mesh.hidesato_offset_edges_profile", text='Offset with Profile') 

        row = layout.row()
        row.operator("curve.fillet") 

        row = layout.row()
        row.operator("object.stair_maker") 
        
        # split = layout.split()
        # # First column
        # col = split.column()
        # col.operator("texture.metal_compiler")
        
        # # Second column
        # scn = context.scene
        # mytool = scn.my_tool
        # col = split.column(align=True)
        # col.prop(mytool, 'invert' ,text = "Invert")   

class UI_PT_LynchonMMCPanel(bpy.types.Panel):
    """Las super herramientas de Juan"""
    bl_idname = 'UI_PT_LynchonMMCPanel'
    bl_label = "MMC Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = "UI"
    bl_category = "Lynchon Tools"
    

    def draw(self, context):
        layout = self.layout

        scn = context.scene
        mytool = scn.my_tool
      
        split = layout.split()

        # First column
        col = split.column()
        col.label(text="Import Venue")
        col.operator( "xml.lowpolygeneratorparticles")

        # Second column, aligned
        col = split.column(align=True)
        col.label(text="Collapse Venue")
        col.operator( "xml.conform_lp_venue")
               
        # Create two columns, by using a split layout.  
        split = layout.split()

        # First column
        col = split.column()
        col.operator("xml.conformheight")

        # Second column, aligned
        col = split.column(align=True)
        col.prop(mytool, "conform_threshold")
        # root for export
        col = layout.column(align=True)
        col.prop(mytool, "path", text="")
 
class UI_PT_LynchoToolsPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    ####### HIDESATO OFFSET EDGES  PREFERENCES#####
    interactive: bpy.props.BoolProperty(
        name = "Interactive",
        description = "makes operation interactive",
        default = True)
    free_move: bpy.props.BoolProperty(
        name = "Free Move",
        description = "enables to adjust both width and depth while pressing ctrl-key",
        default = False)
    

    ####### UPDATER PREFERENCES#####
    auto_check_update : bpy.props.BoolProperty(
        name="Auto-check for Update",
        description="If enabled, auto-check for updates using an interval",
        default=False,
    )
    
    updater_intrval_months : bpy.props.IntProperty(
        name='Months',
        description="Number of months between checking for updates",
        default=0,
        min=0
    )
    
    updater_intrval_days : bpy.props.IntProperty(
        name='Days',
        description="Number of days between checking for updates",
        default=7,
        min=0,
        max=31
    )
    
    updater_intrval_hours : bpy.props.IntProperty(
        name='Hours',
        description="Number of hours between checking for updates",
        default=0,
        min=0,
        max=23
    )
    
    updater_intrval_minutes : bpy.props.IntProperty(
        name='Minutes',
        description="Number of minutes between checking for updates",
        default=0,
        min=0,
        max=59
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "interactive")
        if self.interactive:
            row.prop(self, "free_move")

        col = layout.column() # works best if a column, or even just self.layout
        mainrow = layout.row()
        col = mainrow.column()

 		# updater draw function
 		# could also pass in col as third arg
        addon_updater_ops.update_settings_ui(self, context)

		# Alternate draw function, which is more condensed and can be
		# placed within an existing draw function. Only contains:
		#   1) check for update/update now buttons
		#   2) toggle for auto-check (interval will be equal to what is set above)
        # addon_updater_ops.update_settings_ui_condensed(self, context, col)

		# Adding another column to help show the above condensed ui as one column
        # col = mainrow.column()
        # col.scale_y = 2
        # col.operator("wm.url_open","Open webpage ").url=addon_updater_ops.updater.website)       

def register():
      
    bpy.utils.register_class(UI_PT_LynchonMMCPanel)
    bpy.utils.register_class(UI_PT_LynchonPanel)
    bpy.utils.register_class(MySettings)
    bpy.types.Scene.my_tool = PointerProperty(type=MySettings)
    bpy.utils.register_class(UI_PT_LynchoToolsPreferences)


def unregister():
    
    bpy.utils.unregister_class(UI_PT_LynchonMMCPanel)
    bpy.utils.unregister_class(UI_PT_LynchonPanel)
    bpy.utils.unregister_class(MySettings)
    del bpy.types.Scene.my_tool
    bpy.utils.unregister_class(UI_PT_LynchoToolsPreferences)
