import bpy


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _is_light_object(obj):
    """Return True if *obj* is a light that can own linking collections."""
    return obj and obj.type == 'LIGHT'


def _get_selected_non_lights(context):
    """Return selected objects that are NOT lights."""
    return [o for o in context.selected_objects if not _is_light_object(o)]


def _ensure_linking_collection(light_obj, link_type):
    """
    Ensure the light has a linking collection for *link_type*
    ('receiver_collection' or 'blocker_collection').
    Creates one if it doesn't exist yet.
    """
    coll = getattr(light_obj.light_linking, link_type)
    if coll is None:
        coll = bpy.data.collections.new(f"{light_obj.name}_{link_type}")
        setattr(light_obj.light_linking, link_type, coll)
    return coll


def _link_item_to_collection(coll, item):
    """
    Link *item* (Object or Collection) into *coll* if not already present.
    Returns True if newly linked.
    """
    if isinstance(item, bpy.types.Collection):
        existing = {c.collection for c in coll.collection_children}
        if item not in existing:
            coll.children.link(item)
            return True
    else:
        existing = {o.object for o in coll.collection_objects}
        if item not in existing:
            coll.objects.link(item)
            return True
    return False


def _set_link_state(coll, item, state):
    """
    Set the light-linking state of *item* inside *coll* to *state*
    ('INCLUDE' or 'EXCLUDE').
    """
    if isinstance(item, bpy.types.Collection):
        for child in coll.collection_children:
            if child.collection == item:
                child.light_linking.link_state = state
                return
    else:
        for obj_entry in coll.collection_objects:
            if obj_entry.object == item:
                obj_entry.light_linking.link_state = state
                return


def _get_collections_for_selected(context):
    """
    Return collections that directly contain at least one selected object.
    """
    selected = set(context.selected_objects)
    return [c for c in bpy.data.collections if set(c.objects) & selected]


def _apply_link_action(lights, items, link_mode, action):
    """
    Core logic shared by all operators.
    *lights*: list of light objects.
    *items*: list of Objects or Collections to process.
    *link_mode*: 'BOTH', 'LIGHT', or 'SHADOW'.
    *action*: 'EXCLUDE' or 'INCLUDE'.
    Returns the number of operations performed.
    """
    do_light  = link_mode in ('BOTH', 'LIGHT')
    do_shadow = link_mode in ('BOTH', 'SHADOW')
    count = 0

    for light in lights:
        for item in items:
            if do_light:
                if action == 'EXCLUDE':
                    coll = _ensure_linking_collection(light, 'receiver_collection')
                    _link_item_to_collection(coll, item)
                    _set_link_state(coll, item, 'EXCLUDE')
                else:
                    coll = getattr(light.light_linking, 'receiver_collection')
                    if coll is not None:
                        _set_link_state(coll, item, 'INCLUDE')
                count += 1

            if do_shadow:
                if action == 'EXCLUDE':
                    coll = _ensure_linking_collection(light, 'blocker_collection')
                    _link_item_to_collection(coll, item)
                    _set_link_state(coll, item, 'EXCLUDE')
                else:
                    coll = getattr(light.light_linking, 'blocker_collection')
                    if coll is not None:
                        _set_link_state(coll, item, 'INCLUDE')
                count += 1
    return count


def _collection_items(self, context):
    """Dynamic enum items listing all collections in the .blend file."""
    return [(c.name, c.name, "") for c in bpy.data.collections]


# ──────────────────────────────────────────────────────────────
# Shared property definitions
# ──────────────────────────────────────────────────────────────

_LINK_MODE_ITEMS = [
    ('BOTH',   "Light + Shadow", "Both light and shadow linking"),
    ('LIGHT',  "Light Only",     "Light linking only"),
    ('SHADOW', "Shadow Only",    "Shadow linking only"),
]

_TARGET_TYPE_ITEMS = [
    ('OBJECTS',     "Objects",     "Act on selected objects individually"),
    ('COLLECTIONS', "Collections", "Act on collections containing selected objects"),
]


# ══════════════════════════════════════════════════════════════
# METHOD 1 — Selection-based  (select lights + objects/collections)
# ══════════════════════════════════════════════════════════════

