import tkinter
from tkinter import filedialog
import os
import shutil

from xray import xray_ltx
from xray import xray_io


def copy_file(src, output, missing_files):
    if os.path.exists(src):
        out_dir_name = os.path.dirname(output)
        if not os.path.exists(out_dir_name):
            os.makedirs(out_dir_name)
        shutil.copyfile(src, output)
    else:
        missing_files.add(src)


def read_object_main(data, textures):
    chunked_reader = xray_io.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x0907:    # surfaces
            reader = xray_io.PackedReader(chunk_data)
            surfaces_count = reader.int()
            for surface_index in range(surfaces_count):
                name = reader.gets()
                eshader = reader.gets()
                cshader = reader.gets()
                gamemtl = reader.gets()
                texture = reader.gets()
                vmap = reader.gets()
                surface_flags = reader.int()
                reader.skip(4 + 4)    # fvf and ?
                textures.add(texture)
        elif chunk_id == 0x0903:    # flags (object type)
            reader = xray_io.PackedReader(chunk_data)
            flags = reader.getf('I')[0]
    return flags


def get_object_textures(object_path, textures):
    with open(object_path, 'rb') as file:
        data = file.read()
    chunked_reader = xray_io.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x7777:    # main
            flags = read_object_main(chunk_data, textures)
            if flags == 0x1:    # multiple usage
                object_type = 'MULIPLE_USAGE'
            else:
                object_type = None
            return object_type


