import bpy


def build_fk_name(def_name: str) -> str:
	if def_name.startswith("DEF-"):
		return "FK-" + def_name[4:]
	return "FK-" + def_name


def get_selected_bone_names(arm_obj: bpy.types.Object) -> list[str]:
	mode = bpy.context.mode

	if mode == "POSE":
		return [
			pb.name
			for pb in (bpy.context.selected_pose_bones or [])
			if pb.name.startswith("DEF-")
		]

	if mode == "EDIT_ARMATURE":
		return [
			eb.name
			for eb in arm_obj.data.edit_bones
			if eb.select and eb.name.startswith("DEF-")
		]

	if mode == "OBJECT":
		return [
			b.name
			for b in arm_obj.data.bones
			if b.select and b.name.startswith("DEF-")
		]

	return []


def duplicate_def_bones_to_fk(arm_obj: bpy.types.Object, source_names: list[str]) -> dict[str, str]:
	bpy.ops.object.mode_set(mode="EDIT")
	edit_bones = arm_obj.data.edit_bones

	mapping: dict[str, str] = {}
	original_parent_name_by_source: dict[str, str | None] = {}
	for name in source_names:
		src = edit_bones.get(name)
		if src is None:
			continue

		fk_bone = edit_bones.new(build_fk_name(src.name))
		fk_bone.head = src.head
		fk_bone.tail = src.tail
		fk_bone.roll = src.roll
		fk_bone.use_connect = False
		fk_bone.use_deform = False

		mapping[src.name] = fk_bone.name
		original_parent_name_by_source[src.name] = src.parent.name if src.parent else None

	for src_name, fk_name in mapping.items():
		src = edit_bones.get(src_name)
		fk_bone = edit_bones.get(fk_name)
		if src is None or fk_bone is None:
			continue

		parent_name = original_parent_name_by_source.get(src_name)
		if parent_name in mapping:
			fk_parent = edit_bones.get(mapping[parent_name])
			fk_bone.parent = fk_parent
		else:
			fk_bone.parent = src.parent

	return mapping


def add_copy_transform_constraints(arm_obj: bpy.types.Object, mapping: dict[str, str]) -> None:
	bpy.ops.object.mode_set(mode="POSE")

	for src_name, fk_name in mapping.items():
		pose_bone = arm_obj.pose.bones.get(src_name)
		if pose_bone is None:
			continue

		existing = None
		for c in pose_bone.constraints:
			if c.type == "COPY_TRANSFORMS" and c.target == arm_obj and c.subtarget == fk_name:
				existing = c
				break

		constraint = existing or pose_bone.constraints.new(type="COPY_TRANSFORMS")
		constraint.name = "FK Copy Transforms"
		constraint.target = arm_obj
		constraint.subtarget = fk_name
		constraint.target_space = "POSE"
		constraint.owner_space = "POSE"


def main() -> None:
	arm_obj = bpy.context.active_object
	if arm_obj is None or arm_obj.type != "ARMATURE":
		raise RuntimeError("Select an armature object and select DEF bones first.")

	original_mode = bpy.context.mode
	selected_names = get_selected_bone_names(arm_obj)

	if not selected_names:
		raise RuntimeError("No selected bones with 'DEF-' prefix were found.")

	mapping = duplicate_def_bones_to_fk(arm_obj, selected_names)
	add_copy_transform_constraints(arm_obj, mapping)

	if original_mode in {"POSE", "EDIT_ARMATURE", "OBJECT"}:
		restore_mode = "EDIT" if original_mode == "EDIT_ARMATURE" else original_mode
		bpy.ops.object.mode_set(mode=restore_mode)

	print(f"Created {len(mapping)} FK control bones and applied Copy Transforms constraints.")


main()
