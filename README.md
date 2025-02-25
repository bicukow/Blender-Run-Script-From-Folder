![preview](https://github.com/user-attachments/assets/1696b8ee-404d-424f-9385-793b28eef78d)

https://extensions.blender.org/approval-queue/blender-run-scripts-from-folder/

Quick operator to choose script to be executed from Folder path in preferences -> File Paths -> Script Directories (The first folder will be used for .py scripts lookup)

You can find operator by opening search menu (F3) and typing 'Run Script From Folder', you can also add it to quick menu (q), and give it a key shortcut

Freed from Context Overriding for .ops:
This addon allows run bpy.ops operators without area context overridng, since you can just execute your script from the right window context, so you can make your own ops macroses without annoying context overriding.

For example using operator bpy.ops.view3d.camera_to_view() requires to run it from '3D_VIEW' area context, so you cannot just write it to text editor end execute it, but with this addon you are able to this by executing Run Scripts From Folder from 3d Viewport.
