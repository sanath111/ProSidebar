import bpy
import os, sys, inspect
from ..bp_lib.xml import BlenderProXML
import xml.etree.ElementTree as ET
from importlib import import_module

DEFAULT_LIBRARY_ROOT_FOLDER = os.path.join(bpy.utils.user_resource('SCRIPTS'), "creative_designer")
SCRIPT_FOLDER = os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,"scripts")
OBJECT_FOLDER = os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,"objects")
COLLECTION_FOLDER = os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,"collections")
MATERIAL_FOLDER = os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,"materials")
WORLD_FOLDER = os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,"worlds")
LIBRARY_FOLDER = os.path.join(os.path.dirname(__file__),"data")
LIBRARY_PATH_FILENAME = "creative_designer_paths.xml"

def get_wm_props():
    wm = bpy.context.window_manager
    return wm.bp_lib

def get_scene_props():
    scene = bpy.context.scene
    return scene.bp_props    

def get_thumbnail_file_path():
    return os.path.join(os.path.dirname(__file__),"thumbnail.blend")

def get_library_path_file():
    """ Returns the path to the file that stores all of the library paths.
    """
    # path = os.path.join(bpy.utils.user_resource('SCRIPTS'), "creative_designer")

    if not os.path.exists(DEFAULT_LIBRARY_ROOT_FOLDER):
        os.makedirs(DEFAULT_LIBRARY_ROOT_FOLDER)
        
    return os.path.join(DEFAULT_LIBRARY_ROOT_FOLDER,LIBRARY_PATH_FILENAME)

def get_script_libraries():
    wm_props = get_wm_props()

    # Store all library paths
    library_paths = []

    # Search for internal library paths
    file_path = os.path.dirname(__file__)
    path, folder = os.path.split(file_path)
    internal_library_path = os.path.join(path,'libraries')
    folders = os.listdir(internal_library_path)
    for folder in folders:
        lib_path = os.path.join(internal_library_path,folder)
        if os.path.isdir(lib_path):
            library_paths.append(lib_path)

    #This is being run multiple times on debug startup so remove all items first
    for item in wm_props.script_libraries:
        wm_props.script_libraries.remove(0)

    #Load all Libraries
    for path in library_paths:
        print('Loading Library: ',path)
        if os.path.exists(path):
            files = os.listdir(path)
            for file in files:
                if file == '__init__.py':
                    path, folder_name = os.path.split(os.path.normpath(path))
                    sys.path.append(path)
                    pkg = import_module(folder_name)
                    lib = wm_props.script_libraries.add()
                    lib.name = folder_name
                    for mod_name, mod in inspect.getmembers(pkg):
                        if mod_name == 'LIBRARY_PATH':
                            lib.library_path = mod
                        if mod_name == 'PANEL_ID':
                            lib.panel_id = mod
                        if mod_name[:2] != "__": #No need to go through built in modules
                            for name, obj in inspect.getmembers(mod):
                                if hasattr(obj,'show_in_library') and name != 'ops' and obj.show_in_library:
                                    item = lib.library_items.add()
                                    item.package_name = folder_name
                                    item.module_name = mod_name
                                    item.class_name = name
                                    item.name = name

def get_active_script_library():
    scene_props = get_scene_props()
    wm_props = get_wm_props()
    if scene_props.active_script_library in wm_props.script_libraries:
        return wm_props.script_libraries[scene_props.active_script_library]
    else:
        return wm_props.script_libraries[0]

def get_active_category(scene_props,folders):
    """ Gets the active folder for the active library
    """
    if scene_props.library_tabs == 'SCRIPT':
        if scene_props.active_script_category in folders:
            for folder in folders:
                if scene_props.active_script_category == folder:
                    return folder
    if scene_props.library_tabs == 'OBJECT':
        if scene_props.active_object_library in folders:
            for folder in folders:
                if scene_props.active_object_library == folder:
                    return folder
    if scene_props.library_tabs == 'COLLECTION':
        if scene_props.active_collection_library in folders:
            for folder in folders:
                if scene_props.active_collection_library == folder:
                    return folder
    if scene_props.library_tabs == 'MATERIAL':
        if scene_props.active_material_library in folders:
            for folder in folders:
                if scene_props.active_material_library == folder:
                    return folder                 
    if scene_props.library_tabs == 'WORLD':
        if scene_props.active_world_library in folders:
            for folder in folders:
                if scene_props.active_world_library == folder:
                    return folder   
    if len(folders) > 0:
        return folders[0]

def get_active_categories(library_tabs):
    """ Gets a list of all of the categories
    """
    path = get_active_library_path(library_tabs)
    folders = []
    if path and os.path.exists(path):
        for fn in os.listdir(path):
            if os.path.isdir(os.path.join(path,fn)):
                folders.append(fn)    
    return folders

def get_active_library_path(library_tabs):
    if library_tabs == 'SCRIPT':
        lib = get_active_script_library()  
        return lib.library_path      
    if library_tabs == 'OBJECT':
        return get_object_library_path()
    if library_tabs == 'COLLECTION':
        return get_collection_library_path()
    if library_tabs == 'MATERIAL':
        return get_material_library_path()
    if library_tabs == 'WORLD':
        return get_world_library_path()

def get_script_library_path():
    props = get_wm_props()
    if os.path.exists(props.script_library_path):
        return props.script_library_path
    else:
        return SCRIPT_FOLDER

def get_object_library_path():
    props = get_wm_props()
    if os.path.exists(props.object_library_path):
        return props.object_library_path
    else:
        return OBJECT_FOLDER