class LIGHTEXCL_OT_exclude_selection(bpy.types.Operator):
    """Exclude selected objects (or their collections) from the selected lights"""
    bl_idname = "object.light_excluder_exclude"
    bl_label = "Exclude Selection from Lights"
    bl_options = {'REGISTER', 'UNDO'}

    link_mode: bpy.props.EnumProperty(
        name="Linking Mode", items=_LINK_MODE_ITEMS, default='BOTH')
    target_type: bpy.props.EnumProperty(
        name="Target Type", items=_TARGET_TYPE_ITEMS, default='OBJECTS')

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            return False
        sel = context.selected_objects
        return (any(_is_light_object(o) for o in sel)
                and any(not _is_light_object(o) for o in sel))

    def execute(self, context):
        lights = [o for o in context.selected_objects if _is_light_object(o)]
        items = (_get_selected_non_lights(context)
                 if self.target_type == 'OBJECTS'
                 else _get_collections_for_selected(context))
        if not items:
            self.report({'WARNING'}, "No valid targets to exclude")
            return {'CANCELLED'}
        count = _apply_link_action(lights, items, self.link_mode, 'EXCLUDE')
        self.report({'INFO'}, f"Excluded {count} item(s)")
        return {'FINISHED'}


class LIGHTEXCL_OT_include_selection(bpy.types.Operator):
    """Re-include selected objects (or their collections) in the selected lights"""
    bl_idname = "object.light_excluder_include"
    bl_label = "Include Selection in Lights"
    bl_options = {'REGISTER', 'UNDO'}

    link_mode: bpy.props.EnumProperty(
        name="Linking Mode", items=_LINK_MODE_ITEMS, default='BOTH')
    target_type: bpy.props.EnumProperty(
        name="Target Type", items=_TARGET_TYPE_ITEMS, default='OBJECTS')

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            return False
        sel = context.selected_objects
        return (any(_is_light_object(o) for o in sel)
                and any(not _is_light_object(o) for o in sel))

    def execute(self, context):
        lights = [o for o in context.selected_objects if _is_light_object(o)]
        items = (_get_selected_non_lights(context)
                 if self.target_type == 'OBJECTS'
                 else _get_collections_for_selected(context))
        if not items:
            self.report({'WARNING'}, "No valid targets to include")
            return {'CANCELLED'}
        count = _apply_link_action(lights, items, self.link_mode, 'INCLUDE')
        self.report({'INFO'}, f"Included {count} item(s)")
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════
# METHOD 2 — Collection picker  (select lights → pick collection)
# ══════════════════════════════════════════════════════════════

class LIGHTEXCL_OT_exclude_collection(bpy.types.Operator):
    """Exclude a collection (picked from a list) from the selected lights"""
    bl_idname = "object.light_excluder_excl_coll"
    bl_label = "Exclude Collection from Lights"
    bl_options = {'REGISTER', 'UNDO'}

    link_mode: bpy.props.EnumProperty(
        name="Linking Mode", items=_LINK_MODE_ITEMS, default='BOTH')
    target_collection: bpy.props.EnumProperty(
        name="Collection", description="Collection to exclude",
        items=_collection_items)

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            return False
        return any(_is_light_object(o) for o in context.selected_objects)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "target_collection", icon='OUTLINER_COLLECTION')
        layout.prop(self, "link_mode")

    def execute(self, context):
        coll = bpy.data.collections.get(self.target_collection)
        if coll is None:
            self.report({'ERROR'}, f"Collection '{self.target_collection}' not found")
            return {'CANCELLED'}
        lights = [o for o in context.selected_objects if _is_light_object(o)]
        count = _apply_link_action(lights, [coll], self.link_mode, 'EXCLUDE')
        self.report({'INFO'}, f"Excluded collection '{coll.name}' from {len(lights)} light(s)")
        return {'FINISHED'}


