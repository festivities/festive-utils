import bpy
import math

class BONEROLLER_OT_flip_roll(bpy.types.Operator):
    """Flip bone roll closer to 0 degrees"""
    bl_idname = "armature.boneroller_flip_roll"
    bl_label = "Flip Roll"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_ARMATURE' and context.selected_editable_bones

    def execute(self, context):
        for b in context.selected_editable_bones:
            r1 = b.roll + math.pi
            r2 = b.roll - math.pi
            b.roll = r1 if abs(r1) < abs(r2) else r2
        return {'FINISHED'}


class BONEROLLER_OT_add_roll(bpy.types.Operator):
    """Add angle to bone roll"""
    bl_idname = "armature.boneroller_add_roll"
    bl_label = "Add Roll"
    bl_options = {'REGISTER', 'UNDO'}

    angle: bpy.props.FloatProperty(
        name="Angle",
        description="Angle to add to bone roll",
        default=0.0,
        subtype='ANGLE'
    )

    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_ARMATURE' and context.selected_editable_bones

    def execute(self, context):
        for b in context.selected_editable_bones:
            b.roll += self.angle
        return {'FINISHED'}


class BONEROLLER_PT_panel(bpy.types.Panel):
    """Bone Roller Panel"""
    bl_label = "Bone Roller"
    bl_idname = "BONEROLLER_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Item'
    
    @classmethod
    def poll(cls, context):
        return context.mode == 'EDIT_ARMATURE'

    def draw(self, context):
        layout = self.layout

        layout.operator("armature.boneroller_flip_roll", text="Flip 180° (Closer to 0°)")

        layout.separator()
        layout.label(text="Increment/Decrement:")

        angles_deg = [22.5, 45.0, 90.0]
        
        for angle in angles_deg:
            row = layout.row(align=True)
            
            # format the number to remove .0 if it's an integer
            angle_str = f"{int(angle)}" if angle.is_integer() else f"{angle}"
            
            op_minus = row.operator("armature.boneroller_add_roll", text=f"-{angle_str}°")
            op_minus.angle = math.radians(-angle)
            
            op_plus = row.operator("armature.boneroller_add_roll", text=f"+{angle_str}°")
            op_plus.angle = math.radians(angle)


classes = (
    BONEROLLER_OT_flip_roll,
    BONEROLLER_OT_add_roll,
    BONEROLLER_PT_panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
