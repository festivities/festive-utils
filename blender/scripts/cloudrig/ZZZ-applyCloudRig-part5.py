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
        
        comp.params.parent_switching = True
        comp.params.base.base_name = "Leg"
        comp.params.chain.segments = 2
        comp.params.fk_chain.hinge = True
        comp.params.ik_chain.use_pole = True
        comp.params.ik_chain.world_align = True
        comp.params.limb.limit_elbow_axes = True
        comp.params.leg.use_foot_roll = True
        comp.params.default_stretch = 1
        comp.params.shape_size = 0.2
        
        # Dynamically set the correct side for heel_bone, assuming the user's "HeelPivot.L" implies symmetry
        heel_bone_name = f"HeelPivot.{side}"
        comp.params.leg.heel_bone = heel_bone_name
        
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
            
        comp.params.base.base_name = "Spine"
        comp.params.fk_chain.hinge = False
        comp.params.spine_toon.world_align = True
        comp.params.shape_size = 0.3
        
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
            
        comp.params.chain.segments = 1
        comp.params.chain.tip_control = False
        comp.params.fk_chain.root = True
        comp.params.fk_chain.hinge = True
        comp.params.chain.bbone_density = 32
        comp.params.chain.sharp = True
        comp.params.chain.shape_key_helpers = True
        comp.params.shape_size = 0.4
        
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
            
        comp.params.chain.segments = 1
        comp.params.chain.tip_control = True
        comp.params.fk_chain.root = True
        comp.params.fk_chain.hinge = True
        comp.params.shape_size = 0.2
        
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
            
        comp.params.chain.tip_control = True
        comp.params.chain.sharp = True
        comp.params.shape_size = 0.3
        
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
        
        comp.params.parent_switching = True
        comp.params.base.base_name = "Arm"
        comp.params.chain.segments = 2
        comp.params.chain.tip_control = True
        comp.params.fk_chain.hinge = True
        comp.params.ik_chain.use_pole = True
        comp.params.limb.limit_elbow_axes = True
        comp.params.shape_size = 0.2
        comp.params.default_fkik = 0
        comp.params.default_stretch = 1
        
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
            
        comp.params.chain.segments = 1
        comp.params.chain.tip_control = True
        comp.params.fk_chain.root = True
        comp.params.fk_chain.hinge = False
        comp.params.fk_chain.create_curl_control = True
        comp.params.fk_chain.rot_mode = 'PROPAGATE'
        comp.params.chain.sharp = True
        comp.params.shape_size = 0.4
        
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
            
        comp.params.aim.group = "Eyes"
        comp.params.aim.deform = True
        comp.params.aim.root = True
        
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
            
        comp.params.base.base_name = "Breast"
        comp.params.chain.tip_control = True
        comp.params.fk_chain.hinge = False
        comp.params.shape_size = 0.3
        
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
