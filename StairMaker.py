import bpy, bmesh, mathutils, math
from mathutils import Vector, Matrix
from mathutils.geometry import intersect_line_plane, intersect_point_line, intersect_line_line
from math import sin, cos, pi, sqrt, degrees, tan, radians
from colorsys import hsv_to_rgb, rgb_to_hsv
import os, urllib
from bpy.props import (BoolProperty,
                       FloatProperty,
                       StringProperty,
                       EnumProperty,
                       IntProperty,
                       CollectionProperty,
                       FloatVectorProperty
                       )
from bpy_extras.io_utils import ExportHelper, ImportHelper
from bpy.types import Operator
import time
from collections import namedtuple
from operator import mul, itemgetter, add, attrgetter
from functools import reduce
from abc import abstractmethod, ABCMeta
from addon_utils import check

list_z = []
mats_idx = []
list_f = []
maloe = 1e-5
steps_smoose = 0
omsureuv_all_scale_def_glob = 1.0   

def check_lukap(bm):
    if hasattr(bm.verts, "ensure_lookup_table"):
        bm.verts.ensure_lookup_table()
        bm.edges.ensure_lookup_table()
        bm.faces.ensure_lookup_table()  
    
def StairsMaker():
    #bpy.ops.object.mode_set(mode='OBJECT')
    #bpy.ops.object.mode_set(mode='EDIT')

    obj = bpy.context.active_object
    mesh = obj.data

    # Найти верхнюю и нижнюю Z-координаты и вычислить dZ
    vcoz = [v.co.z for v in mesh.vertices if v.select]
    z_max = max(vcoz)
    z_min = min(vcoz)
    dZ = z_max - z_min

    # Определить количество лесенок (фейсов) Pc
    faces_selected = [f for f in mesh.polygons if f.select]
    Pc = len(faces_selected)

    # Вычисить высоту лесенок dZ/(Pc+1)=h0
    h0 = dZ / (Pc + 1)

    #print_info("H/S = %.4f / %d = %.4f" % (dZ, Pc + 1, h0), self)

    # Построить лесенку
    bm = bmesh.new()
    bm.from_mesh(mesh)
    check_lukap(bm)

    lEdges_select_idx = [e.index for e in mesh.edges if e.select]
    lFaces_select = [p for p in mesh.polygons if p.select]
    lEdges_select = [mesh.edges[i] for i in lEdges_select_idx]

    def findNearestPols(pol, sel_pols):
        lEdges_ = [e for e in pol.edge_keys]
        lEdges = list(add(*zip(*lEdges_)))

        lEdges_pols = [p.edge_keys for p in sel_pols if p != pol]
        lEdges_sel_ = [e for e in lEdges_pols]
        tmp = list(*zip(*zip(lEdges_sel_)))
        tmp_ = []
        for line in tmp:
            tmp_.extend(line)

        lEdges_sel = list(add(*zip(*tmp_)))
        lNearest_pols = set(lEdges) & set(lEdges_sel)
        count = len(lNearest_pols)
        return count, list(lNearest_pols)

    def findNearestEdges(sel_pols, sel_edges):
        lEdges_sel_ = [p.edge_keys for p in sel_pols]
        lEdges_sel = []
        lEdges_for_sel = []
        sel_edges_ = [(e.vertices[0], e.vertices[1]) for e in sel_edges]
        sel_edges_.extend([(e.vertices[1], e.vertices[0]) for e in sel_edges])
        for te in lEdges_sel_:
            for e in te:
                if e in lEdges_sel and e in sel_edges_:
                    lEdges_for_sel.append(e)

            lEdges_sel.extend(te)

        lEdges_ = list(set(lEdges_for_sel))
        lEdges = [e.index for e in sel_edges if (e.vertices[0], e.vertices[1]) in lEdges_ or \
                  (e.vertices[1], e.vertices[0]) in lEdges_]
        return lEdges

    def memory_new_edge(v0, v1, lverts, ledges, base_vi):
        lverts.extend([v0, v1])
        ledges.append((base_vi, base_vi + 1))
        # base_vi += 2

    def memory_new_face(lverts, lfaces, base_vi):
        v0, v1, v2, v3 = base_vi - 2, base_vi - 1, base_vi + 1, base_vi
        dv01 = lverts[v0] - lverts[v1]
        dv32 = lverts[v3] - lverts[v2]
        if dv01 @ dv32 < 0:
            v2, v3 = base_vi, base_vi + 1

        lfaces.append((v0, v1, v2, v3))

    def createMeshFromData(name, origin, verts, faces):
        # Создание меша и объекта
        bpy.ops.object.mode_set(mode='OBJECT')
        me = bpy.data.meshes.new(name + 'Mesh')
        ob = bpy.data.objects.new(name, me)
        ob.location = origin
        ob.show_name = True

        # Привязка объекта к сцене, он становится активным
        scn = bpy.context.scene
        scn.collection.objects.link(ob)
        bpy.context.view_layer.objects.active = ob
        ob.select_set  (True)

        # Создание меша из полученных verts (вершин), faces (граней).
        me.from_pydata(verts, [], faces)
        # Обновление меша с новыми данными
        me.update()
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.normals_make_consistent(inside=False)
        return ob

    lEdgesAll = findNearestEdges(lFaces_select, lEdges_select)
    extr_pols = []
    for pol in lFaces_select:
        test, npls = findNearestPols(pol, lFaces_select)
        if test == 2:
            extr_pols.append(pol.index)
            continue

    if len(extr_pols) == 2:
        c0 = abs(mesh.polygons[extr_pols[0]].center.z - z_max)
        c1 = abs(mesh.polygons[extr_pols[1]].center.z - z_max)
        if c1 < c0: extr_pols.reverse()

        start_face = extr_pols[0]
        end_face = extr_pols[1]

        cener0 = abs((sum([v.co.z for v in bm.edges[lEdgesAll[0]].verts]) / 2) - z_max)
        cener1 = abs((sum([v.co.z for v in bm.edges[lEdgesAll[-1]].verts]) / 2) - z_max)
        if cener1 < cener0: lEdgesAll.reverse()

        verts_unpack_faces_ = [(e.verts[0], e.verts[1]) for e in bm.faces[start_face].edges]
        verts_unpack_faces = list(add(*zip(*verts_unpack_faces_)))  # [(,),(,)] -> [,,,]
        all_verts_ = [(e.verts[0], e.verts[1]) for e in [bm.edges[ei] for ei in lEdgesAll]]
        all_verts = list(add(*zip(*all_verts_)))  # [(,),(,)] -> [,,,]
        verts_start_edge = list(set(verts_unpack_faces) ^ set(all_verts))

        verts_end_edge = [v for v in bm.edges[lEdgesAll[-1]].verts]
        start_edge = [e for e in bm.faces[start_face].edges \
                      if e.verts[0] in verts_start_edge \
                      and e.verts[1] in verts_start_edge][0]

        end_edge = [e for e in bm.faces[end_face].edges \
                    if e.verts[0] not in verts_start_edge \
                    and e.verts[1] not in verts_start_edge][0]

        ## Сортируем список
        centre_edges = [(bm.edges[ei].verts[0].co + bm.edges[ei].verts[1].co) / 2 for ei in lEdgesAll]
        size = len(centre_edges)
        kd = mathutils.kdtree.KDTree(size)
        for i, p in enumerate(centre_edges):
            kd.insert(p, i)
        kd.balance()
        point = (start_edge.verts[0].co + start_edge.verts[1].co) / 2
        lEdgesAll_ = []
        for (co, index, dist) in kd.find_n(point, size):
            lEdgesAll_.append(lEdgesAll[index])
            edge_ = bm.edges[lEdgesAll[index]]

        lEdgesAll = lEdgesAll_

        ## lEdgesAll - упорядоченный список ребер сверху вниз
        top = z_max
        # base_vi = len(bm.verts)
        base_vi = 2
        ex_lEdgesAll = lEdgesAll + [end_edge.index]
        prev_edge = start_edge
        v2_prev = prev_edge.verts[0].co.copy()
        v3_prev = prev_edge.verts[1].co.copy()
        new_verts_co = [v2_prev, v3_prev]
        new_edges = [(0, 1)]
        new_faces = []

        for i, ei in enumerate([start_edge.index] + lEdgesAll):
            top -= h0
            edge_ = bm.edges[ei]
            v0_ = edge_.verts[0].co.copy()
            v1_ = edge_.verts[1].co.copy()
            v0_.z = v1_.z = top
            memory_new_edge(v0_, v1_, new_verts_co, new_edges, base_vi)
            memory_new_face(new_verts_co, new_faces, base_vi)
            base_vi += 2

            next_edge_ = bm.edges[ex_lEdgesAll[i]]
            v2_ = next_edge_.verts[0].co.copy()
            v3_ = next_edge_.verts[1].co.copy()
            v2_.z = v3_.z = top
            memory_new_edge(v2_, v3_, new_verts_co, new_edges, base_vi)
            memory_new_face(new_verts_co, new_faces, base_vi)
            base_vi += 2

            v2_prev, v3_prev = v2_, v3_

        top -= h0
        v0_ = v3_prev.copy()
        v1_ = v2_prev.copy()
        v0_.z = v1_.z = top
        memory_new_edge(v0_, v1_, new_verts_co, new_edges, base_vi)
        memory_new_face(new_verts_co, new_faces, base_vi)
        base_vi += 2

        obj_lift = createMeshFromData("new_lift", obj.location, new_verts_co, new_faces)
        #edit_mode_out()
        bpy.context.view_layer.objects.active = obj
        obj.select_set (True)
        obj_lift.select_set  (False)
        #edit_mode_in()

    bm.free()
    
    


class StairMaker(bpy.types.Operator):
    """Tooltip"""       
    bl_idname = "object.stair_maker"
    bl_label = "StairMaker"

    def execute(self, context):
        StairsMaker()
        return {'FINISHED'}


def register():
    
    bpy.utils.register_class(StairMaker)
    


def unregister():
    
    bpy.utils.unregister_class(StairMaker)    