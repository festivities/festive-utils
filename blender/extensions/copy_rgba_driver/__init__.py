# SPDX-License-Identifier: GPL-3.0-or-later
"""
Copy RGBA Driver – Blender Extension

Adds entries to the right-click context menu of any RGB / RGBA colour property:

  • **Copy Color as Driver Source** – remembers the ID block and data-path so
    a new AVERAGE driver can be created on a target.
  • **Copy Color Drivers** – serialises the *existing* per-channel drivers so
    they can be duplicated onto another property.
  • **Paste Color Driver** – applies whichever clipboard mode was last used.
  • **Remove Color Drivers** – strips all channel drivers from the property.
"""

import bpy
from bpy.types import Operator


# ---------------------------------------------------------------------------
#   Clipboard  – stores copied driver data
# ---------------------------------------------------------------------------

# Two clipboard modes:
#   "source"  – the property itself is the source; paste creates AVERAGE drivers
#   "drivers" – existing driver configs are copied verbatim

class _DriverClipboard:
    """Module-level clipboard for colour driver data."""

    mode: str = ""              # "source" or "drivers"

    # -- "source" mode fields ------------------------------------------------
    id_data = None              # bpy.types.ID
    data_path: str = ""         # RNA path from the ID block
    channel_count: int = 0      # 3 (RGB) or 4 (RGBA)

    # -- "drivers" mode fields -----------------------------------------------
    driver_configs: list = []   # list of (index, config_dict) per channel

    @classmethod
    def store_source(cls, id_data, data_path, channel_count):
        cls.mode = "source"
        cls.id_data = id_data
        cls.data_path = data_path
        cls.channel_count = channel_count
        cls.driver_configs = []

    @classmethod
    def store_drivers(cls, configs, channel_count):
        cls.mode = "drivers"
        cls.driver_configs = configs
        cls.channel_count = channel_count
        cls.id_data = None
        cls.data_path = ""

    @classmethod
    def clear(cls):
        cls.mode = ""
        cls.id_data = None
        cls.data_path = ""
        cls.channel_count = 0
        cls.driver_configs = []

    @classmethod
    def is_set(cls) -> bool:
        if cls.mode == "source":
            return cls.id_data is not None and cls.data_path != ""
        if cls.mode == "drivers":
            return len(cls.driver_configs) > 0
        return False


# ---------------------------------------------------------------------------
#   Helpers
# ---------------------------------------------------------------------------

# Map Python ID class names → DriverTarget.id_type enum values.
_ID_TYPE_MAP = {
    "Action":            "ACTION",
    "Armature":          "ARMATURE",
    "Camera":            "CAMERA",
    "Collection":        "COLLECTION",
    "Curve":             "CURVE",
    "FreestyleLineStyle":"LINESTYLE",
    "GreasePencil":      "GREASEPENCIL",
    "GreasePencilv3":    "GREASEPENCIL",
    "Image":             "IMAGE",
    "Key":               "KEY",
    "Lattice":           "LATTICE",
    "Light":             "LIGHT",
    "LightProbe":        "LIGHT_PROBE",
    "Material":          "MATERIAL",
    "Mesh":              "MESH",
    "MetaBall":          "META",
    "MovieClip":         "MOVIECLIP",
    "NodeTree":          "NODETREE",
    "Object":            "OBJECT",
    "ParticleSettings":  "PARTICLE",
    "Scene":             "SCENE",
    "Sound":             "SOUND",
    "Speaker":           "SPEAKER",
    "Texture":           "TEXTURE",
    "Volume":            "VOLUME",
    "World":             "WORLD",
}

# Subtypes that are clearly *not* colours.
_NON_COLOR_SUBTYPES = frozenset({
    "TRANSLATION", "DIRECTION", "VELOCITY", "ACCELERATION",
    "XYZ", "XYZ_LENGTH", "EULER", "QUATERNION", "AXISANGLE",
    "MATRIX", "LAYER", "LAYER_MEMBER",
})


def _get_id_type(id_block) -> str:
    """Return the ``DriverTarget.id_type`` enum string for *id_block*.

    Walks the MRO so that subclasses (e.g. ``ShaderNodeTree`` →
    ``NodeTree`` → ``"NODETREE"``) are resolved automatically.
    """
    for cls in type(id_block).__mro__:
        result = _ID_TYPE_MAP.get(cls.__name__)
        if result is not None:
            return result
    return "OBJECT"