def copy_resource():
    fs_path = fs_path_ent.get()
    fs_path = fs_path.replace('/', os.sep)
    fs = xray_ltx.StalkerLtxParser(fs_path)
    level_dir = fs.values['$maps$']
    level_name = level_name_var.get()
    level_folder = os.path.join(level_dir, level_name)
    objects_list = set()
    if os.path.exists(level_folder):
        for level_file in os.listdir(level_folder):
            if level_file == 'scene_object.part':
                objects = xray_ltx.StalkerLtxParser(os.path.join(level_folder, level_file))
                for section in objects.sections.values():
                    if section.name.startswith('object_'):
                        for param_name, param_value in section.params.items():
                            if param_name == 'reference_name':
                                objects_list.add(param_value)
    objects_list = list(objects_list)
    objects_list.sort()
    objects_folder = fs.values['$objects$']
    out_folder = output_path_ent.get()
    out_folder = out_folder.replace('/', os.sep)
    out_objects_folder = os.path.join(out_folder, 'rawdata', 'objects')
    textures = set()
    missing_files = set()

    game_textures_folder = fs.values['$game_textures$']
    raw_textures_folder = fs.values['$textures$']
    out_game_tex_folder = os.path.join(out_folder, 'gamedata', 'textures')
    out_raw_tex_folder = os.path.join(out_folder, 'rawdata', 'textures')

    if not os.path.exists(out_objects_folder):
        os.makedirs(out_objects_folder)

    for object_name in objects_list:

        # OBJECT
        object_path = os.path.join(objects_folder, object_name + os.extsep + 'object')
        if os.path.exists(object_path):
            out_object_path = os.path.join(out_objects_folder, object_name + os.extsep + 'object')
            object_dir = os.path.dirname(out_object_path)
            if not os.path.exists(object_dir):
                os.makedirs(object_dir)
            shutil.copyfile(object_path, out_object_path)
            object_type = get_object_textures(object_path, textures)
            if object_type == 'MULIPLE_USAGE':
                lod_tex_path = 'lod' + os.sep + 'lod_' + object_name.replace(os.sep, '_')
                # source paths
                game_tex_path = os.path.join(game_textures_folder, lod_tex_path + os.extsep + 'dds')
                raw_tex_path = os.path.join(raw_textures_folder, lod_tex_path + os.extsep + 'tga')
                game_thm_path = os.path.join(game_textures_folder, lod_tex_path + os.extsep + 'thm')
                raw_thm_path = os.path.join(raw_textures_folder, lod_tex_path + os.extsep + 'thm')
                # output paths
                out_game_tex_path = os.path.join(out_game_tex_folder, lod_tex_path + os.extsep + 'dds')
                out_raw_tex_path = os.path.join(out_raw_tex_folder, lod_tex_path + os.extsep + 'tga')
                out_thm_path = os.path.join(out_game_tex_folder, lod_tex_path + os.extsep + 'thm')
                texs = [
                    [game_tex_path, out_game_tex_path],
                    [raw_tex_path, out_raw_tex_path],
                    [game_thm_path, out_thm_path],
                    [raw_thm_path, out_thm_path]
                ]
                for src, dist in texs:
                    copy_file(src, dist, missing_files)
        else:
            missing_files.add(object_path)

        # THM
        thm_path = os.path.join(objects_folder, object_name + os.extsep + 'thm')
        if os.path.exists(thm_path):
            out_thm_path = os.path.join(out_objects_folder, object_name + os.extsep + 'thm')
            thm_dir = os.path.dirname(out_thm_path)
            if not os.path.exists(thm_dir):
                os.makedirs(thm_dir)
            shutil.copyfile(thm_path, out_thm_path)
        else:
            missing_files.add(thm_path)

    textures = list(textures)
    textures.sort()

    for texture in textures:
        # source paths
        game_tex_path = os.path.join(game_textures_folder, texture + os.extsep + 'dds')
        raw_tex_path = os.path.join(raw_textures_folder, texture + os.extsep + 'tga')
        game_thm_path = os.path.join(game_textures_folder, texture + os.extsep + 'thm')
        raw_thm_path = os.path.join(raw_textures_folder, texture + os.extsep + 'thm')
        # output paths
        out_game_tex_path = os.path.join(out_game_tex_folder, texture + os.extsep + 'dds')
        out_raw_tex_path = os.path.join(out_raw_tex_folder, texture + os.extsep + 'tga')
        out_thm_path = os.path.join(out_game_tex_folder, texture + os.extsep + 'thm')
        texs = [
            [game_tex_path, out_game_tex_path],
            [raw_tex_path, out_raw_tex_path],
            [game_thm_path, out_thm_path],
            [raw_thm_path, out_thm_path]
        ]
        for src, dist in texs:
            copy_file(src, dist, missing_files)

    missing_files = list(missing_files)
    missing_files.sort()
    log_lines = []
    if len(missing_files):
        log_lines.append('These files are not copied because they are missing:\n\n')
        for file in missing_files:
            log_lines.append('{}\n'.format(file))
    else:
        log_lines.append('All files are copied.')
    with open('stalker_resource_copier.log', 'w') as log_file:
        for log_line in log_lines:
            log_file.write(log_line)


def set_output():
    dir_path = filedialog.askdirectory()
    output_path_ent.delete(0, last=tkinter.END)
    output_path_ent.insert(0, dir_path)


def open_fs():
    file_path = filedialog.askopenfilename()
    fs_path_ent.delete(0, last=tkinter.END)
    fs_path_ent.insert(0, file_path)
    menu = level_list_menu['menu']
    menu.delete(0, "end")
    if file_path:
        fs = xray_ltx.StalkerLtxParser(file_path)
        level_dir = fs.values['$maps$']
        for level_file in os.listdir(level_dir):
            if os.path.isfile(os.path.join(level_dir, level_file)):
                level_name, level_ext = os.path.splitext(level_file)
                if level_ext == '.level':
                    menu.add_command(
                        label=level_name,
                        command=lambda value=level_name: level_name_var.set(value)
                    )