class LIGHTEXCL_OT_include_collection(bpy.types.Operator):
    """Re-include a collection (picked from a list) in the selected lights"""
    bl_idname = "object.light_excluder_incl_coll"
    bl_label = "Include Collection in Lights"
    bl_options = {'REGISTER', 'UNDO'}

    link_mode: bpy.props.EnumProperty(
        name="Linking Mode", items=_LINK_MODE_ITEMS, default='BOTH')
    target_collection: bpy.props.EnumProperty(
        name="Collection", description="Collection to re-include",
        items=_collection_items)

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            return False
        return any(_is_light_object(o) for o in context.selected_objects)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=300)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "target_collection", icon='OUTLINER_COLLECTION')
        layout.prop(self, "link_mode")

    def execute(self, context):
        coll = bpy.data.collections.get(self.target_collection)
        if coll is None:
            self.report({'ERROR'}, f"Collection '{self.target_collection}' not found")
            return {'CANCELLED'}
        lights = [o for o in context.selected_objects if _is_light_object(o)]
        count = _apply_link_action(lights, [coll], self.link_mode, 'INCLUDE')
        self.report({'INFO'}, f"Included collection '{coll.name}' in {len(lights)} light(s)")
        return {'FINISHED'}


# ══════════════════════════════════════════════════════════════
# METHOD 3 — Collection-to-Collection
#   (Collection A has lights → exclude/include Collection B)
# ══════════════════════════════════════════════════════════════

def _get_lights_in_collection(coll):
    """Recursively gather all light objects inside *coll* and its children."""
    lights = [o for o in coll.objects if _is_light_object(o)]
    for child in coll.children:
        lights.extend(_get_lights_in_collection(child))
    return lights


class LIGHTEXCL_OT_coll_to_coll_exclude(bpy.types.Operator):
    """All lights in Collection A exclude Collection B"""
    bl_idname = "object.light_excluder_c2c_exclude"
    bl_label = "Collection → Collection Exclude"
    bl_options = {'REGISTER', 'UNDO'}

    link_mode: bpy.props.EnumProperty(
        name="Linking Mode", items=_LINK_MODE_ITEMS, default='BOTH')
    lights_collection: bpy.props.EnumProperty(
        name="Lights Collection",
        description="Collection containing the lights",
        items=_collection_items)
    target_collection: bpy.props.EnumProperty(
        name="Target Collection",
        description="Collection to exclude from those lights",
        items=_collection_items)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and len(bpy.data.collections) >= 2

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "lights_collection", icon='LIGHT')
        layout.prop(self, "target_collection", icon='OUTLINER_COLLECTION')
        layout.separator()
        layout.prop(self, "link_mode")

    def execute(self, context):
        src = bpy.data.collections.get(self.lights_collection)
        tgt = bpy.data.collections.get(self.target_collection)
        if not src:
            self.report({'ERROR'}, f"Lights collection '{self.lights_collection}' not found")
            return {'CANCELLED'}
        if not tgt:
            self.report({'ERROR'}, f"Target collection '{self.target_collection}' not found")
            return {'CANCELLED'}
        if src == tgt:
            self.report({'WARNING'}, "Lights and target collection must be different")
            return {'CANCELLED'}

        lights = _get_lights_in_collection(src)
        if not lights:
            self.report({'WARNING'}, f"No lights found in '{src.name}'")
            return {'CANCELLED'}

        count = _apply_link_action(lights, [tgt], self.link_mode, 'EXCLUDE')
        self.report({'INFO'},
                    f"Excluded '{tgt.name}' from {len(lights)} light(s) in '{src.name}'")
        return {'FINISHED'}


