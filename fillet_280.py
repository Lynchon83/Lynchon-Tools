'''
Copyright (C) 2015 CG Cookie
http://cgcookie.com
hello@cgcookie.com

Created by Luxuy Liu
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

bl_info = {
    "name": "Bezier curve fillet tool",
    "description": "A small add-on for Blender 2.7x that makes a fillet between straight segments in bezier curve.",
    "author": "Luxuy Liu",
    "version": (1, 0, 0),
    "blender": (2, 80, 0),
    "location": "curve edit mode > W key > Bezier curve fillet, shortcut 'ctrl+F' in curve edit mode",
    "warning": '',  
    "category": "Add Curve"} 

from bpy.types import Menu, Panel, UIList
import bpy,math,mathutils,bmesh
from bpy.props import FloatProperty, IntProperty, BoolProperty,EnumProperty,StringProperty
from mathutils import Matrix,Vector,Color
import random,bgl
from math import *
from bpy_extras.mesh_utils import *
from mathutils.geometry import *


def get_fillet_pts(knot,hdl_left,hdl_right,rad):
    vec1=hdl_left-knot
    vec2=hdl_right-knot
    ang=vec1.angle(vec2)*0.5
    # print(ang)
    size=rad/tan(ang)
    
    vec1.length=size
    vec2.length=size
    
    return knot+vec1,knot+vec2,ang

    
def split_pt(cv):
    void_pts_dic={}
    sel_pts_dic={}
    for j,spl in enumerate(cv.data.splines):
        sel_pts_dic[str(j)]=[]
        void_pts_dic[str(j)]=[]
        for i,pt in enumerate(spl.bezier_points):
            if pt.select_control_point:
                if (not spl.use_cyclic_u) and (i==0 or i==len(spl.bezier_points)-1):
                    pass
                else:
                    sel_pts_dic[str(j)].append(i)
    for i,spl in enumerate(cv.data.splines):
        size=len(spl.bezier_points)
        times=len(sel_pts_dic[str(i)])
        for j in range(size-1,-1,-1):
            
            if j in sel_pts_dic[str(i)]:
                
                bpy.ops.curve.select_all(action='DESELECT')
                spl.bezier_points[j].select_control_point=True
                spl.bezier_points[(j+1)%size].select_control_point=True
                bpy.ops.curve.subdivide()
                void_pts_dic[str(i)].append([j+times-1,spl.bezier_points[j].co.copy(),j+1+times-1])
                times=times-1
                
                spl.bezier_points[j+1].co=spl.bezier_points[j+1].co*0.1+spl.bezier_points[j].co*0.9
                
                spl.bezier_points[j].co=spl.bezier_points[j].co*0.9+spl.bezier_points[j-1].co*0.1
    
    bpy.ops.curve.select_all(action='DESELECT')
    return void_pts_dic
def cv_fillet(cv,void_pts_dic,rad,k):
    for key in void_pts_dic.keys():
        spl=cv.data.splines[int(key)]
        # ppt=void_pts_dic[key]
        for arr in void_pts_dic[key]:
            p1=spl.bezier_points[arr[0]].handle_left
            p2=arr[1]
            p3=spl.bezier_points[arr[2]].handle_right
            # print("*"*30)
            # print(p2,p1,p3,rad)
            ret=get_fillet_pts(p2,p1,p3,rad)
            
            spl.bezier_points[arr[0]].handle_right_type="FREE"
            spl.bezier_points[arr[2]].handle_left_type="FREE"
            spl.bezier_points[arr[0]].co=ret[0]
            spl.bezier_points[arr[2]].co=ret[1]
            if abs(k)<10e-5:
                spl.bezier_points[arr[0]].handle_right=ret[0]+(p3-p1).normalized()*0.01
                spl.bezier_points[arr[2]].handle_left=ret[1]+(p1-p3).normalized()*0.01
            else:
                ang=pi-(p1-p2).angle(p3-p2)
                spl.bezier_points[arr[0]].handle_right=ret[0]+(p2-p1).normalized()*rad*tan(ang/3)*k
                spl.bezier_points[arr[2]].handle_left=ret[1]+(p2-p3).normalized()*rad*tan(ang/3)*k
        
#========================================================================================
def draw_gl_line(context,pts,width,dash,color): #pts matrix_world
    bgl.glLineWidth(width)
    bgl.glEnable(bgl.GL_BLEND)
    bgl.glColor4f(color[0],color[1],color[2],color[3])
    if dash:
        bgl.glEnable(bgl.GL_LINE_STIPPLE)
    # Draw  stuff.
    bgl.glBegin(bgl.GL_LINE_STRIP) 
   
    for pt in pts:
        bgl.glVertex2i(pt[0], pt[1])       
    bgl.glEnd()
    
    # restore opengl defaults
    bgl.glLineWidth(1)
    bgl.glDisable(bgl.GL_BLEND)
    bgl.glColor4f(0.0, 0.0, 0.0, 1.0)
    bgl.glDisable(bgl.GL_LINE_STIPPLE)
    

def draw_callback(self, context,event):
    
   
    line=[self._initial_mouse,self.m_pos]
    draw_gl_line(context,line,1,True,(0.5,0.5,0.5,0.5))
    
class BezierCurveFillet(bpy.types.Operator):
    bl_idname = "curve.fillet"
    bl_label = "Bezier curve fillet"
    bl_options = {'REGISTER', 'UNDO'}
    
    
    rad:FloatProperty(name='Radius:',default=0.3,min=0.1,max=30)
    k:FloatProperty(name='Handle Ratio:',default=1,min=0.0,max=30)
   

    @classmethod
    def poll(cls, context):
        if context.mode=='EDIT_CURVE':
            return True

    def modal(self, context, event):
        # print(event.type)
        context.area.tag_redraw()
        cv=context.object
        if context.space_data.type == 'VIEW_3D':
            
            self.m_pos=(event.mouse_region_x, event.mouse_region_y)
            gap=math.sqrt((self._initial_mouse[0]-self.m_pos[0])**2+(self._initial_mouse[1]-self.m_pos[1])**2)
            
            if event.type == 'MOUSEMOVE':

                
                if event.ctrl:
                    self.k=10.0/1500*gap
                else:
                    self.rad=10.0/1500*gap
                void_pts_dic=self.void_pts_dic
                cv_fillet(cv,void_pts_dic,self.rad,self.k)
                
                context.area.header_text_set("          Confirm: Enter/LClick, Cancel: Esc/RClick, MouseMove: Radius[ %.2f ]  (Ctrl)Handle ratio[ %.2f ]"%(self.rad,self.k))
                return {'RUNNING_MODAL'}
        if event.type in { 'LEFTMOUSE','RET'}:
            
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            #context.area.header_text_set()
            self.execute(context)
            return {'FINISHED'}
        if event.type in { 'ESC','RIGHTMOUSE'}:
            bpy.types.SpaceView3D.draw_handler_remove(self._handle, 'WINDOW')
            
            context.area.header_text_set()
            return {'CANCELLED'}
        if event.type in { 'Z'}:
            if not event.ctrl:
                return {'PASS_THROUGH'} 
            
        return {'RUNNING_MODAL'}
    def invoke(self, context, event):
        if context.space_data.type == 'VIEW_3D':
            self._initial_mouse = (event.mouse_region_x, event.mouse_region_y)

            cv=context.object
            bpy.ops.curve.handle_type_set(type='VECTOR')

            self.void_pts_dic=split_pt(cv)
            
            self._handle = bpy.types.SpaceView3D.draw_handler_add(
                            draw_callback,
                            (self, context,event),'WINDOW',
                            'POST_PIXEL')
            context.window_manager.modal_handler_add(self)

        return {'RUNNING_MODAL'}
    
    def execute(self, context):
        cv=context.object
        self.void_pts_dic=split_pt(cv)
        void_pts_dic=self.void_pts_dic
        # print("-"*30)
        # print(self.void_pts_dic)
        cv_fillet(cv,void_pts_dic,self.rad,self.k)
        return {'FINISHED'}
        


    
        

        

# class DATA_PT_spline_handle(bpy.types.Panel):

    # bl_space_type = 'PROPERTIES'
    # bl_region_type = 'WINDOW'
    # bl_context = "data"
    # bl_label = "Spline Handles"
    # @classmethod
    # def poll(cls, context):
        # return context.object.type=='CURVE'
    # def draw(self,context):
        # l=self.layout
        # l.operator("curve.fillet")
#---------------------------------------------
def menu_func(self, context):
    self.layout.operator_context = 'INVOKE_DEFAULT'
    layout=self.layout
   
    layout.operator(BezierCurveFillet.bl_idname,text="Bezier curve fillet")


def register():
    bpy.utils.register_class(BezierCurveFillet)
    # bpy.types.VIEW3D_PT_tools_curveedit.append(menu_func)
   
    bpy.types.VIEW3D_MT_edit_curve_context_menu.append(menu_func)
    
    km = bpy.context.window_manager.keyconfigs.default.keymaps['Curve']
    kmi = km.keymap_items.new(BezierCurveFillet.bl_idname, 'F', 'PRESS',ctrl=True)


def unregister():
    bpy.utils.unregister_class(BezierCurveFillet)

if __name__ == "__main__":
    register()