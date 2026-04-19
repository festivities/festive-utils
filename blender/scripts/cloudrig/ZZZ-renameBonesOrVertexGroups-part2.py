import bpy

# =========================================================================
# CONFIGURATION
# Define the mapping from old names to new names
# RENAME_MAP = { "OldName": "NewName" }
# =========================================================================
RENAME_MAP = {
    "Bip001 Pelvis": "Hips",
    "Bip001 Spine": "Spine0",
    "Bip001 Spine1": "Spine1",
    "Bip001 Spine2": "Chest",
    "Bip001 Neck": "Neck",
    "Bip001 Head": "Head",

    "Bip001 L Clavicle": "Shoulder.L",
    "Bip001 R Clavicle": "Shoulder.R",
    "Bip001 L UpperArm": "UpperArm.L",
    "Bip001 R UpperArm": "UpperArm.R",
    "Bip001 L Forearm": "Forearm.L",
    "Bip001 R Forearm": "Forearm.R",
    "Bip001 L Hand": "Hand.L",
    "Bip001 R Hand": "Hand.R",

    "Bip001_L_UpArmTwist01": "UpperArm_1.L",
    "Bip001_R_UpArmTwist01": "UpperArm_1.R",
    "Bip001_L_UpArmTwist02": "UpperArm_2.L",
    "Bip001_R_UpArmTwist02": "UpperArm_2.R",
    "Bip001 L Thigh_Twis": "Thigh_1.L",
    "Bip001 R Thigh_Twis": "Thigh_1.R",
    "Bip001 L Thigh": "Thigh_2.L",
    "Bip001 R Thigh": "Thigh_2.R",
    "Bip001 L Calf Adv": "Knee_1.L",
    "Bip001 R Calf Adv": "Knee_1.R",

    "Bip001 L Finger0": "Finger_Thumb1.L",
    "Bip001 L Finger01": "Finger_Thumb2.L",
    "Bip001 L Finger02": "Finger_Thumb3.L",
    "Bip001 R Finger0": "Finger_Thumb1.R",
    "Bip001 R Finger01": "Finger_Thumb2.R",
    "Bip001 R Finger02": "Finger_Thumb3.R",
    "Bip001 L Finger1": "Finger_Index1.L",
    "Bip001 L Finger11": "Finger_Index2.L",
    "Bip001 L Finger12": "Finger_Index3.L",
    "Bip001 R Finger1": "Finger_Index1.R",
    "Bip001 R Finger11": "Finger_Index2.R",
    "Bip001 R Finger12": "Finger_Index3.R",
    "Bip001 L Finger2": "Finger_Middle1.L",
    "Bip001 L Finger21": "Finger_Middle2.L",
    "Bip001 L Finger22": "Finger_Middle3.L",
    "Bip001 R Finger2": "Finger_Middle1.R",
    "Bip001 R Finger21": "Finger_Middle2.R",
    "Bip001 R Finger22": "Finger_Middle3.R",
    "Bip001 L Finger3": "Finger_Ring1.L",
    "Bip001 L Finger31": "Finger_Ring2.L",
    "Bip001 L Finger32": "Finger_Ring3.L",
    "Bip001 R Finger3": "Finger_Ring1.R",
    "Bip001 R Finger31": "Finger_Ring2.R",
    "Bip001 R Finger32": "Finger_Ring3.R",
    "Bip001 L Finger4": "Finger_Pinky1.L",
    "Bip001 L Finger41": "Finger_Pinky2.L",
    "Bip001 L Finger42": "Finger_Pinky3.L",
    "Bip001 R Finger4": "Finger_Pinky1.R",
    "Bip001 R Finger41": "Finger_Pinky2.R",
    "Bip001 R Finger42": "Finger_Pinky3.R",

    "Bip001 L Thigh": "Thigh.L",
    "Bip001 R Thigh": "Thigh.R",
    "Bip001 L Calf": "Knee.L",
    "Bip001 R Calf": "Knee.R",
    "Bip001 L Foot": "Foot.L",
    "Bip001 R Foot": "Foot.R",
    "Bip001 L Toe0": "Toes.L",
    "Bip001 R Toe0": "Toes.R",
}

