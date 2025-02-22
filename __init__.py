import bpy

import bpy
from os.path import isfile, join
from os import listdir

from bpy.props import (IntProperty,
                       BoolProperty,
                       StringProperty,
                       CollectionProperty,
                       PointerProperty)

from bpy.types import (Operator,
                       Panel,
                       PropertyGroup,
                       UIList)

# User input Property Group:
class scripts_prop_group_list(PropertyGroup):
    name: bpy.props.StringProperty(name = "name")
    item: bpy.props.StringProperty(name = "item")

class scriptspaths_prop_group_list(PropertyGroup):
    name: bpy.props.StringProperty(name = "name")
    item: bpy.props.StringProperty(name = "item")
    
## defs ##
def scripts_directories_exist(): # check that directories are defined
    return len(bpy.utils.script_paths_pref()) > 0

def text_load_and_run(filepath, context): # main function: load, run (bpy.ops) and remove with context override
    try:
        loaded_text = bpy.data.texts.load(filepath)
        override = bpy.context.copy()
        override["edit_text"] = loaded_text
        with context.temp_override(**override):
            bpy.ops.text.run_script()
        bpy.data.texts.remove(loaded_text)
        error_was_raised = False
    except:
        error_was_raised = True
        #print('There is an error in the evaluated sctipt. Check system console')
        bpy.data.texts.remove(loaded_text)
    return error_was_raised

# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------

class RSFF_OT_refresh_scripts_list(Operator):
    bl_label = "refresh_scripts_list"
    bl_idname = "rsff.refresh_scripts_list"
    bl_description = "Refresh Scripts Paths and Scripts Files"
    bl_options = {"INTERNAL"}
    
    def execute(self, context):
        bpy.context.scene.scriptspaths_list.clear()
        bpy.context.scene.scripts_list.clear()
        # update scriptspaths list
        for index, i in enumerate(bpy.utils.script_paths_pref()):
            bpy.context.scene.scriptspaths_list.add()
            bpy.context.scene.scriptspaths_list[index].name = bpy.path.basename(i)
            bpy.context.scene.scriptspaths_list[index].item = i
    
        scripts_path_index = bpy.context.scene.scriptspaths_list_index
        scripts_path = bpy.context.scene.scriptspaths_list[scripts_path_index].item
        allfiles_list = [f for f in listdir(scripts_path) if isfile(join(scripts_path, f))] # get all files in dir
        files_list = [f for f in allfiles_list if '.py' in f]  
        # update scripts list
        for index, i in enumerate(files_list):
            bpy.context.scene.scripts_list.add()
            bpy.context.scene.scripts_list[index].name = i
            bpy.context.scene.scripts_list[index].item = join(scripts_path,i)
    
        return {'FINISHED'}

# -------------------------------------------------------------------
#   UI
# -------------------------------------------------------------------

class RSFF_UIList_Scripts(UIList):
    '''Scripts List '''
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        #icon = 'FILE_SCRIPT'
        #ob = data
        #slot = item
        scene = context.scene
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if scene:
                layout.prop(item, "name", text="", emboss=False, icon_value=icon, icon='FILE_SCRIPT')
            else:
                layout.label(text="", translate=False, icon_value=icon)
        # 'GRID' layout type should be as compact as possible (typically a single icon!).
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
        
    def invoke(self, context, event):
        pass
    
class RSFF_UIList_ScriptsPaths(UIList):
    '''ScriptsPaths List '''
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        scene = context.scene
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            if scene:
                layout.prop(item, "name", text="", emboss=False, icon_value=icon, icon='FILE_FOLDER')
            else:
                layout.label(text="aaa", translate=False, icon_value=icon)
        elif self.layout_type == 'GRID':
            layout.alignment = 'CENTER'
            layout.label(text="", icon_value=icon)
        
    def invoke(self, context, event):
        pass


class RSFF_OT_Popup(bpy.types.Operator):
    bl_label = "run_script_from_folder".replace('_',' ').title()
    bl_idname = "wm.run_script_from_folder"
    bl_options = {'REGISTER', 'UNDO'}

    def draw(self, context):
        layout = self.layout
        # info warning:
        if scripts_directories_exist() is False:
            row = layout.row()
            row.label(text="No Folders in 'File Paths' -> 'Scripts Directories'", icon='WARNING_LARGE')
        else:
            # Update Button
            col = layout.column(align=True)
            col.operator(RSFF_OT_refresh_scripts_list.bl_idname, text="Refresh Folder", icon="FILE_REFRESH")
            # UIList
            scene = context.scene
            # Scripts List:
            layout.template_list("RSFF_UIList_ScriptsPaths", "", scene, "scriptspaths_list", scene, "scriptspaths_list_index", type='DEFAULT',rows=2)
            # Scripts Paths:
            layout.template_list("RSFF_UIList_Scripts", "", scene, "scripts_list", scene, "scripts_list_index", type='DEFAULT', rows=10)
        
    def execute(self, context):
        index = bpy.context.scene['scripts_list_index'] 
        folder_path = bpy.context.scene['scripts_list'][index]['item']
        error = text_load_and_run(folder_path, context)
        if error == True:
            self.report({'ERROR'}, 'There is an error in the evaluated sctipt. Check system console')
        return {'FINISHED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self) 

# Register and Unregister classes from Blender:
classes = (
    scripts_prop_group_list,
    scriptspaths_prop_group_list,
    RSFF_UIList_Scripts,
    RSFF_UIList_ScriptsPaths,
    RSFF_OT_Popup,
    RSFF_OT_refresh_scripts_list,
)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    # UIListScriptsList:
    bpy.types.Scene.scripts_list = bpy.props.CollectionProperty(type=scripts_prop_group_list)
    bpy.types.Scene.scripts_list_index = bpy.props.IntProperty(default=0, min= 0)
    # UIListSCriptsPathsList:
    bpy.types.Scene.scriptspaths_list =bpy.props.CollectionProperty(type=scriptspaths_prop_group_list)
    bpy.types.Scene.scriptspaths_list_index = bpy.props.IntProperty(default=0, min=0)

def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)
# UIList:
    del bpy.types.Scene.my_tool
    del bpy.types.Scene.scripts_list
    del bpy.types.Scene.scripts_list_index
    del bpy.types.Scene.scriptspaths_list
    del bpy.types.Scene.scriptspaths_list_index


if __name__ == '__main__': register()