def get_collection_library_path():
    props = get_wm_props()
    if os.path.exists(props.collection_library_path):
        return props.collection_library_path
    else:
        return COLLECTION_FOLDER

def get_material_library_path():
    props = get_wm_props()
    if os.path.exists(props.material_library_path):
        return props.material_library_path
    else:
        return MATERIAL_FOLDER                

def get_world_library_path():
    props = get_wm_props()
    if os.path.exists(props.world_library_path):
        return props.world_library_path
    else:
        return WORLD_FOLDER   

def update_file_browser_path(context,path):
    for area in context.screen.areas:
        if area.type == 'FILE_BROWSER':
            for space in area.spaces:
                if space.type == 'FILE_BROWSER':
                    params = space.params
                    params.directory = str.encode(path)
                    if not context.screen.show_fullscreen:
                        params.use_filter = True
                        params.display_type = 'THUMBNAIL'
                        params.use_filter_movie = False
                        params.use_filter_script = False
                        params.use_filter_sound = False
                        params.use_filter_text = False
                        params.use_filter_font = False
                        params.use_filter_folder = False
                        params.use_filter_blender = False
                        params.use_filter_image = True

def get_folder_enum_previews(path,key):
    """ Returns: ImagePreviewCollection
        Par1: path - The path to collect the folders from
        Par2: key - The dictionary key the previews will be stored in
    """
    enum_items = []
    if len(key.my_previews) > 0:
        return key.my_previews
    
    if path and os.path.exists(path):
        folders = []
        for fn in os.listdir(path):
            if os.path.isdir(os.path.join(path,fn)):
                folders.append(fn)

        for i, name in enumerate(folders):
            filepath = os.path.join(path, name)
            thumb = key.load(filepath, "", 'IMAGE')
            filename, ext = os.path.splitext(name)
            enum_items.append((filename, filename, filename, thumb.icon_id, i))
    
    key.my_previews = enum_items
    key.my_previews_dir = path
    return key.my_previews

def get_image_enum_previews(path,key,force_reload=False):
    """ Returns: ImagePreviewCollection
        Par1: path - The path to collect the images from
        Par2: key - The dictionary key the previews will be stored in
    """
    enum_items = []
    if len(key.my_previews) > 0:
        return key.my_previews
    
    if path and os.path.exists(path):
        image_paths = []
        for fn in os.listdir(path):
            if fn.lower().endswith(".png"):
                image_paths.append(fn)

        for i, name in enumerate(image_paths):
            filepath = os.path.join(path, name)
            thumb = key.load(filepath, filepath, 'IMAGE',force_reload)
            filename, ext = os.path.splitext(name)
            enum_items.append((filename, filename, filename, thumb.icon_id, i))
    
    key.my_previews = enum_items
    key.my_previews_dir = path
    return key.my_previews

def create_image_preview_collection():
    import bpy.utils.previews
    col = bpy.utils.previews.new()
    col.my_previews_dir = ""
    col.my_previews = ()
    return col

def write_xml_file():
    '''
    This writes the XML file from the current props. 
    This file gets written everytime a property changes.
    '''
    xml = BlenderProXML()
    root = xml.create_tree()
    paths = xml.add_element(root,'LibraryPaths')
    
    wm = bpy.context.window_manager
    wm_props = wm.bp_lib
    
    if os.path.exists(wm_props.object_library_path):
        xml.add_element_with_text(paths,'Objects',wm_props.object_library_path)
    else:
        xml.add_element_with_text(paths,'Objects',"")
        
    if os.path.exists(wm_props.material_library_path):
        xml.add_element_with_text(paths,'Materials',wm_props.material_library_path)
    else:
        xml.add_element_with_text(paths,'Materials',"")
        
    if os.path.exists(wm_props.collection_library_path):
        xml.add_element_with_text(paths,'Collections',wm_props.collection_library_path)
    else:
        xml.add_element_with_text(paths,'Collections',"")
    
    if os.path.exists(wm_props.world_library_path):
        xml.add_element_with_text(paths,'Worlds',wm_props.world_library_path)
    else:
        xml.add_element_with_text(paths,'Worlds',"")

    if os.path.exists(wm_props.script_library_path):
        xml.add_element_with_text(paths,'Scripts',wm_props.script_library_path)
    else:
        xml.add_element_with_text(paths,'Scripts',"")

    xml.write(get_library_path_file())

def update_props_from_xml_file():
    '''
    This gets read on startup and sets the window manager props
    '''
    wm_props = get_wm_props()
    if os.path.exists(get_library_path_file()):
        tree = ET.parse(get_library_path_file())
        root = tree.getroot()
        for elm in root.findall("LibraryPaths"):
            items = elm.getchildren()
            for item in items:
                
                if item.tag == 'Objects':
                    if os.path.exists(str(item.text)):
                        wm_props.object_library_path = item.text
                    else:
                        wm_props.object_library_path = ""
                        
                if item.tag == 'Materials':
                    if os.path.exists(str(item.text)):
                        wm_props.material_library_path = item.text
                    else:
                        wm_props.material_library_path = ""
                        
                if item.tag == 'Collections':
                    if os.path.exists(str(item.text)):
                        wm_props.collection_library_path = item.text
                    else:
                        wm_props.collection_library_path = "" 

                if item.tag == 'Worlds':
                    if os.path.exists(str(item.text)):
                        wm_props.world_library_path = item.text
                    else:
                        wm_props.world_library_path = "" 

                if item.tag == 'Scripts':
                    if os.path.exists(str(item.text)):
                        wm_props.script_library_path = item.text
                    else:
                        wm_props.script_library_path = "" 
