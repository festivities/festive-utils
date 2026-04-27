import bpy


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _is_light_object(obj):
    """Return True if *obj* is a light or an emissive-mesh that can own linking collections."""
    return obj and obj.type == 'LIGHT'


def _get_selected_non_lights(context):
    """Return selected objects/collections that are NOT lights (the targets to exclude)."""
    return [o for o in context.selected_objects if not _is_light_object(o)]


def _ensure_linking_collection(light_obj, link_type):
    """
    Ensure the light has a linking collection for *link_type*
    ('receiver_collection' or 'blocker_collection').
    Creates one if it doesn't exist yet.
    Returns the collection.
    """
    coll = getattr(light_obj.light_linking, link_type)
    if coll is None:
        coll = bpy.data.collections.new(f"{light_obj.name}_{link_type}")
        setattr(light_obj.light_linking, link_type, coll)
    return coll


def _link_item_to_collection(coll, item):
    """
    Link *item* (Object or Collection) into *coll* if not already present.
    Returns True if newly linked, False if it was already there.
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
    Return a list of collections that contain at least one selected object.
    Useful when the user wants to exclude whole collections rather than
    individual objects.
    """
    selected = set(context.selected_objects)
    result = []
    for coll in bpy.data.collections:
        if set(coll.objects) & selected:
            result.append(coll)
    return result


# ──────────────────────────────────────────────────────────────
# Operators
# ──────────────────────────────────────────────────────────────

class LIGHTEXCL_OT_exclude_from_lights(bpy.types.Operator):
    """Exclude selected objects/collections from target lights' light and/or shadow linking"""
    bl_idname = f"object.{__package__}_exclude"
    bl_label = "Exclude from Lights"
    bl_options = {'REGISTER', 'UNDO'}

    # ── Operator properties (shown in the redo panel) ──

    link_mode: bpy.props.EnumProperty(
        name="Linking Mode",
        description="Which linking collections to add exclusions to",
        items=[
            ('BOTH',   "Light + Shadow", "Exclude from both light and shadow linking"),
            ('LIGHT',  "Light Only",     "Exclude from light linking only"),
            ('SHADOW', "Shadow Only",    "Exclude from shadow linking only"),
            ('NONE',   "Remove All",     "Remove exclusions from both (re-include)"),
        ],
        default='BOTH',
    )

    target_type: bpy.props.EnumProperty(
        name="Target Type",
        description="What to add to the linking collections",
        items=[
            ('OBJECTS',     "Objects",     "Exclude selected objects individually"),
            ('COLLECTIONS', "Collections", "Exclude collections that contain selected objects"),
        ],
        default='OBJECTS',
    )

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            return False
        has_lights = any(_is_light_object(o) for o in context.selected_objects)
        has_non_lights = any(not _is_light_object(o) for o in context.selected_objects)
        return has_lights and has_non_lights

    def execute(self, context):
        # Split selection into lights (targets) and things to exclude
        lights = [o for o in context.selected_objects if _is_light_object(o)]
        exclude_items = (
            _get_selected_non_lights(context)
            if self.target_type == 'OBJECTS'
            else _get_collections_for_selected(context)
        )

        if not exclude_items:
            self.report({'WARNING'}, "No valid objects/collections to exclude")
            return {'CANCELLED'}

        do_light  = self.link_mode in ('BOTH', 'LIGHT')
        do_shadow = self.link_mode in ('BOTH', 'SHADOW')
        do_remove = self.link_mode == 'NONE'

        count = 0
        for light in lights:
            for item in exclude_items:
                # ── Light linking ──
                if do_light:
                    coll = _ensure_linking_collection(light, 'receiver_collection')
                    _link_item_to_collection(coll, item)
                    _set_link_state(coll, item, 'EXCLUDE')
                    count += 1

                # ── Shadow linking ──
                if do_shadow:
                    coll = _ensure_linking_collection(light, 'blocker_collection')
                    _link_item_to_collection(coll, item)
                    _set_link_state(coll, item, 'EXCLUDE')
                    count += 1

                # ── Remove (re-include) ──
                if do_remove:
                    for attr in ('receiver_collection', 'blocker_collection'):
                        coll = getattr(light.light_linking, attr)
                        if coll is None:
                            continue
                        _set_link_state(coll, item, 'INCLUDE')
                        count += 1

        mode_label = dict(self.rna_type.properties['link_mode'].enum_items_static)[self.link_mode]
        self.report({'INFO'}, f"Processed {count} exclusion(s) ({mode_label})")
        return {'FINISHED'}