class LIGHTEXCL_OT_coll_to_coll_include(bpy.types.Operator):
    """All lights in Collection A re-include Collection B"""
    bl_idname = "object.light_excluder_c2c_include"
    bl_label = "Collection → Collection Include"
    bl_options = {'REGISTER', 'UNDO'}

    link_mode: bpy.props.EnumProperty(
        name="Linking Mode", items=_LINK_MODE_ITEMS, default='BOTH')
    lights_collection: bpy.props.EnumProperty(
        name="Lights Collection",
        description="Collection containing the lights",
        items=_collection_items)
    target_collection: bpy.props.EnumProperty(
        name="Target Collection",
        description="Collection to re-include in those lights",
        items=_collection_items)

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT' and len(bpy.data.collections) >= 2

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=350)

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "lights_collection", icon='LIGHT')
        layout.prop(self, "target_collection", icon='OUTLINER_COLLECTION')
        layout.separator()
        layout.prop(self, "link_mode")

    def execute(self, context):
        src = bpy.data.collections.get(self.lights_collection)
        tgt = bpy.data.collections.get(self.target_collection)
        if not src:
            self.report({'ERROR'}, f"Lights collection '{self.lights_collection}' not found")
            return {'CANCELLED'}
        if not tgt:
            self.report({'ERROR'}, f"Target collection '{self.target_collection}' not found")
            return {'CANCELLED'}
        if src == tgt:
            self.report({'WARNING'}, "Lights and target collection must be different")
            return {'CANCELLED'}

        lights = _get_lights_in_collection(src)
        if not lights:
            self.report({'WARNING'}, f"No lights found in '{src.name}'")
            return {'CANCELLED'}

        count = _apply_link_action(lights, [tgt], self.link_mode, 'INCLUDE')
        self.report({'INFO'},
                    f"Included '{tgt.name}' in {len(lights)} light(s) in '{src.name}'")
        return {'FINISHED'}


# ──────────────────────────────────────────────────────────────
# UI Panel
# ──────────────────────────────────────────────────────────────

class LIGHTEXCL_PT_panel(bpy.types.Panel):
    """Light Excluder Panel"""
    bl_label = "Light Excluder"
    bl_idname = "LIGHTEXCL_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Light'

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def draw(self, context):
        layout = self.layout

        # ── Selection info ──
        sel = context.selected_objects
        lights = [o for o in sel if _is_light_object(o)]
        non_lights = [o for o in sel if not _is_light_object(o)]

        box = layout.box()
        box.label(text=f"Lights: {len(lights)}  |  Objects: {len(non_lights)}",
                  icon='LIGHT')

        # ──────────────────────────────────────────────────────
        # Method 1 — Selection-based
        # ──────────────────────────────────────────────────────
        header, body = layout.panel("LIGHTEXCL_selection", default_closed=False)
        header.label(text="Selection-Based", icon='RESTRICT_SELECT_OFF')
        if body:
            if not lights:
                body.label(text="Select at least one light", icon='ERROR')
            if not non_lights:
                body.label(text="Also select objects to target", icon='ERROR')

            col = body.column(align=True)
            col.label(text="Exclude Objects:")
            row = col.row(align=True)
            for mode, label in [('BOTH', "Both"), ('LIGHT', "Light"), ('SHADOW', "Shadow")]:
                op = row.operator(LIGHTEXCL_OT_exclude_selection.bl_idname, text=label)
                op.link_mode = mode
                op.target_type = 'OBJECTS'

            col.label(text="Exclude by Collection:")
            row = col.row(align=True)
            for mode, label in [('BOTH', "Both"), ('LIGHT', "Light"), ('SHADOW', "Shadow")]:
                op = row.operator(LIGHTEXCL_OT_exclude_selection.bl_idname, text=label)
                op.link_mode = mode
                op.target_type = 'COLLECTIONS'

            col.separator()
            col.label(text="Re-include Objects:")
            row = col.row(align=True)
            for mode, label in [('BOTH', "Both"), ('LIGHT', "Light"), ('SHADOW', "Shadow")]:
                op = row.operator(LIGHTEXCL_OT_include_selection.bl_idname, text=label)
                op.link_mode = mode
                op.target_type = 'OBJECTS'

            col.label(text="Re-include by Collection:")
            row = col.row(align=True)
            for mode, label in [('BOTH', "Both"), ('LIGHT', "Light"), ('SHADOW', "Shadow")]:
                op = row.operator(LIGHTEXCL_OT_include_selection.bl_idname, text=label)
                op.link_mode = mode
                op.target_type = 'COLLECTIONS'

        # ──────────────────────────────────────────────────────
        # Method 2 — Collection picker (lights selected → pick collection)
        # ──────────────────────────────────────────────────────
        header, body = layout.panel("LIGHTEXCL_coll_picker", default_closed=False)
        header.label(text="Collection Picker", icon='OUTLINER_COLLECTION')
        if body:
            if not lights:
                body.label(text="Select lights first, then pick a collection", icon='INFO')
            col = body.column(align=True)
            col.operator(LIGHTEXCL_OT_exclude_collection.bl_idname,
                         text="Exclude Collection…", icon='REMOVE')
            col.operator(LIGHTEXCL_OT_include_collection.bl_idname,
                         text="Include Collection…", icon='ADD')

        # ──────────────────────────────────────────────────────
        # Method 3 — Collection-to-Collection
        # ──────────────────────────────────────────────────────
        header, body = layout.panel("LIGHTEXCL_c2c", default_closed=False)
        header.label(text="Collection → Collection", icon='LINKED')
        if body:
            body.label(text="Lights in A → target B", icon='INFO')
            col = body.column(align=True)
            col.operator(LIGHTEXCL_OT_coll_to_coll_exclude.bl_idname,
                         text="Exclude B from A…", icon='REMOVE')
            col.operator(LIGHTEXCL_OT_coll_to_coll_include.bl_idname,
                         text="Include B in A…", icon='ADD')


