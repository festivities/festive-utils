import bpy

def copy_light_linking():
    active_obj = bpy.context.active_object
    if not active_obj:
        print("No active object selected.")
        return
        
    if not hasattr(active_obj, "light_linking"):
        print("Active object does not support light linking.")
        return
        
    receiver_collection = active_obj.light_linking.receiver_collection
    
    count = 0
    for obj in bpy.context.selected_objects:
        if obj != active_obj and hasattr(obj, "light_linking"):
            obj.light_linking.receiver_collection = receiver_collection
            count += 1
            
    print(f"Copied light linking to {count} object(s).")

if __name__ == "__main__":
    copy_light_linking()

