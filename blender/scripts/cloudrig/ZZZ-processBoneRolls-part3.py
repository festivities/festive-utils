import bpy
import math
import ast
import os

SPINE_BONES = {
    "Hips",
    "Spine0",
    "Spine1",
    "Chest",
    "Neck",
    "Head"
}

def get_rename_map_values():
    return {
        "Hips", "Spine0", "Spine1", "Chest", "Neck", "Head",
        "Shoulder.L", "Shoulder.R", "UpperArm.L", "UpperArm.R", "Forearm.L", "Forearm.R", "Hand.L", "Hand.R",
        "Finger_Thumb1.L", "Finger_Thumb2.L", "Finger_Thumb3.L",
        "Finger_Thumb1.R", "Finger_Thumb2.R", "Finger_Thumb3.R",
        "Finger_Index1.L", "Finger_Index2.L", "Finger_Index3.L",
        "Finger_Index1.R", "Finger_Index2.R", "Finger_Index3.R",
        "Finger_Middle1.L", "Finger_Middle2.L", "Finger_Middle3.L",
        "Finger_Middle1.R", "Finger_Middle2.R", "Finger_Middle3.R",
        "Finger_Ring1.L", "Finger_Ring2.L", "Finger_Ring3.L",
        "Finger_Ring1.R", "Finger_Ring2.R", "Finger_Ring3.R",
        "Finger_Pinky1.L", "Finger_Pinky2.L", "Finger_Pinky3.L",
        "Finger_Pinky1.R", "Finger_Pinky2.R", "Finger_Pinky3.R",
        "Thigh.L", "Thigh.R", "Knee.L", "Knee.R", "Foot.L", "Foot.R", "Toes.L", "Toes.R"
    }

def flip_these():
    return {
        "Shoulder.L", "Shoulder.R", "UpperArm.L", "UpperArm.R", "Forearm.L", "Forearm.R", "Hand.L", "Hand.R",
        "Thigh.L", "Thigh.R", "Knee.L", "Knee.R", "Foot.L", "Foot.R", "Toes.L", "Toes.R",
        "Thigh_1.L", "Thigh_1.R", "Thigh_2.L", "Thigh_2.R",
        "Breast.L", "Breast.R",
        "Eye.L", "Eye.R",
    }

def process_bone_rolls(armature_obj):
    if armature_obj.type != 'ARMATURE':
        return
        
    bpy.context.view_layer.objects.active = armature_obj
    bpy.ops.object.mode_set(mode='EDIT')
    
    edit_bones = armature_obj.data.edit_bones
    
    rename_map_values = get_rename_map_values()
    fingers = flip_these()
    
    for bone in edit_bones:
        if bone.name in flip_these():
            # 1. Flip 180 degrees
            bone.roll += math.pi
        elif bone.name in rename_map_values:
            # 2. Ensure they are perfectly mirrored (excludes spine bones due to elif)
            if bone.name.endswith(".L"):
                r_name = bone.name[:-2] + ".R"
                if r_name in edit_bones:
                    edit_bones[r_name].roll = -bone.roll
            elif bone.name.endswith(".R"):
                l_name = bone.name[:-2] + ".L"
                if l_name in edit_bones:
                    bone.roll = -edit_bones[l_name].roll
            
    # 3. Lastly, round to nearest multiple of 180 if within epsilon
    epsilon = 0.01
    for bone in edit_bones:
        multiple = round(bone.roll / math.pi)
        if abs(bone.roll - (multiple * math.pi)) < epsilon:
            bone.roll = multiple * math.pi

    bpy.ops.object.mode_set(mode='OBJECT')
    print(f"Processed bone rolls for '{armature_obj.name}'.")

def main():
    selected_objects = bpy.context.selected_objects
    armatures = [obj for obj in selected_objects if obj.type == 'ARMATURE']
    
    if not armatures:
        print("No armatures selected.")
        return
        
    for arm in armatures:
        process_bone_rolls(arm)
        
if __name__ == "__main__":
    main()