# ──────────────────────────────────────────────────────────────
# Right-click context menu
# ──────────────────────────────────────────────────────────────

def _draw_context_menu(self, context):
    if context.mode != 'OBJECT':
        return
    sel = context.selected_objects
    has_lights = any(_is_light_object(o) for o in sel)
    if not has_lights:
        return

    self.layout.separator()
    self.layout.menu(LIGHTEXCL_MT_context_menu.bl_idname, icon='LIGHT')


class LIGHTEXCL_MT_context_menu(bpy.types.Menu):
    bl_label = "Light Excluder"
    bl_idname = "LIGHTEXCL_MT_context_menu"

    def draw(self, context):
        layout = self.layout
        has_non_lights = any(not _is_light_object(o) for o in context.selected_objects)

        # Selection-based (only if mixed selection)
        if has_non_lights:
            layout.label(text="Selection-Based:", icon='RESTRICT_SELECT_OFF')
            for action, op_id, prefix in [
                ('EXCLUDE', LIGHTEXCL_OT_exclude_selection.bl_idname, "Exclude"),
                ('INCLUDE', LIGHTEXCL_OT_include_selection.bl_idname, "Include"),
            ]:
                for mode, suffix in [('BOTH', "Both"), ('LIGHT', "Light"), ('SHADOW', "Shadow")]:
                    op = layout.operator(op_id, text=f"{prefix} {suffix}")
                    op.link_mode = mode
                    op.target_type = 'OBJECTS'
            layout.separator()

        # Collection picker (always available when lights selected)
        layout.label(text="Collection Picker:", icon='OUTLINER_COLLECTION')
        layout.operator(LIGHTEXCL_OT_exclude_collection.bl_idname,
                        text="Exclude Collection…")
        layout.operator(LIGHTEXCL_OT_include_collection.bl_idname,
                        text="Include Collection…")
        layout.separator()

        # Collection-to-Collection
        layout.label(text="Collection → Collection:", icon='LINKED')
        layout.operator(LIGHTEXCL_OT_coll_to_coll_exclude.bl_idname,
                        text="Exclude B from A…")
        layout.operator(LIGHTEXCL_OT_coll_to_coll_include.bl_idname,
                        text="Include B in A…")


# ──────────────────────────────────────────────────────────────
# Registration
# ──────────────────────────────────────────────────────────────

classes = (
    LIGHTEXCL_OT_exclude_selection,
    LIGHTEXCL_OT_include_selection,
    LIGHTEXCL_OT_exclude_collection,
    LIGHTEXCL_OT_include_collection,
    LIGHTEXCL_OT_coll_to_coll_exclude,
    LIGHTEXCL_OT_coll_to_coll_include,
    LIGHTEXCL_MT_context_menu,
    LIGHTEXCL_PT_panel,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.VIEW3D_MT_object_context_menu.append(_draw_context_menu)


def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.remove(_draw_context_menu)
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
