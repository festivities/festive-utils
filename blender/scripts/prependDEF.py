import bpy

def prepend_def_to_vertex_groups():
    selected_meshes = [obj for obj in bpy.context.selected_objects if obj.type == 'MESH']
    
    if not selected_meshes:
        print("Please select at least one mesh object.")
        return
        
    for obj in selected_meshes:
        for vg in obj.vertex_groups:
            if not vg.name.startswith("DEF-"):
                vg.name = f"DEF-{vg.name}"
            
if __name__ == "__main__":
    prepend_def_to_vertex_groups()
