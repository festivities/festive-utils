import bpy

def process_armature():
    obj = bpy.context.active_object
    if not obj or obj.type != 'ARMATURE':
        print("Please select an armature object.")
        return

    armature = obj.data

    bpy.ops.object.mode_set(mode='EDIT')
    
    # 1. Create pairs of thigh bones residing in Thigh_1.X and Thigh_2.X
    for side in ['L', 'R']:
        t1_name = f"Thigh_1.{side}"
        t2_name = f"Thigh_2.{side}"
        
        t1 = armature.edit_bones.get(t1_name)
        t2 = armature.edit_bones.get(t2_name)
        
        if t1 and t2:
            thigh_name = f"Thigh.{side}"
            if thigh_name not in armature.edit_bones:
                thigh = armature.edit_bones.new(thigh_name)
                thigh.head = t1.head
                thigh.tail = t2.tail
                thigh.roll = t1.roll
                if t1.parent:
                    thigh.parent = t1.parent
                
                # Reparent children of the original thigh bones to the new thigh
                for b in armature.edit_bones:
                    if b.parent in (t1, t2) and b not in (t1, t2):
                        b.parent = thigh

    # 2. Delete the specified bones
    bones_to_delete = []
    for side in ['L', 'R']:
        bones_to_delete.extend([
            f"Thigh_1.{side}",
            f"Thigh_2.{side}",
            f"UpperArm_1.{side}",
            f"UpperArm_2.{side}",
            f"Forearm_1.{side}",
            f"Forearm_2.{side}",
            f"Knee_1.{side}",
            f"Bip001 {side} ForeTwist OLD"
        ])

    for b_name in bones_to_delete:
        b = armature.edit_bones.get(b_name)
        if b:
            armature.edit_bones.remove(b)

    # Note: Vertex groups are NOT deleted when an edit bone is removed via python.
    # They reside on the mesh object data, so deleting the bone leaves the vertex group intact.

    # 3. Process the vertex groups for parented meshes
    bpy.ops.object.mode_set(mode='OBJECT')
    
    meshes = [o for o in bpy.data.objects if o.type == 'MESH' and (o.parent == obj or any(mod.type == 'ARMATURE' and mod.object == obj for mod in o.modifiers))]
    
    for mesh_obj in meshes:
        for side in ['L', 'R']:
            old_vg_name = f"Bip001 {side} ForeTwist OLD"
            new_vg_name = f"Forearm_1.{side}"
            
            old_vg = mesh_obj.vertex_groups.get(old_vg_name)
            if old_vg:
                new_vg = mesh_obj.vertex_groups.get(new_vg_name)
                if not new_vg:
                    new_vg = mesh_obj.vertex_groups.new(name=new_vg_name)
                
                old_idx = old_vg.index
                
                # Join weights onto the new vertex group
                for v in mesh_obj.data.vertices:
                    for g in v.groups:
                        if g.group == old_idx:
                            new_vg.add([v.index], g.weight, 'ADD')
                            break

    # 4. Parent Kneecap.X to Knee.X and Elbow.X to Forearm.X
    bpy.ops.object.mode_set(mode='EDIT')
    for side in ['L', 'R']:
        kneecap = armature.edit_bones.get(f"Kneecap.{side}")
        knee = armature.edit_bones.get(f"Knee.{side}")
        if kneecap and knee:
            kneecap.parent = knee
            
        elbow = armature.edit_bones.get(f"Elbow.{side}")
        forearm = armature.edit_bones.get(f"Forearm.{side}")
        if elbow and forearm:
            elbow.parent = forearm

    # 5. Connect bone chains
    chains = [
        ["Hips", "Spine0", "Spine1", "Chest", "Neck", "Head"]
    ]
    
    sided_chains = [
        ["Thigh.X", "Knee.X", "Foot.X", "Toes.X"],
        ["Shoulder.X", "UpperArm.X", "Elbow.X", "Forearm.X", "Hand.X"],
        ["Finger_Thumb1.X", "Finger_Thumb2.X", "Finger_Thumb3.X"],
        ["Finger_Index1.X", "Finger_Index2.X", "Finger_Index3.X"],
        ["Finger_Middle1.X", "Finger_Middle2.X", "Finger_Middle3.X"],
        ["Finger_Ring1.X", "Finger_Ring2.X", "Finger_Ring3.X"],
        ["Finger_Pinky1.X", "Finger_Pinky2.X", "Finger_Pinky3.X"]
    ]

    for side in ['L', 'R']:
        for chain in sided_chains:
            chains.append([name.replace('X', side) for name in chain])

    for chain in chains:
        for i in range(len(chain) - 1):
            parent_name = chain[i]
            child_name = chain[i+1]
            
            parent_bone = armature.edit_bones.get(parent_name)
            child_bone = armature.edit_bones.get(child_name)
            
            if parent_bone and child_bone:
                child_bone.parent = parent_bone
                parent_bone.tail = child_bone.head
                child_bone.use_connect = True

    # 6. Create HeelPivot bones
    for side in ['L', 'R']:
        foot = armature.edit_bones.get(f"Foot.{side}")
        toes = armature.edit_bones.get(f"Toes.{side}")
        
        if foot and toes:
            heel_name = f"HeelPivot.{side}"
            heel = armature.edit_bones.get(heel_name)
            if not heel:
                heel = armature.edit_bones.new(heel_name)
            
            # Position below Foot.X, aligned with Toes.X's tail Z
            heel.head = (foot.head.x, foot.head.y, toes.tail.z)
            
            # Tails facing outwards
            outward_sign = 1 if foot.head.x > 0 else -1
            # Give it a reasonable length
            length = foot.length * 0.5 if foot.length > 0 else 0.1
            heel.tail = (heel.head.x + outward_sign * length, heel.head.y, heel.head.z)
            
            heel.roll = 0.0
            heel.parent = foot
            heel.use_connect = False

    # 7. Create properties bone
    hips = armature.edit_bones.get("Hips")
    head_bone = armature.edit_bones.get("Head")
    if hips and head_bone:
        prop_bone = armature.edit_bones.get("Properties")
        if not prop_bone:
            prop_bone = armature.edit_bones.new("Properties")
        
        prop_bone.head = (hips.tail.x, hips.tail.y, head_bone.tail.z + 0.4)
        prop_bone.tail = (prop_bone.head.x, prop_bone.head.y, prop_bone.head.z + 0.15)
        prop_bone.roll = 0.0
        prop_bone.parent = head_bone
        prop_bone.use_connect = False

    # 8. Set up root bone
    root_bone = armature.edit_bones.get("Root")
    if not root_bone:
        root_bone = armature.edit_bones.new("Root")
    
    root_bone.head = (0.0, 0.0, 0.0)
    root_bone.tail = (0.0, 1.0, 0.0)
    root_bone.roll = 0.0

    bpy.ops.object.mode_set(mode='OBJECT')

    def srgb_to_linear(c):
        if c <= 0.04045:
            return c / 12.92
        else:
            return ((c + 0.055) / 1.055) ** 2.4

    def hex_to_rgb(h):
        h = h.lstrip('#')
        return tuple(srgb_to_linear(int(h[i:i+2], 16) / 255.0) for i in (0, 2, 4))

    # 9. Assign all bones to "Rigging" collection and set BBone width
    rigging_coll = armature.collections.get("Rigging")
    if not rigging_coll:
        rigging_coll = armature.collections.new("Rigging")
        
    for bone in armature.bones:
        rigging_coll.assign(bone)
        bone.bbone_x = 0.001
        bone.bbone_z = 0.001

    # 10. Set colors for Root and Properties bones
    for b_name, normal_hex in [("Root", "#B078AD"), ("Properties", "#00FF97")]:
        b = armature.bones.get(b_name)
        if b:
            b.color.palette = 'CUSTOM'
            b.color.custom.normal = hex_to_rgb(normal_hex)
            b.color.custom.select = hex_to_rgb("#98E5FF")
            b.color.custom.active = hex_to_rgb("#C4FFFF")
            
        pb = obj.pose.bones.get(b_name)
        if pb:
            pb.color.palette = 'CUSTOM'
            pb.color.custom.normal = hex_to_rgb(normal_hex)
            pb.color.custom.select = hex_to_rgb("#98E5FF")
            pb.color.custom.active = hex_to_rgb("#C4FFFF")

    # 11. Turn all bones into B-Bones
    armature.display_type = 'BBONE'

    print("Process complete.")

if __name__ == "__main__":
    process_armature()