def _is_color_value(value) -> bool:
    """Return True if *value* looks like a 3- or 4-channel numeric array."""
    try:
        if hasattr(value, "__len__") and len(value) in (3, 4):
            return all(isinstance(v, (int, float)) for v in value)
    except TypeError:
        pass
    return False


def _is_color_button(context) -> bool:
    """Decide whether the right-clicked button represents a colour property."""
    prop = getattr(context, "button_prop", None)
    if prop is None:
        return False

    # --- Strategy 1: standard RNA metadata -----------------------------------
    prop_type = getattr(prop, "type", None)
    if prop_type == "FLOAT":
        length = getattr(prop, "array_length", 0)
        if length in (3, 4):
            subtype = getattr(prop, "subtype", "NONE")
            if subtype not in _NON_COLOR_SUBTYPES:
                return True

    # --- Strategy 2: inspect the live value ----------------------------------
    ptr = getattr(context, "button_pointer", None)
    if ptr is None:
        return False

    identifier = getattr(prop, "identifier", "")
    if not identifier:
        return False

    try:
        value = getattr(ptr, identifier)
        if _is_color_value(value):
            return True
    except (AttributeError, TypeError):
        pass

    try:
        value = ptr[identifier]
        if _is_color_value(value):
            return True
    except (KeyError, TypeError, IndexError):
        pass

    return False


def _resolve_button(context):
    """Return ``(id_data, data_path, channel_count)`` for the active button.

    Returns *None* when the button cannot be resolved to a drivable path.
    """
    ptr = getattr(context, "button_pointer", None)
    prop = getattr(context, "button_prop", None)
    if ptr is None or prop is None:
        return None

    id_block = ptr.id_data
    if id_block is None:
        return None

    identifier = getattr(prop, "identifier", "")
    if not identifier:
        return None

    # --- Build the data-path ------------------------------------------------
    data_path = None

    try:
        data_path = ptr.path_from_id(identifier)
    except (ValueError, TypeError, AttributeError):
        pass

    if not data_path:
        try:
            base = ptr.path_from_id()
            if base:
                data_path = f'{base}["{identifier}"]'
            else:
                data_path = f'["{identifier}"]'
        except (ValueError, TypeError):
            data_path = f'["{identifier}"]'

    if not data_path:
        return None

    # --- Determine channel count --------------------------------------------
    array_length = getattr(prop, "array_length", 0)

    if array_length not in (3, 4):
        try:
            value = getattr(ptr, identifier)
            if hasattr(value, "__len__"):
                array_length = len(value)
        except (AttributeError, TypeError):
            pass

    if array_length not in (3, 4):
        try:
            value = ptr[identifier]
            if hasattr(value, "__len__"):
                array_length = len(value)
        except (KeyError, TypeError, IndexError):
            pass

    if array_length not in (3, 4):
        return None

    return id_block, data_path, array_length


# ---------------------------------------------------------------------------
#   Driver serialisation helpers
# ---------------------------------------------------------------------------

def _serialize_driver(fcurve):
    """Capture an FCurve's driver configuration into a plain dict."""
    drv = fcurve.driver
    config = {
        "type": drv.type,
        "expression": drv.expression,
        "use_self": drv.use_self,
        "variables": [],
    }
    for var in drv.variables:
        var_cfg = {
            "name": var.name,
            "type": var.type,
            "targets": [],
        }
        for tgt in var.targets:
            tgt_cfg = {
                "id_type": tgt.id_type,
                "id": tgt.id,           # live reference – valid while .blend is open
                "data_path": tgt.data_path,
                "bone_target": tgt.bone_target,
                "transform_type": getattr(tgt, "transform_type", "LOC_X"),
                "transform_space": getattr(tgt, "transform_space", "WORLD_SPACE"),
                "rotation_mode": getattr(tgt, "rotation_mode", "AUTO"),
            }
            var_cfg["targets"].append(tgt_cfg)
        config["variables"].append(var_cfg)
    return config


