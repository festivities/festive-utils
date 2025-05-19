import bpy
import math

from bpy.types import NodeTree

images = bpy.data.images

def sameMaterial(a, b):
    tree_a: NodeTree = a.node_tree
    img_a = None

    for node in tree_a.nodes:
        if node.bl_idname == 'ShaderNodeTexImage':
            img_a = node.image.name
            break

    tree_b: NodeTree = b.node_tree
    img_b = None

    for node in tree_b.nodes:
        if node.bl_idname == 'ShaderNodeTexImage':
            img_b = node.image.name
            break
    
    return img_a == img_b

merged_mats = []

for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for slot in obj.material_slots:
            mat:bpy.types.Material = slot.material
            for merged_mat in merged_mats:
                if sameMaterial(merged_mat, mat):
                    slot.material = merged_mat
                    break
            else:
                merged_mats.append(mat)