class LIGHTEXCL_OT_include_in_lights(bpy.types.Operator):
    """Re-include selected objects/collections in target lights' linking (undo exclusions)"""
    bl_idname = f"object.{__package__}_include"
    bl_label = "Include in Lights"
    bl_options = {'REGISTER', 'UNDO'}

    link_mode: bpy.props.EnumProperty(
        name="Linking Mode",
        description="Which linking collections to re-include in",
        items=[
            ('BOTH',   "Light + Shadow", "Re-include in both light and shadow linking"),
            ('LIGHT',  "Light Only",     "Re-include in light linking only"),
            ('SHADOW', "Shadow Only",    "Re-include in shadow linking only"),
        ],
        default='BOTH',
    )

    target_type: bpy.props.EnumProperty(
        name="Target Type",
        description="What to re-include in the linking collections",
        items=[
            ('OBJECTS',     "Objects",     "Re-include selected objects individually"),
            ('COLLECTIONS', "Collections", "Re-include collections that contain selected objects"),
        ],
        default='OBJECTS',
    )

    @classmethod
    def poll(cls, context):
        if context.mode != 'OBJECT':
            return False
        has_lights = any(_is_light_object(o) for o in context.selected_objects)
        has_non_lights = any(not _is_light_object(o) for o in context.selected_objects)
        return has_lights and has_non_lights

    def execute(self, context):
        lights = [o for o in context.selected_objects if _is_light_object(o)]
        include_items = (
            _get_selected_non_lights(context)
            if self.target_type == 'OBJECTS'
            else _get_collections_for_selected(context)
        )

        if not include_items:
            self.report({'WARNING'}, "No valid objects/collections to include")
            return {'CANCELLED'}

        do_light  = self.link_mode in ('BOTH', 'LIGHT')
        do_shadow = self.link_mode in ('BOTH', 'SHADOW')

        count = 0
        for light in lights:
            for item in include_items:
                if do_light:
                    coll = getattr(light.light_linking, 'receiver_collection')
                    if coll is not None:
                        _set_link_state(coll, item, 'INCLUDE')
                        count += 1

                if do_shadow:
                    coll = getattr(light.light_linking, 'blocker_collection')
                    if coll is not None:
                        _set_link_state(coll, item, 'INCLUDE')
                        count += 1

        self.report({'INFO'}, f"Re-included {count} item(s)")
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

        # ── Info box ──
        sel = context.selected_objects
        lights = [o for o in sel if _is_light_object(o)]
        non_lights = [o for o in sel if not _is_light_object(o)]

        box = layout.box()
        box.label(text=f"Lights: {len(lights)}  |  Objects: {len(non_lights)}", icon='LIGHT')
        if not lights:
            box.label(text="Select at least one light", icon='ERROR')
        if not non_lights:
            box.label(text="Select objects to exclude", icon='ERROR')

        layout.separator()

        # ── Exclude section ──
        col = layout.column(align=True)
        col.label(text="Exclude from Lights:", icon='REMOVE')

        row = col.row(align=True)
        op = row.operator(LIGHTEXCL_OT_exclude_from_lights.bl_idname,
                          text="Both", icon='CON_TRACKTO')
        op.link_mode = 'BOTH'
        op.target_type = 'OBJECTS'

        op = row.operator(LIGHTEXCL_OT_exclude_from_lights.bl_idname,
                          text="Light", icon='LIGHT')
        op.link_mode = 'LIGHT'
        op.target_type = 'OBJECTS'

        op = row.operator(LIGHTEXCL_OT_exclude_from_lights.bl_idname,
                          text="Shadow", icon='SHADOW')
        op.link_mode = 'SHADOW'
        op.target_type = 'OBJECTS'

        # Collection-level exclusion
        row = col.row(align=True)
        row.label(text="By Collection:")
        op = row.operator(LIGHTEXCL_OT_exclude_from_lights.bl_idname,
                          text="Both", icon='OUTLINER_COLLECTION')
        op.link_mode = 'BOTH'
        op.target_type = 'COLLECTIONS'

        op = row.operator(LIGHTEXCL_OT_exclude_from_lights.bl_idname,
                          text="Light", icon='LIGHT')
        op.link_mode = 'LIGHT'
        op.target_type = 'COLLECTIONS'

        op = row.operator(LIGHTEXCL_OT_exclude_from_lights.bl_idname,
                          text="Shadow", icon='SHADOW')
        op.link_mode = 'SHADOW'
        op.target_type = 'COLLECTIONS'

        layout.separator()

        # ── Re-include section ──
        col = layout.column(align=True)
        col.label(text="Re-include in Lights:", icon='ADD')

        row = col.row(align=True)
        op = row.operator(LIGHTEXCL_OT_include_in_lights.bl_idname,
                          text="Both", icon='CON_TRACKTO')
        op.link_mode = 'BOTH'
        op.target_type = 'OBJECTS'

        op = row.operator(LIGHTEXCL_OT_include_in_lights.bl_idname,
                          text="Light", icon='LIGHT')
        op.link_mode = 'LIGHT'
        op.target_type = 'OBJECTS'

        op = row.operator(LIGHTEXCL_OT_include_in_lights.bl_idname,
                          text="Shadow", icon='SHADOW')
        op.link_mode = 'SHADOW'
        op.target_type = 'OBJECTS'

        row = col.row(align=True)
        row.label(text="By Collection:")
        op = row.operator(LIGHTEXCL_OT_include_in_lights.bl_idname,
                          text="Both", icon='OUTLINER_COLLECTION')
        op.link_mode = 'BOTH'
        op.target_type = 'COLLECTIONS'

        op = row.operator(LIGHTEXCL_OT_include_in_lights.bl_idname,
                          text="Light", icon='LIGHT')
        op.link_mode = 'LIGHT'
        op.target_type = 'COLLECTIONS'

        op = row.operator(LIGHTEXCL_OT_include_in_lights.bl_idname,
                          text="Shadow", icon='SHADOW')
        op.link_mode = 'SHADOW'
        op.target_type = 'COLLECTIONS'


