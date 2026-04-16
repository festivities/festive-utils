import bpy

def run():
    obj = bpy.context.active_object
    if not obj or obj.type != 'ARMATURE':
        print("Please select an armature.")
        return

    # Check the current mode and get selected bones accordingly
    mode = obj.mode
    if mode == 'POSE':
        selected_bones = bpy.context.selected_pose_bones
    elif mode == 'EDIT':
        selected_bones = bpy.context.selected_editable_bones
    else:
        print("Please swap bones in POSE or EDIT mode.")
        return

    # Make sure exactly 2 bones are selected
    if len(selected_bones) != 2:
        print(f"Error: {len(selected_bones)} bone(s) selected. Please select exactly 2 bones.")
        return

    bone1, bone2 = selected_bones
    name1 = bone1.name
    name2 = bone2.name

    # Swap vertex groups in all objects
    for ob in bpy.data.objects:
        vg1 = ob.vertex_groups.get(name1)
        vg2 = ob.vertex_groups.get(name2)
        
        if vg1 and vg2:
            vg1.name = "TEMP_VG_NAME_SWAP"
            vg2.name = name1
            vg1.name = name2
        elif vg1:
            vg1.name = name2
        elif vg2:
            vg2.name = name1

    # Swap names using a temporary name to avoid Blender auto-numbering collisions
    bone1.name = "TEMP_BONE_NAME_SWAP"
    bone2.name = name1
    bone1.name = name2

    print(f"Swapped bone names: '{name1}' <-> '{name2}'")

if __name__ == "__main__":
    run()