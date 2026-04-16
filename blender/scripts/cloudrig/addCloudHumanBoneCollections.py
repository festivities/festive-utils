import bpy

def add_cloud_human_bone_collections():
    obj = bpy.context.active_object
    if not obj or obj.type != 'ARMATURE':
        print("Please select an armature.")
        return
        
    arm = obj.data
    
    def get_or_create(name, parent_name=None):
        coll = arm.collections.get(name)
        if not coll:
            coll = arm.collections.new(name=name)
            
        if parent_name:
            parent_coll = arm.collections.get(parent_name)
            if parent_coll:
                coll.parent = parent_coll
        return coll
        
    get_or_create("IK Controls")
    get_or_create("IK Secondary", "IK Controls")
    
    get_or_create("FK Controls")
    get_or_create("FK Secondary", "FK Controls")
    
    get_or_create("Stretch Controls")
    
    get_or_create("Hair")
    get_or_create("Hair Stretch", "Hair")
    
    get_or_create("Fingers")
    get_or_create("Finger Stretch", "Fingers")
    
    get_or_create("Rigging")
    get_or_create("Deform Bones", "Rigging")
    get_or_create("Original Bones", "Rigging")
    get_or_create("Mechanism Bones", "Rigging")

if __name__ == "__main__":
    add_cloud_human_bone_collections()
