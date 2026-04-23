import bpy

def duplicate_and_rename_bones(find_str="SubstringA", replace_str="SubstringB"):
    obj = bpy.context.active_object
    
    if not obj or obj.type != 'ARMATURE':
        self.report({'WARNING'}, "Active object is not an armature.")
        return
        
    if bpy.context.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')
        
    # Get currently selected bones
    selected_bones = bpy.context.selected_bones
    if not selected_bones:
        print("No bones selected.")
        return
        
    # Duplicate selected bones
    bpy.ops.armature.duplicate()
    
    # The duplicated bones are automatically selected
    new_selected = bpy.context.selected_bones
    
    for bone in new_selected:
        # Blender automatically adds a numerical suffix (e.g., .001) during duplication.
        # We replace the target substring.
        new_name = bone.name.replace(find_str, replace_str)
        
        # Attempt to strip the auto-generated suffix if it exists,
        # otherwise Blender will resolve conflicts on its own.
        if new_name.endswith(".001"):
            new_name = new_name[:-4]
            
        bone.name = new_name
        
if __name__ == "__main__":
    duplicate_and_rename_bones()
