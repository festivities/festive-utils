import bpy

def process_armature():
    obj = bpy.context.active_object
    if not obj or obj.type != 'ARMATURE':
        print("Please select an armature object.")
        return

    # Make the selected armature a CloudRig
    obj.cloudrig.enabled = True
    obj.cloudrig.generator.ensure_root = "Root"
    obj.cloudrig.generator.properties_bone = "Root"
    
    # Need to be in pose mode to interact with rig components
    bpy.ops.object.mode_set(mode='POSE')
    
    bones_to_process = ['Thigh.L', 'Thigh.R']
    
    for bone_name in bones_to_process:
        pbone = obj.pose.bones.get(bone_name)
        if not pbone:
            print(f"Bone {bone_name} not found.")
            continue
            
        side = bone_name.split('.')[-1]
            
        comp = pbone.cloudrig_component
        comp.component_type = "Limb: Biped Leg"
        
        # Ensure default bone sets are populated after changing component type
        if hasattr(comp, 'update_ui_bone_sets'):
            comp.update_ui_bone_sets()
        
        # Helper to set parameter regardless of which subgroup it's under
        def set_param(comp, param_name, value):
            for group_name in dir(comp.params):
                if group_name.startswith('__'): continue
                try:
                    group = getattr(comp.params, group_name)
                    if hasattr(group, param_name):
                        setattr(group, param_name, value)
                        return
                except Exception:
                    pass
            print(f"Warning: Param {param_name} not found for {bone_name}")
            
        set_param(comp, 'base_name', "Leg")
        set_param(comp, 'segments', 2)
        set_param(comp, 'hinge', True)
        set_param(comp, 'use_pole', True)
        set_param(comp, 'world_align', True)
        set_param(comp, 'limit_elbow_axes', True)
        set_param(comp, 'use_foot_roll', True)
        
        # Dynamically set the correct side for heel_bone, assuming the user's "HeelPivot.L" implies symmetry
        heel_bone_name = f"HeelPivot.{side}"
        set_param(comp, 'heel_bone', heel_bone_name)
        
        bone_set_mapping = {
            "FK Controls": "Legs FK",
            "FK Controls Extra": "Legs Extra",
            "Foot Reverse IK Controls": "Legs Extra",
            "IK Child Controls": "Legs Extra",
            "IK Controls": "Legs IK",
            "IK Controls Secondary": "Legs Extra",
            "Stretch Controls": "Legs Tweak"
        }
        
        for prop_name in dir(comp.params.bone_sets):
            if prop_name.startswith('__') or prop_name in ['name', 'rna_type']: 
                continue
            try:
                bone_set = getattr(comp.params.bone_sets, prop_name)
                if hasattr(bone_set, 'ui_name') and bone_set.ui_name in bone_set_mapping:
                    target_coll = bone_set_mapping[bone_set.ui_name]
                    if len(bone_set.collections) > 0:
                        bone_set.collections[0].name = target_coll
                    else:
                        bone_set.collections.add().name = target_coll
            except AttributeError:
                pass

    hips_pbone = obj.pose.bones.get("Hips")
    if hips_pbone:
        comp = hips_pbone.cloudrig_component
        comp.component_type = "Spine: Cartoon"
        
        if hasattr(comp, 'update_ui_bone_sets'):
            comp.update_ui_bone_sets()
            
        def set_param_hips(comp, param_name, value):
            for group_name in dir(comp.params):
                if group_name.startswith('__'): continue
                try:
                    group = getattr(comp.params, group_name)
                    if hasattr(group, param_name):
                        setattr(group, param_name, value)
                        return
                except Exception:
                    pass
            print(f"Warning: Param {param_name} not found for Hips")
            
        set_param_hips(comp, 'base_name', "Spine")
        set_param_hips(comp, 'hinge', False)
        set_param_hips(comp, 'world_align', True)
        
        spine_bone_set_mapping = {
            "FK Controls": "Spine FK",
            "FK Controls Extra": "Spine Extra",
            "Toon Spine IK": "Spine IK",
            "Toon Spine IK Secondary": "Spine Extra",
            "Stretch Controls": "Spine Tweak"
        }
        
        for prop_name in dir(comp.params.bone_sets):
            if prop_name.startswith('__') or prop_name in ['name', 'rna_type']: 
                continue
            try:
                bone_set = getattr(comp.params.bone_sets, prop_name)
                if hasattr(bone_set, 'ui_name') and bone_set.ui_name in spine_bone_set_mapping:
                    target_coll = spine_bone_set_mapping[bone_set.ui_name]
                    if len(bone_set.collections) > 0:
                        bone_set.collections[0].name = target_coll
                    else:
                        bone_set.collections.add().name = target_coll
            except AttributeError:
                pass

    neck_pbone = obj.pose.bones.get("Neck")
    if neck_pbone:
        comp = neck_pbone.cloudrig_component
        comp.component_type = "Chain: FK"
        
        if hasattr(comp, 'update_ui_bone_sets'):
            comp.update_ui_bone_sets()
            
        def set_param_neck(comp, param_name, value):
            for group_name in dir(comp.params):
                if group_name.startswith('__'): continue
                try:
                    group = getattr(comp.params, group_name)
                    if hasattr(group, param_name):
                        setattr(group, param_name, value)
                        return
                except Exception:
                    pass
            print(f"Warning: Param {param_name} not found for Neck")
            
        set_param_neck(comp, 'segments', 1)
        set_param_neck(comp, 'root', True)
        set_param_neck(comp, 'hinge', True)
        set_param_neck(comp, 'bbone_density', 32)
        set_param_neck(comp, 'sharp', True)
        set_param_neck(comp, 'shape_key_helpers', True)
        
        neck_bone_set_mapping = {
            "FK Controls": "Spine FK",
            "FK Controls Extra": "Spine Extra",
            "Stretch Controls": "Spine Tweak"
        }
        
        for prop_name in dir(comp.params.bone_sets):
            if prop_name.startswith('__') or prop_name in ['name', 'rna_type']: 
                continue
            try:
                bone_set = getattr(comp.params.bone_sets, prop_name)
                if hasattr(bone_set, 'ui_name') and bone_set.ui_name in neck_bone_set_mapping:
                    target_coll = neck_bone_set_mapping[bone_set.ui_name]
                    if len(bone_set.collections) > 0:
                        bone_set.collections[0].name = target_coll
                    else:
                        bone_set.collections.add().name = target_coll
            except AttributeError:
                pass

    head_pbone = obj.pose.bones.get("Head")
    if head_pbone:
        comp = head_pbone.cloudrig_component
        comp.component_type = "Chain: FK"
        
        if hasattr(comp, 'update_ui_bone_sets'):
            comp.update_ui_bone_sets()
            
        def set_param_head(comp, param_name, value):
            for group_name in dir(comp.params):
                if group_name.startswith('__'): continue
                try:
                    group = getattr(comp.params, group_name)
                    if hasattr(group, param_name):
                        setattr(group, param_name, value)
                        return
                except Exception:
                    pass
            print(f"Warning: Param {param_name} not found for Head")
            
        set_param_head(comp, 'segments', 1)
        set_param_head(comp, 'tip_control', True)
        set_param_head(comp, 'root', True)
        set_param_head(comp, 'hinge', True)
        
        head_bone_set_mapping = {
            "FK Controls": "Spine FK",
            "FK Controls Extra": "Spine Extra",
            "Stretch Controls": "Spine Tweak"
        }
        
        for prop_name in dir(comp.params.bone_sets):
            if prop_name.startswith('__') or prop_name in ['name', 'rna_type']: 
                continue
            try:
                bone_set = getattr(comp.params.bone_sets, prop_name)
                if hasattr(bone_set, 'ui_name') and bone_set.ui_name in head_bone_set_mapping:
                    target_coll = head_bone_set_mapping[bone_set.ui_name]
                    if len(bone_set.collections) > 0:
                        bone_set.collections[0].name = target_coll
                    else:
                        bone_set.collections.add().name = target_coll
            except AttributeError:
                pass

    shoulder_bones = ['Shoulder.L', 'Shoulder.R']
    for bone_name in shoulder_bones:
        pbone = obj.pose.bones.get(bone_name)
        if not pbone:
            print(f"Bone {bone_name} not found.")
            continue
            
        comp = pbone.cloudrig_component
        comp.component_type = "Shoulder Bone"
        
        if hasattr(comp, 'update_ui_bone_sets'):
            comp.update_ui_bone_sets()
            
        def set_param_shoulder(comp, param_name, value):
            for group_name in dir(comp.params):
                if group_name.startswith('__'): continue
                try:
                    group = getattr(comp.params, group_name)
                    if hasattr(group, param_name):
                        setattr(group, param_name, value)
                        return
                except Exception:
                    pass
            print(f"Warning: Param {param_name} not found for {bone_name}")
            
        set_param_shoulder(comp, 'tip_control', True)
        set_param_shoulder(comp, 'sharp', True)
        
        shoulder_bone_set_mapping = {
            "FK Controls": "Arms",
            "Stretch Controls": "Arms Tweak"
        }
        
        for prop_name in dir(comp.params.bone_sets):
            if prop_name.startswith('__') or prop_name in ['name', 'rna_type']: 
                continue
            try:
                bone_set = getattr(comp.params.bone_sets, prop_name)
                if hasattr(bone_set, 'ui_name') and bone_set.ui_name in shoulder_bone_set_mapping:
                    target_coll = shoulder_bone_set_mapping[bone_set.ui_name]
                    if len(bone_set.collections) > 0:
                        bone_set.collections[0].name = target_coll
                    else:
                        bone_set.collections.add().name = target_coll
            except AttributeError:
                pass

    upperarm_bones = ['UpperArm.L', 'UpperArm.R']
    for bone_name in upperarm_bones:
        pbone = obj.pose.bones.get(bone_name)
        if not pbone:
            print(f"Bone {bone_name} not found.")
            continue
            
        comp = pbone.cloudrig_component
        comp.component_type = "Limb: Generic"
        
        if hasattr(comp, 'update_ui_bone_sets'):
            comp.update_ui_bone_sets()
            
        def set_param_upperarm(comp, param_name, value):
            for group_name in dir(comp.params):
                if group_name.startswith('__'): continue
                try:
                    group = getattr(comp.params, group_name)
                    if hasattr(group, param_name):
                        setattr(group, param_name, value)
                        return
                except Exception:
                    pass
            print(f"Warning: Param {param_name} not found for {bone_name}")
            
        set_param_upperarm(comp, 'base_name', "Arm")
        set_param_upperarm(comp, 'segments', 2)
        set_param_upperarm(comp, 'tip_control', True)
        set_param_upperarm(comp, 'hinge', True)
        set_param_upperarm(comp, 'use_pole', True)
        set_param_upperarm(comp, 'limit_elbow_axes', True)
        
        arm_bone_set_mapping = {
            "FK Controls": "Arms FK",
            "FK Controls Extra": "Arms Extra",
            "IK Child Controls": "Arms Extra",
            "IK Controls": "Arms IK",
            "IK Controls Secondary": "Arms Extra",
            "Stretch Controls": "Arms Tweak"
        }
        
        for prop_name in dir(comp.params.bone_sets):
            if prop_name.startswith('__') or prop_name in ['name', 'rna_type']: 
                continue
            try:
                bone_set = getattr(comp.params.bone_sets, prop_name)
                if hasattr(bone_set, 'ui_name') and bone_set.ui_name in arm_bone_set_mapping:
                    target_coll = arm_bone_set_mapping[bone_set.ui_name]
                    if len(bone_set.collections) > 0:
                        bone_set.collections[0].name = target_coll
                    else:
                        bone_set.collections.add().name = target_coll
            except AttributeError:
                pass

    finger_bones = []
    for side in ['L', 'R']:
        for finger in ['Thumb', 'Index', 'Middle', 'Ring', 'Pinky']:
            finger_bones.append(f'Finger_{finger}1.{side}')

    for bone_name in finger_bones:
        pbone = obj.pose.bones.get(bone_name)
        if not pbone:
            print(f"Bone {bone_name} not found.")
            continue
            
        comp = pbone.cloudrig_component
        comp.component_type = "Chain: FK"
        
        if hasattr(comp, 'update_ui_bone_sets'):
            comp.update_ui_bone_sets()
            
        def set_param_finger(comp, param_name, value):
            for group_name in dir(comp.params):
                if group_name.startswith('__'): continue
                try:
                    group = getattr(comp.params, group_name)
                    if hasattr(group, param_name):
                        setattr(group, param_name, value)
                        return
                except Exception:
                    pass
            print(f"Warning: Param {param_name} not found for {bone_name}")
            
        set_param_finger(comp, 'segments', 1)
        set_param_finger(comp, 'tip_control', True)
        set_param_finger(comp, 'root', True)
        set_param_finger(comp, 'hinge', False)
        set_param_finger(comp, 'create_curl_control', True)
        set_param_finger(comp, 'rot_mode', 'PROPAGATE')
        set_param_finger(comp, 'sharp', True)
        
        finger_bone_set_mapping = {
            "FK Controls": "Fingers",
            "FK Controls Extra": "Fingers Extra",
            "FK Curl Control": "Fingers",
            "Stretch Controls": "Fingers Stretch"
        }
        
        for prop_name in dir(comp.params.bone_sets):
            if prop_name.startswith('__') or prop_name in ['name', 'rna_type']: 
                continue
            try:
                bone_set = getattr(comp.params.bone_sets, prop_name)
                if hasattr(bone_set, 'ui_name') and bone_set.ui_name in finger_bone_set_mapping:
                    target_coll = finger_bone_set_mapping[bone_set.ui_name]
                    if len(bone_set.collections) > 0:
                        bone_set.collections[0].name = target_coll
                    else:
                        bone_set.collections.add().name = target_coll
            except AttributeError:
                pass

    eye_bones = ['Eye.L', 'Eye.R']
    for bone_name in eye_bones:
        pbone = obj.pose.bones.get(bone_name)
        if not pbone:
            print(f"Bone {bone_name} not found.")
            continue
            
        comp = pbone.cloudrig_component
        comp.component_type = "Aim"
        
        if hasattr(comp, 'update_ui_bone_sets'):
            comp.update_ui_bone_sets()
            
        def set_param_eye(comp, param_name, value):
            for group_name in dir(comp.params):
                if group_name.startswith('__'): continue
                try:
                    group = getattr(comp.params, group_name)
                    if hasattr(group, param_name):
                        setattr(group, param_name, value)
                        return
                except Exception:
                    pass
            print(f"Warning: Param {param_name} not found for {bone_name}")
            
        set_param_eye(comp, 'group', "Eyes")
        set_param_eye(comp, 'deform', True)
        set_param_eye(comp, 'root', True)
        
        eye_bone_set_mapping = {
            "Aim Group Target Control": "Face Main",
            "Aim Root Control": "Face Secondary",
            "Aim Target Control": "Face Main"
        }
        
        for prop_name in dir(comp.params.bone_sets):
            if prop_name.startswith('__') or prop_name in ['name', 'rna_type']: 
                continue
            try:
                bone_set = getattr(comp.params.bone_sets, prop_name)
                if hasattr(bone_set, 'ui_name') and bone_set.ui_name in eye_bone_set_mapping:
                    target_coll = eye_bone_set_mapping[bone_set.ui_name]
                    if len(bone_set.collections) > 0:
                        bone_set.collections[0].name = target_coll
                    else:
                        bone_set.collections.add().name = target_coll
            except AttributeError:
                pass

    breast_bones = ['Breast.L', 'Breast.R']
    for bone_name in breast_bones:
        pbone = obj.pose.bones.get(bone_name)
        if not pbone:
            print(f"Bone {bone_name} not found.")
            continue
            
        comp = pbone.cloudrig_component
        comp.component_type = "Chain: FK"
        
        if hasattr(comp, 'update_ui_bone_sets'):
            comp.update_ui_bone_sets()
            
        def set_param_breast(comp, param_name, value):
            for group_name in dir(comp.params):
                if group_name.startswith('__'): continue
                try:
                    group = getattr(comp.params, group_name)
                    if hasattr(group, param_name):
                        setattr(group, param_name, value)
                        return
                except Exception:
                    pass
            print(f"Warning: Param {param_name} not found for {bone_name}")
            
        set_param_breast(comp, 'base_name', "Breast")
        set_param_breast(comp, 'tip_control', True)
        set_param_breast(comp, 'hinge', False)
        
        breast_bone_set_mapping = {
            "FK Controls": "Spine",
            "Stretch Controls": "Spine Tweak"
        }
        
        for prop_name in dir(comp.params.bone_sets):
            if prop_name.startswith('__') or prop_name in ['name', 'rna_type']: 
                continue
            try:
                bone_set = getattr(comp.params.bone_sets, prop_name)
                if hasattr(bone_set, 'ui_name') and bone_set.ui_name in breast_bone_set_mapping:
                    target_coll = breast_bone_set_mapping[bone_set.ui_name]
                    if len(bone_set.collections) > 0:
                        bone_set.collections[0].name = target_coll
                    else:
                        bone_set.collections.add().name = target_coll
            except AttributeError:
                pass
                
    bpy.ops.object.mode_set(mode='OBJECT')
    print("CloudRig processing part 5 complete.")

if __name__ == "__main__":
    process_armature()