def _apply_driver_config(fcurve, config):
    """Apply a previously serialised driver config onto *fcurve*."""
    drv = fcurve.driver
    drv.type = config["type"]
    drv.expression = config["expression"]
    drv.use_self = config["use_self"]

    # Clear existing variables.
    for v in reversed(drv.variables):
        drv.variables.remove(v)

    for var_cfg in config["variables"]:
        var = drv.variables.new()
        var.name = var_cfg["name"]
        var.type = var_cfg["type"]

        for i, tgt_cfg in enumerate(var_cfg["targets"]):
            if i >= len(var.targets):
                break
            tgt = var.targets[i]
            tgt.id_type = tgt_cfg["id_type"]
            tgt.id = tgt_cfg["id"]
            tgt.data_path = tgt_cfg["data_path"]
            if var.type == "TRANSFORMS":
                tgt.bone_target = tgt_cfg.get("bone_target", "")
                tgt.transform_type = tgt_cfg.get("transform_type", "LOC_X")
                tgt.transform_space = tgt_cfg.get("transform_space", "WORLD_SPACE")
                tgt.rotation_mode = tgt_cfg.get("rotation_mode", "AUTO")


def _find_channel_drivers(id_block, data_path, channel_count):
    """Return a dict ``{array_index: FCurve}`` for existing channel drivers."""
    anim = id_block.animation_data
    if anim is None:
        return {}
    result = {}
    for fc in anim.drivers:
        if fc.data_path == data_path and 0 <= fc.array_index < channel_count:
            result[fc.array_index] = fc
    return result


def _has_channel_drivers(context) -> bool:
    """Return True if the current colour button already has drivers."""
    resolved = _resolve_button(context)
    if resolved is None:
        return False
    id_block, data_path, channels = resolved
    return len(_find_channel_drivers(id_block, data_path, channels)) > 0


# ---------------------------------------------------------------------------
#   Operators
# ---------------------------------------------------------------------------

class COPYRGBA_OT_copy_as_source(Operator):
    """Copy this colour property as a driver source (all channels)"""

    bl_idname = "ui.copy_rgba_as_driver"
    bl_label = "Copy Color as Driver Source"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return _is_color_button(context)

    def execute(self, context):
        result = _resolve_button(context)
        if result is None:
            self.report({"WARNING"}, "Cannot resolve an RNA path for this property")
            return {"CANCELLED"}

        id_data, data_path, channels = result
        _DriverClipboard.store_source(id_data, data_path, channels)

        tag = "RGBA" if channels == 4 else "RGB"
        self.report({"INFO"}, f"Copied {tag} driver source: {id_data.name_full} ▸ {data_path}")
        return {"FINISHED"}


class COPYRGBA_OT_copy_drivers(Operator):
    """Copy the existing per-channel drivers from this colour property"""

    bl_idname = "ui.copy_rgba_drivers"
    bl_label = "Copy Color Drivers"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        if not _is_color_button(context):
            return False
        return _has_channel_drivers(context)

    def execute(self, context):
        result = _resolve_button(context)
        if result is None:
            self.report({"WARNING"}, "Cannot resolve an RNA path for this property")
            return {"CANCELLED"}

        id_data, data_path, channels = result
        found = _find_channel_drivers(id_data, data_path, channels)

        if not found:
            self.report({"WARNING"}, "No drivers found on this property")
            return {"CANCELLED"}

        configs = [(idx, _serialize_driver(fc)) for idx, fc in sorted(found.items())]
        _DriverClipboard.store_drivers(configs, channels)

        tag = "RGBA" if channels == 4 else "RGB"
        self.report(
            {"INFO"},
            f"Copied {len(configs)}-channel {tag} driver(s) from "
            f"{id_data.name_full} ▸ {data_path}",
        )
        return {"FINISHED"}


