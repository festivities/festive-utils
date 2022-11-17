import bpy

const_targetChara = ' '

for x in bpy.context.active_object.vertex_groups:
    for chara in x.name:
        if chara == const_targetChara: x.name = x.name.replace(chara, '_')