# ──────────────────────────────────────────────────────────────
# Right-click context menu
# ──────────────────────────────────────────────────────────────

def _draw_context_menu(self, context):
    """Append a submenu to the Object context menu."""
    if context.mode != 'OBJECT':
        return
    sel = context.selected_objects
    if not any(_is_light_object(o) for o in sel):
        return
    if not any(not _is_light_object(o) for o in sel):
        return

    self.layout.separator()
    self.layout.menu(LIGHTEXCL_MT_context_menu.bl_idname, icon='LIGHT')


class LIGHTEXCL_MT_context_menu(bpy.types.Menu):
    bl_label = "Light Excluder"
    bl_idname = "LIGHTEXCL_MT_context_menu"

    def draw(self, context):
        layout = self.layout

        layout.label(text="Exclude:")
        op = layout.operator(LIGHTEXCL_OT_exclude_from_lights.bl_idname,
                             text="Light + Shadow")
        op.link_mode = 'BOTH'
        op.target_type = 'OBJECTS'

        op = layout.operator(LIGHTEXCL_OT_exclude_from_lights.bl_idname,
                             text="Light Only")
        op.link_mode = 'LIGHT'
        op.target_type = 'OBJECTS'

        op = layout.operator(LIGHTEXCL_OT_exclude_from_lights.bl_idname,
                             text="Shadow Only")
        op.link_mode = 'SHADOW'
        op.target_type = 'OBJECTS'

        layout.separator()
        layout.label(text="Re-include:")
        op = layout.operator(LIGHTEXCL_OT_include_in_lights.bl_idname,
                             text="Light + Shadow")
        op.link_mode = 'BOTH'
        op.target_type = 'OBJECTS'

        op = layout.operator(LIGHTEXCL_OT_include_in_lights.bl_idname,
                             text="Light Only")
        op.link_mode = 'LIGHT'
        op.target_type = 'OBJECTS'

        op = layout.operator(LIGHTEXCL_OT_include_in_lights.bl_idname,
                             text="Shadow Only")
        op.link_mode = 'SHADOW'
        op.target_type = 'OBJECTS'


# ──────────────────────────────────────────────────────────────
# Registration
# ──────────────────────────────────────────────────────────────

classes = (
    LIGHTEXCL_OT_exclude_from_lights,
    LIGHTEXCL_OT_include_in_lights,
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