class COPYRGBA_OT_paste_driver(Operator):
    """Paste colour drivers from the clipboard"""

    bl_idname = "ui.paste_rgba_as_driver"
    bl_label = "Paste Color Driver"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not _DriverClipboard.is_set():
            return False
        return _is_color_button(context)

    def execute(self, context):
        if _DriverClipboard.mode == "source":
            return self._paste_from_source(context)
        elif _DriverClipboard.mode == "drivers":
            return self._paste_from_drivers(context)
        else:
            self.report({"ERROR"}, "Clipboard is empty")
            return {"CANCELLED"}

    # -- paste mode: "source" ------------------------------------------------

    def _paste_from_source(self, context):
        result = _resolve_button(context)
        if result is None:
            self.report({"WARNING"}, "Cannot resolve an RNA path for the target property")
            return {"CANCELLED"}

        target_id, target_path, target_channels = result
        src_id = _DriverClipboard.id_data
        src_path = _DriverClipboard.data_path
        src_channels = _DriverClipboard.channel_count

        num = min(src_channels, target_channels)
        added = 0

        for i in range(num):
            try:
                fcurve = target_id.driver_add(target_path, i)
            except Exception as exc:
                self.report({"WARNING"}, f"Channel {i}: {exc}")
                continue

            drv = fcurve.driver
            drv.type = "AVERAGE"

            for var in reversed(drv.variables):
                drv.variables.remove(var)

            var = drv.variables.new()
            var.name = "src"
            var.type = "SINGLE_PROP"

            tgt = var.targets[0]
            tgt.id_type = _get_id_type(src_id)
            tgt.id = src_id
            tgt.data_path = f"{src_path}[{i}]"

            added += 1

        if added == 0:
            self.report({"ERROR"}, "Failed to create any channel drivers")
            return {"CANCELLED"}

        tag = "RGBA" if added == 4 else "RGB"
        self.report(
            {"INFO"},
            f"Pasted {added}-channel {tag} driver  "
            f"{src_id.name_full} → {target_id.name_full}",
        )
        return {"FINISHED"}

    # -- paste mode: "drivers" -----------------------------------------------

    def _paste_from_drivers(self, context):
        result = _resolve_button(context)
        if result is None:
            self.report({"WARNING"}, "Cannot resolve an RNA path for the target property")
            return {"CANCELLED"}

        target_id, target_path, target_channels = result
        added = 0

        for idx, config in _DriverClipboard.driver_configs:
            if idx >= target_channels:
                continue
            try:
                fcurve = target_id.driver_add(target_path, idx)
            except Exception as exc:
                self.report({"WARNING"}, f"Channel {idx}: {exc}")
                continue

            _apply_driver_config(fcurve, config)
            added += 1

        if added == 0:
            self.report({"ERROR"}, "Failed to paste any channel drivers")
            return {"CANCELLED"}

        tag = "RGBA" if added == 4 else "RGB"
        self.report({"INFO"}, f"Pasted {added}-channel {tag} driver configuration")
        return {"FINISHED"}


class COPYRGBA_OT_remove_driver(Operator):
    """Remove all channel drivers from this colour property"""

    bl_idname = "ui.remove_rgba_driver"
    bl_label = "Remove Color Drivers"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _is_color_button(context)

    def execute(self, context):
        result = _resolve_button(context)
        if result is None:
            self.report({"WARNING"}, "Cannot resolve an RNA path for this property")
            return {"CANCELLED"}

        id_data, data_path, channels = result
        removed = 0

        for i in range(channels):
            try:
                id_data.driver_remove(data_path, i)
                removed += 1
            except Exception:
                pass

        if removed:
            self.report({"INFO"}, f"Removed {removed} channel driver(s)")
        else:
            self.report({"INFO"}, "No drivers to remove")
        return {"FINISHED"}


# ---------------------------------------------------------------------------
#   Context-menu draw callback
# ---------------------------------------------------------------------------

def _draw_context_menu(self, context):
    """Append colour-driver items to the right-click button menu."""
    if not _is_color_button(context):
        return

    layout = self.layout
    layout.separator()

    layout.operator(
        COPYRGBA_OT_copy_as_source.bl_idname,
        icon="DRIVER",
    )

    layout.operator(
        COPYRGBA_OT_copy_drivers.bl_idname,
        icon="COPYDOWN",
    )

    if _DriverClipboard.is_set():
        layout.operator(
            COPYRGBA_OT_paste_driver.bl_idname,
            icon="PASTEDOWN",
        )

    layout.operator(
        COPYRGBA_OT_remove_driver.bl_idname,
        icon="X",
    )


# ---------------------------------------------------------------------------
#   Registration
# ---------------------------------------------------------------------------

_classes = (
    COPYRGBA_OT_copy_as_source,
    COPYRGBA_OT_copy_drivers,
    COPYRGBA_OT_paste_driver,
    COPYRGBA_OT_remove_driver,
)


def register():
    for cls in _classes:
        bpy.utils.register_class(cls)
    bpy.types.UI_MT_button_context_menu.append(_draw_context_menu)


def unregister():
    bpy.types.UI_MT_button_context_menu.remove(_draw_context_menu)
    for cls in reversed(_classes):
        bpy.utils.unregister_class(cls)
