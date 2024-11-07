# https://blender.stackexchange.com/questions/244976/bulk-remove-shape-key-drivers

import bpy
from bpy import context as C

for b in C.active_object.data.shape_keys.key_blocks:
    b.driver_remove('value')