def rename_armature_bones(armature_obj, base_map):
    """Renames bones in the given armature based on the base_map."""
    if armature_obj.type != 'ARMATURE':
        return
        
    is_edit_mode = (armature_obj.mode == 'EDIT')
    renamed_count = 0
    
    # Generate dynamic map for this armature
    data = armature_obj.data
    def exists(name):
        if is_edit_mode:
            return name in data.edit_bones
        else:
            return name in data.bones

    local_map = base_map.copy()
    for side in ['L', 'R']:
        twist_name = f"Bip001_{side}_ForeTwist"
        adv_name = f"Bip001 {side} Forearm Adv"
        has_twist = exists(twist_name)
        has_adv = exists(adv_name)
        
        if has_twist and has_adv:
            local_map[adv_name] = f"Forearm_1.{side}"
            local_map[twist_name] = f"Forearm_2.{side}"
        elif has_twist:
            local_map[twist_name] = f"Forearm_1.{side}"
            
    # Use edit_bones if we're in Edit Mode, otherwise use bones.
    if is_edit_mode:
        for old_name, new_name in local_map.items():
            bone = data.edit_bones.get(old_name)
            if bone:
                bone.name = new_name
                renamed_count += 1
    else:
        for old_name, new_name in local_map.items():
            bone = data.bones.get(old_name)
            if bone:
                bone.name = new_name
                renamed_count += 1
                
    if renamed_count > 0:
        print(f"Renamed {renamed_count} bones in '{armature_obj.name}'.")

def rename_mesh_vertex_groups(mesh_obj, base_map):
    """Renames vertex groups in the given mesh based on the base_map."""
    if mesh_obj.type != 'MESH':
        return
    
    renamed_count = 0
    
    local_map = base_map.copy()
    for side in ['L', 'R']:
        twist_name = f"Bip001_{side}_ForeTwist"
        adv_name = f"Bip001 {side} Forearm Adv"
        has_twist = twist_name in mesh_obj.vertex_groups
        has_adv = adv_name in mesh_obj.vertex_groups
        
        if has_twist and has_adv:
            local_map[adv_name] = f"Forearm_1.{side}"
            local_map[twist_name] = f"Forearm_2.{side}"
        elif has_twist:
            local_map[twist_name] = f"Forearm_1.{side}"
            
    for old_name, new_name in local_map.items():
        vg = mesh_obj.vertex_groups.get(old_name)
        if vg:
            vg.name = new_name
            renamed_count += 1
            
    if renamed_count > 0:
        print(f"Renamed {renamed_count} vertex groups in '{mesh_obj.name}'.")

def get_armatures_from_mesh(mesh_obj):
    """Find armatures that this mesh is bound to (via parent or modifier)."""
    armatures = set()
    if mesh_obj.parent and mesh_obj.parent.type == 'ARMATURE':
        armatures.add(mesh_obj.parent)
    
    for mod in mesh_obj.modifiers:
        if mod.type == 'ARMATURE' and mod.object and mod.object.type == 'ARMATURE':
            armatures.add(mod.object)
            
    return armatures

def get_meshes_for_armature(armature_obj):
    """Find all meshes in the file bound to this armature."""
    meshes = set()
    for obj in bpy.data.objects:
        if obj.type == 'MESH':
            if obj.parent == armature_obj:
                meshes.add(obj)
            else:
                for mod in obj.modifiers:
                    if mod.type == 'ARMATURE' and mod.object == armature_obj:
                        meshes.add(obj)
                        break # No need to check other modifiers on this obj
    return meshes

def main():
    if not RENAME_MAP:
        print("RENAME_MAP is empty. Nothing to rename.")
        return

    processed_armatures = set()
    processed_meshes = set()
    
    selected_objects = bpy.context.selected_objects
    
    armatures = [obj for obj in selected_objects if obj.type == 'ARMATURE']
    meshes = [obj for obj in selected_objects if obj.type == 'MESH']
            
    # 1. Process selected armatures:
    for arm in armatures:
        if arm in processed_armatures:
            continue
            
        rename_armature_bones(arm, RENAME_MAP)
        processed_armatures.add(arm)
        
        # Find all meshes bound to this armature and rename their vertex groups
        linked_meshes = get_meshes_for_armature(arm)
        for mesh in linked_meshes:
            if mesh not in processed_meshes:
                rename_mesh_vertex_groups(mesh, RENAME_MAP)
                processed_meshes.add(mesh)
                
    # 2. Process selected meshes:
    for mesh in meshes:
        if mesh not in processed_meshes:
            rename_mesh_vertex_groups(mesh, RENAME_MAP)
            processed_meshes.add(mesh)
            
        # Find all armatures this mesh is bound to and rename their bones
        linked_armatures = get_armatures_from_mesh(mesh)
        for arm in linked_armatures:
            if arm not in processed_armatures:
                rename_armature_bones(arm, RENAME_MAP)
                processed_armatures.add(arm)
                
                # Keep everything consistent by renaming vertex groups of OTHER meshes
                # bound to this newly discovered armature.
                other_meshes = get_meshes_for_armature(arm)
                for other_mesh in other_meshes:
                    if other_mesh not in processed_meshes:
                        rename_mesh_vertex_groups(other_mesh, RENAME_MAP)
                        processed_meshes.add(other_mesh)
                        
    print("Renaming operations complete.")

if __name__ == "__main__":
    main()
