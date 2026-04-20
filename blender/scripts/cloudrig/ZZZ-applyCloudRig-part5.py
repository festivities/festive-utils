import bpy

def process_armature():
    obj = bpy.context.active_object
    if not obj or obj.type != 'ARMATURE':
        print("Please select an armature object.")
        return

    # Make the selected armature a CloudRig
    obj.cloudrig.enabled = True
    
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
        set_param(comp, 'pole_parent_switch', 'FOLLOW')
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
                
    bpy.ops.object.mode_set(mode='OBJECT')
    print("CloudRig processing part 5 complete.")

if __name__ == "__main__":
    process_armature()
