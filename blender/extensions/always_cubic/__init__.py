import bpy
from bpy.app.handlers import persistent

owner = object()

def enforce_cubic_interpolation(*args):
    # Gather potential data block collections containing node trees
    data_collections = (bpy.data.materials, bpy.data.node_groups, bpy.data.scenes)
    
    for collection in data_collections:
        for block in collection:
            # Fallback to the block itself if it is a NodeTree (like in node_groups)
            tree = getattr(block, "node_tree", block) 
            
            if not isinstance(tree, bpy.types.NodeTree):
                continue
                
            for node in tree.nodes:
                # Target nodes with an interpolation setting that haven't been processed yet
                if hasattr(node, "interpolation") and node.get("auto_cubic_init") is None:
                    try:
                        node.interpolation = 'Cubic'
                    except TypeError:
                        pass # Attribute is read-only or not an enum
                    
                    # Store a custom property so we know we handled this node
                    node["auto_cubic_init"] = True

@persistent
def load_post_handler(dummy):
    # Re-register message bus because subscriptions are cleared on file load
    bpy.msgbus.clear_by_owner(owner)
    try:
        bpy.msgbus.subscribe_rna(
            key=(bpy.types.NodeTree, "nodes"),
            owner=owner,
            args=(),
            notify=enforce_cubic_interpolation,
        )
    except ValueError:
        pass # Handle cases where NodeTree.nodes subscription isn't supported gracefully

def register():
    load_post_handler(None) # Call manually to hook up immediately 
    if load_post_handler not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(load_post_handler)

def unregister():
    bpy.msgbus.clear_by_owner(owner)
    if load_post_handler in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(load_post_handler)
