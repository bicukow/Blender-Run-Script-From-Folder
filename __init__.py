bl_info = {
    'name': 'Run Script From Folder',
    'description': 'Quick operator to choose script to be executed from Folder path in preferences -> File Paths -> Script Directories',
    'author': 'bicukov',
    'license': 'GPL',
    'deps': '',
    'version': (0, 0, 1),
    'blender': (4, 3, 0),
    'location': 'Menu Search (F3) -> Run Script From Folder',
    'warning': 'First Folder in File Paths -> Script Drectories will be used for scripts look up',
    'doc_url': 'https://github.com/bicukow/Blender-Run-Script-From-Folder',
    'tracker_url': 'https://github.com/bicukow/Blender-Run-Script-From-Folder/issues',
    'link': '',
    'support': 'COMMUNITY',
    'category': 'User Interface'
    }


import bpy 
from os.path import isfile, join
from os import listdir

#current_dir = bpy.data.filepath.replace(bpy.path.basename(bpy.data.filepath),'')
folder_path = bpy.utils.script_paths_pref()[0]+'\\'

def update_filelist():
    allfiles_list = [f for f in listdir(folder_path) if isfile(join(folder_path, f))]
    files_list = [f for f in allfiles_list if '.py' in f]
    print(files_list)
    return(files_list)

def update_enum_items(files_list):
    enum_items = [('OP' + str(i + 1), item, folder_path) for i, item in enumerate(files_list)]
    print(enum_items)
    return(enum_items) 
  
update_filelist()
update_enum_items(update_filelist())

class RUNSCRIPTFROMFOLDER_OT_PopupMenu(bpy.types.Operator): # enum operator
    bl_label = "Run Script from Folder"
    bl_idname = "wm.run_script_from_folder"
    
    preset_enum : bpy.props.EnumProperty(
        name="execute",
        description='Select a .py script',
        items = update_enum_items(update_filelist()) # dynamic 'items' list for enum operator
    )
    
    def invoke(self, context, event):                # dynamic update filelist on invoke
        wm = context.window_manager
        update_filelist()
        update_enum_items(update_filelist())
        return wm.invoke_props_dialog(self)
       
    def draw(self, context):
        layout = self.layout
        layout.prop(self,'preset_enum')
           
    def execute(self, context):                   # dynamic execute func for enum operator
        files_list = update_filelist()
        for item,i in enumerate(files_list, start=1):
            if self.preset_enum == str('OP' + str(item)):
                filepath = folder_path + i
                # bpy.data.texts.load(filepath)
                exec(compile(open(filepath).read(), filepath, 'exec'))
        
        return {'FINISHED'}    

classes = [RUNSCRIPTFROMFOLDER_OT_PopupMenu]
 
def register():
    for cls in classes:
        bpy.utils.register_class(cls)
 
def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()