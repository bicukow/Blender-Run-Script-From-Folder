import bpy
from os.path import isfile, join
from os import listdir

from bpy.props import (IntProperty, StringProperty, CollectionProperty, PointerProperty)
from bpy.types import (Operator, Panel, PropertyGroup, UIList)    
# -------------------------------------------------------------------
#   Funcs
# -------------------------------------------------------------------
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

def refresh_scripts_list(self, context): # self / context for callback func
    print('refresh_scripts_list')
    bpy.context.scene.RSFF.scriptspaths_list.clear()
    bpy.context.scene.RSFF.scripts_list.clear()
    # update scriptspaths list
    for index, i in enumerate(bpy.utils.script_paths_pref()):
        bpy.context.scene.RSFF.scriptspaths_list.add()
        bpy.context.scene.RSFF.scriptspaths_list[index].name = bpy.path.basename(i)
        bpy.context.scene.RSFF.scriptspaths_list[index].item = i

    scripts_path_index = bpy.context.scene.RSFF.scriptspaths_list_index
    scripts_path = bpy.context.scene.RSFF.scriptspaths_list[scripts_path_index].item
    allfiles_list = [f for f in listdir(scripts_path) if isfile(join(scripts_path, f))] # get all files in dir
    files_list = [f for f in allfiles_list if '.py' in f]  
    # update scripts list
    for index, i in enumerate(files_list):
        bpy.context.scene.RSFF.scripts_list.add()
        bpy.context.scene.RSFF.scripts_list[index].name = i
        bpy.context.scene.RSFF.scripts_list[index].item = join(scripts_path,i)
# -------------------------------------------------------------------
#   Operators
# -------------------------------------------------------------------
class RSFF_OT_refresh_scripts_list(Operator):
    bl_label = "refresh_scripts_list"
    bl_idname = "rsff.refresh_scripts_list"
    bl_description = "Refresh Scripts Paths and Scripts Files"
    bl_options = {"INTERNAL"}

    def execute(self, context):
        refresh_scripts_list(self, context)
        return {'FINISHED'}
# -------------------------------------------------------------------
#   UI
# -------------------------------------------------------------------

class RSFF_UL_UIList_Scripts(UIList):
    '''Scripts List '''
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=icon, icon='FILE_SCRIPT')
        
    def invoke(self, context, event):
        pass
    
class RSFF_UL_UIList_ScriptsPaths(UIList):
    '''ScriptsPaths List '''
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname):
        layout.prop(item, "name", text="", emboss=False, icon_value=icon, icon='FILE_FOLDER')

class RSFF_OT_Popup(bpy.types.Operator):
    bl_label = "run_script_from_folder".replace('_',' ').title()
    bl_idname = "wm.run_script_from_folder"
    bl_options = {'UNDO'}

    def draw(self, context):
        layout = self.layout
        # info warning:
        if scripts_directories_exist() is False:
            row = layout.row()
            row.label(text="Specify \"Scripts Directories\" in Preferences", icon = 'INFO')
        else:
            row = layout.row()
            # split column : Text
            row.label(text="Select Folder:", icon='FILE_FOLDER')
            # split column : Refresh Button
            row.operator(RSFF_OT_refresh_scripts_list.bl_idname, text="Refresh", icon="FILE_REFRESH")
            # UIList
            scene = context.scene.RSFF
            # ScriptsPaths List:
            layout.template_list("RSFF_UL_UIList_ScriptsPaths", "", scene, "scriptspaths_list", scene, "scriptspaths_list_index", rows=2)
            row = layout.column(align=True)
            row.label(text="Select Script to be executed:", icon='FILE_SCRIPT')
            # Scripts List:
            layout.template_list("RSFF_UL_UIList_Scripts", "", scene, "scripts_list", scene, "scripts_list_index", rows=10)
        
    def execute(self, context):
        if scripts_directories_exist() is True:
            index = bpy.context.scene.RSFF.scripts_list_index
            folder_path = bpy.context.scene.RSFF.scripts_list[index].item
            error = text_load_and_run(folder_path, context)
            if error == True:
                self.report({'ERROR'}, 'Python Script Error: Check System Console')
            return {'FINISHED'}
        else:
            return {'CANCELLED'}
    
    def invoke(self, context, event):
        wm = context.window_manager
        if scripts_directories_exist() is True:
            refresh_scripts_list(self, context)
            return wm.invoke_props_dialog(self) 
        else: 
            return wm.invoke_props_dialog(self)
        
# -------------------------------------------------------------------
#   Property Definitions
# -------------------------------------------------------------------
class scripts_prop_group_list(PropertyGroup):
    name: bpy.props.StringProperty(name = "filename")
    item: bpy.props.StringProperty(name = "filepath")

class scriptspaths_prop_group_list(PropertyGroup):
    name: bpy.props.StringProperty(name = "foldername")
    item: bpy.props.StringProperty(name = "filepath") 

class RSFF_PropertyGroup(PropertyGroup):
    scripts_list      : bpy.props.CollectionProperty(type = scripts_prop_group_list)
    scriptspaths_list : bpy.props.CollectionProperty(type = scriptspaths_prop_group_list)
    scripts_list_index      : bpy.props.IntProperty(default=0, min=0)
    scriptspaths_list_index : bpy.props.IntProperty(default=0, min=0, update = refresh_scripts_list) # callback
    
# -------------------------------------------------------------------
#   Register
# -------------------------------------------------------------------
classes = (
    RSFF_UL_UIList_Scripts,
    RSFF_UL_UIList_ScriptsPaths,
    scripts_prop_group_list,
    scriptspaths_prop_group_list,
    RSFF_OT_Popup,
    RSFF_OT_refresh_scripts_list,
    RSFF_PropertyGroup,
)

def register():
    for cls in classes: bpy.utils.register_class(cls)
    # UIListScriptsList:
    bpy.types.Scene.RSFF = bpy.props.PointerProperty(type = RSFF_PropertyGroup, description = 'Run Scripts From Folder Addon PropertyGroup')

def unregister():
    for cls in classes: bpy.utils.unregister_class(cls)
# UIList:
    del bpy.types.Scene.RSFF

if __name__ == '__main__': register()
