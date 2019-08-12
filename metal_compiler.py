import bpy
import os
from bpy import context
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

def compile_met(image_selected, imagename, fileroot, path):
        
        # retrieve bool from UI
        invert = bpy.data.scenes['Scene'].my_tool.invert

        # switch on nodes and get reference
        bpy.context.scene.use_nodes = True
        

        tree = bpy.context.scene.node_tree
                        
        # clear default nodes
        for node in tree.nodes:
                tree.nodes.remove(node)

        # create input nodes
        image = bpy.data.images.load(filepath= image_selected)
        image_node = bpy.context.scene.node_tree.nodes.new('CompositorNodeImage')
        image_node.image = image
        
        comp_node = bpy.context.scene.node_tree.nodes.new('CompositorNodeComposite')
        comp_node.location = 600,0

        output_node = bpy.context.scene.node_tree.nodes.new('CompositorNodeOutputFile')
        output_node.base_path = path
        output_node.file_slots[0].path = imagename
        output_node.location = 600,300
        
        setAlpha = bpy.context.scene.node_tree.nodes.new('CompositorNodeSetAlpha')
        setAlpha.location = 300,0 

        if invert == True:
                invert_node = bpy.context.scene.node_tree.nodes.new('CompositorNodeInvert')     
                invert_node.location = 150,0 
        
        # link nodes
        links = tree.links
        if invert == True:
               links.new(image_node.outputs['Image'], invert_node.inputs[1]) 
               links.new(invert_node.outputs[0], setAlpha.inputs[1])
               links.new(setAlpha.outputs['Image'], comp_node.inputs[0])
               links.new(setAlpha.outputs['Image'], output_node.inputs[0])
        else:

                links.new(image_node.outputs['Image'], setAlpha.inputs[1])
                links.new(setAlpha.outputs['Image'], comp_node.inputs[0])
                links.new(setAlpha.outputs['Image'], output_node.inputs[0])
        
        #render
        bpy.ops.render.render(use_viewport = False, write_still=True)
        
        
        

class metal_compiler(bpy.types.Operator,ImportHelper):
        """Tooltip"""
        bl_idname = "texture.metal_compiler"
        bl_label = "MET COMPILER"

        def execute(self, context):
                fileroot, extension = os.path.splitext(self.filepath)
                path = os.path.dirname(self.filepath)
                imagename = os.path.basename(fileroot)
                image_selected = self.filepath       
                compile_met(image_selected, imagename, fileroot, path)
                return {'FINISHED'}



classes = (metal_compiler,)

register, unregister = bpy.utils.register_classes_factory(classes)
