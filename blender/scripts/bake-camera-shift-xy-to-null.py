# by codywinch

import bpy
from pathlib import Path
import datetime

# CALCULATE 2D TRACK
bpy.context.scene.frame_set(bpy.context.scene.frame_start)

cam = bpy.context.scene.camera

t_fac = 1 / 24

track_obs = [cam]
times, locs = [], []
for i in range(bpy.context.scene.frame_end - bpy.context.scene.frame_start + 1):
    for o, ob in enumerate(track_obs):
        if i == 0:
            times.append([])
            locs.append([])


        times[o].append(i * t_fac)

        locs[o].append([cam.data.shift_x, cam.data.shift_y])

    bpy.context.scene.frame_set(bpy.context.scene.frame_current + 1)

#
#
#

# WRITE JSX FILE
file = Path(bpy.context.blend_data.filepath)

fp = str(file.parent) + "//AE Cam Shifts Export.jsx"

jsx_file = open(fp, "w")

jsx_file.write("/**************************************\n")
jsx_file.write("File : %s\n" % file.name.replace(".blend", ""))
jsx_file.write("Date : %s\n" % datetime.datetime.now())
jsx_file.write("**************************************/\n\n\n\n")

jsx_file.write('app.beginUndoGroup("Import Blender animation data");\n')

jsx_file.write("var missing = true;\n")
jsx_file.write("for (var i = 1; i <= app.project.numItems; i++) {\n")
jsx_file.write("    if (app.project.item(i) instanceof FolderItem) {\n")
jsx_file.write(
    '        if (app.project.item(i).name == "Blender Track Nulls") {\n'
)
jsx_file.write("            var trackFolder = app.project.item(i);\n")
jsx_file.write("            missing = false;\n")
jsx_file.write("        }\n")
jsx_file.write("    }\n")
jsx_file.write("}\n\n\n\n")

jsx_file.write("if (missing) {\n")
jsx_file.write(
    '    var trackFolder = app.project.items.addFolder("Blender Track Nulls");\n'
)
jsx_file.write("}\n\n\n\n")

for o, ob in enumerate(track_obs):
    jsx_file.write("var tracknull = app.project.activeItem.layers.addNull();\n")
    jsx_file.write(
        "tracknull.source.name = %s;\n" % ('"' + ob.name + ' Track"')
    )
    jsx_file.write("tracknull.source.parentFolder = trackFolder;\n")

    jsx_file.write("var locs = %s;\n" % (locs[o]))
    jsx_file.write("for (var i = 0; i < locs.length; i++) {\n")
    jsx_file.write("    locs[i][0] *= app.project.activeItem.width;\n")
    jsx_file.write("    locs[i][1] *= app.project.activeItem.height;\n")
    jsx_file.write("}\n\n\n\n")

    jsx_file.write(
        'tracknull.property("Position").setValuesAtTimes(%s,locs);\n\n'
        % (times[o])
    )

jsx_file.write("\n\n\n\n\n")

jsx_file.write("app.endUndoGroup();\n\n\n")

jsx_file.close()