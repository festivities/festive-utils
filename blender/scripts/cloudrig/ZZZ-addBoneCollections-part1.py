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
        
    get_or_create("Spine")
    get_or_create("Spine IK", "Spine")
    get_or_create("Spine FK", "Spine")
    get_or_create("Spine Tweak", "Spine")
    get_or_create("Spine Extra", "Spine")
    
    get_or_create("Arms")
    get_or_create("Arms IK", "Arms")
    get_or_create("Arms FK", "Arms")
    get_or_create("Arms Tweak", "Arms")
    get_or_create("Arms Extra", "Arms")
    
    get_or_create("Legs")
    get_or_create("Legs IK", "Legs")
    get_or_create("Legs FK", "Legs")
    get_or_create("Legs Tweak", "Legs")
    get_or_create("Legs Extra", "Legs")
    
    get_or_create("Hair")
    get_or_create("Hair Stretch", "Hair")
    
    get_or_create("Fingers")
    get_or_create("Finger Stretch", "Fingers")

    get_or_create("Face")
    get_or_create("Face Main", "Face")
    get_or_create("Face Secondary", "Face")

    get_or_create("Physics")
    get_or_create("Physics Stretch", "Physics")
    get_or_create("Physics Extra", "Physics")

    get_or_create("Weapon")
    
    get_or_create("Root")
    
    get_or_create("Rigging")
    get_or_create("Deform Bones", "Rigging")
    get_or_create("Original Bones", "Rigging")
    get_or_create("Mechanism Bones", "Rigging")

if __name__ == "__main__":
    add_cloud_human_bone_collections()