WINDOW_HEIGHT = 240
WINDOW_WIDTH = 640
BACKGROUND_COLOR = '#808080'
ACTIVE_BACKGROUND_COLOR = '#A0A0A0'
BUTTON_COLOR = '#A0A0A0'
ACTIVE_BUTTON_COLOR = '#B3B3B3'
BUTTON_FONT = ('Font', 10, 'bold')
LABEL_FONT = ('Font', 8, 'bold')
ENTRY_FONT = ('Font', 7, 'bold')
COPY_RES_TEXT = 'Copy Resource'
BUTTON_WIDTH = 13
BUTTON_HEIGHT = 1

# root window
root = tkinter.Tk()
root.resizable(height=False, width=False)
root.minsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
root.maxsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
root.title('S.T.A.L.K.E.R. Resource Copier')
root['bg'] = BACKGROUND_COLOR
root_pos_x = (root.winfo_screenwidth()) / 2
root_pos_y = (root.winfo_screenheight()) / 2
root.geometry('+%d+%d' % (root_pos_x - WINDOW_WIDTH / 2, root_pos_y - WINDOW_HEIGHT / 2 - 50))

frame = tkinter.Frame(root, bg=BACKGROUND_COLOR, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
# entry
fs_path_ent = tkinter.Entry(frame, width=100, font=ENTRY_FONT, bg=BUTTON_COLOR)
output_path_ent = tkinter.Entry(frame, width=100, font=ENTRY_FONT, bg=BUTTON_COLOR)
# buttons
copy_resource_button = tkinter.Button(
    frame, text=COPY_RES_TEXT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
    bg=BUTTON_COLOR, activebackground=ACTIVE_BUTTON_COLOR, font=BUTTON_FONT,
    command=copy_resource
)
open_fs_button = tkinter.Button(frame, text='Open', command=open_fs, bg=BUTTON_COLOR, font=ENTRY_FONT, width=5)
set_output_button = tkinter.Button(frame, text='Set', command=set_output, bg=BUTTON_COLOR, font=ENTRY_FONT, width=5)
# labels
ver_label = tkinter.Label(frame, text='version 0.0.1', font=LABEL_FONT, bg=BACKGROUND_COLOR)
date_label = tkinter.Label(frame, text='21.10.2019', font=LABEL_FONT, bg=BACKGROUND_COLOR)
timer_label = tkinter.Label(frame, text='', font=LABEL_FONT, bg=BACKGROUND_COLOR)
fs_path_label = tkinter.Label(frame, text='fs.ltx', font=LABEL_FONT, bg=BACKGROUND_COLOR)
output_path_label = tkinter.Label(frame, text='output', font=LABEL_FONT, bg=BACKGROUND_COLOR)
level_name_label = tkinter.Label(frame, text='level', font=LABEL_FONT, bg=BACKGROUND_COLOR)
# menu
level_list = ['-- None --', ]
level_name_var = tkinter.StringVar()
level_name_var.set(level_list[0])
level_list_menu = tkinter.OptionMenu(frame, level_name_var, *level_list)
level_list_menu['menu'].config(font=LABEL_FONT, bg=BACKGROUND_COLOR)
level_list_menu.config(
    font=LABEL_FONT, bg=BACKGROUND_COLOR,
    activebackground=ACTIVE_BACKGROUND_COLOR
)

frame.grid(row=0,  column=0, pady=10)
ver_label.grid(row=0,  column=1, padx=10)
date_label.grid(row=1,  column=1, padx=10)
timer_label.grid(row=2,  column=1, padx=10)
fs_path_label.grid(row=3,  column=0, padx=10)
fs_path_ent.grid(row=3,  column=1, padx=0)
open_fs_button.grid(row=3,  column=2, padx=0)
output_path_label.grid(row=4,  column=0, padx=10)
output_path_ent.grid(row=4,  column=1, padx=0)
set_output_button.grid(row=4,  column=2, padx=0)
level_name_label.grid(row=5,  column=0, padx=0)
level_list_menu.grid(row=5,  column=1, padx=0)
copy_resource_button.grid(row=6,  column=1, padx=10)

root.mainloop()
