import os
import time
import shutil
import webbrowser
import tkinter
import tkinter.filedialog

import xray


VERSION = (0, 0, 4)
DATE = (2021, 7, 26)
GITHUB_REPO_URL = 'https://github.com/PavelBlend/stalker-resource-copier'

FS_PATH_PROP = 'fs_path'
OUT_FOLDER_PROP = 'out_folder'
SETTINGS_FILE_NAME = 'stalker_resource_copier.ini'


def read_object_main(data, textures):
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id in (0x0905, 0x0906, 0x0907):    # surfaces
            reader = xray.reader.PackedReader(chunk_data)
            surfaces_count = reader.getf('<I')[0]
            for surface_index in range(surfaces_count):
                if chunk_id in (0x0906, 0x0907):
                    name = reader.gets()
                    eshader = reader.gets()
                    cshader = reader.gets()
                    if chunk_id == 0x0907:
                        gamemtl = reader.gets()
                    texture = reader.gets()
                    vmap = reader.gets()
                    surface_flags = reader.getf('<I')[0]
                    reader.skip(4 + 4)    # fvf and ?
                else:
                    name = reader.gets()
                    eshader = reader.gets()
                    reader.skip(1)    # flags
                    reader.skip(4 + 4)    # fvf and TCs count
                    texture = reader.gets()
                    vmap = reader.gets()
                textures.add(texture)
        elif chunk_id == 0x0903:    # flags (object type)
            reader = xray.reader.PackedReader(chunk_data)
            flags = reader.getf('I')[0]
    return flags


def get_object_textures(object_path, textures):
    with open(object_path, 'rb') as file:
        data = file.read()
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x7777:    # main
            flags = read_object_main(chunk_data, textures)
            if flags == 0x1:    # multiple usage
                object_type = 'MULIPLE_USAGE'
            else:
                object_type = None
            return object_type


def read_glow_data(data, textures):
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0xc415:
            packed_reader = xray.reader.PackedReader(chunk_data)
            texture = packed_reader.gets()
            textures.add(texture)


def read_glow(data, textures):
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x7777:
            read_glow_data(chunk_data, textures)


def read_glows_objects(data, textures):
    chunked_reader = xray.reader.ChunkedReader(data)
    for glow_index, glow_data in chunked_reader:
        read_glow(glow_data, textures)


def read_glows(data, textures):
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x3:
            read_glows_objects(chunk_data, textures)


def read_level_glows(glows_path, textures):
    with open(glows_path, 'rb') as file:
        data = file.read()
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x8001:
            read_glows(chunk_data, textures)


def read_wallmark_object(data, textures):
    packed_reader = xray.reader.PackedReader(data)
    item_count = packed_reader.getf('<I')[0]
    shader_name = packed_reader.gets()
    tex_name = packed_reader.gets()
    textures.add(tex_name)
    for item_index in range(item_count):
        packed_reader.skip(1)    # flags
        packed_reader.skip(3 * 4 * 2)    # bbox
        packed_reader.skip(3 * 4 + 4)    # bounds
        packed_reader.skip(3 * 4)    # w, h, r
        vertices_count = packed_reader.getf('<I')[0]
        for vert_index in range(vertices_count):
            packed_reader.skip(3 * 4)    # position
            packed_reader.skip(4)    # color
            packed_reader.skip(2 * 4)    # uv


def read_wallmarks_objects(data, textures):
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        read_wallmark_object(chunk_data, textures)


def read_wallmarks(data, textures):
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x0005:
            read_wallmarks_objects(chunk_data, textures)


def read_level_wallmarks(wallmark_path, textures):
    with open(wallmark_path, 'rb') as file:
        data = file.read()
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x800e:
            read_wallmarks(chunk_data, textures)


def copy_textures(
        textures,
        missing_files,
        game_textures_folder,
        raw_textures_folder,
        out_game_tex_folder,
        out_raw_tex_folder
    ):

    textures = list(textures)
    textures.sort()

    for texture in textures:
        # source paths
        game_tex_path = os.path.join(game_textures_folder, texture + os.extsep + 'dds')
        game_thm_path = os.path.join(game_textures_folder, texture + os.extsep + 'thm')
        raw_tex_path = os.path.join(raw_textures_folder, texture + os.extsep + 'tga')
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
            xray.utils.copy_file(src, dist, missing_files)


def save_settings(fs_path, out_folder):
    settings_text = '[default_settings]\n'
    settings_text += '{0} = "{1}"\n'.format(FS_PATH_PROP, fs_path)
    settings_text += '{0} = "{1}"\n'.format(OUT_FOLDER_PROP, out_folder)

    with open(SETTINGS_FILE_NAME, 'w', encoding='utf-8') as file:
        file.write(settings_text)


def copy_resource():
    start_time = time.time()
    fs_path = fs_path_ent.get()
    fs_path = fs_path.replace('/', os.sep)
    if not os.path.exists(fs_path):
        status_label.configure(text='ERROR: fs.ltx does not exist!', bg=ERROR_COLOR)
        return
    fs = xray.ltx.LtxParser()
    fs.from_file(fs_path)
    fs_dir = os.path.dirname(fs_path)
    out_folder = output_path_ent.get()
    out_folder = out_folder.replace('/', os.sep)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    if os.listdir(out_folder):
        status_label.configure(text='ERROR: Output folder is not empty!', bg=ERROR_COLOR)
        return
    level_dir = os.path.join(fs_dir, fs.values['$maps$'])
    missing_files = set()
    output_level_dir = os.path.join(out_folder, fs.values['$maps$'])
    level_name = level_name_var.get()
    if level_name == NONE_LEVEL:
        status_label.configure(text='ERROR: Level not selected!', bg=ERROR_COLOR)
        return
    level_folder = os.path.join(level_dir, level_name)
    level_main_file_path = os.path.join(level_dir, level_name) + os.extsep + 'level'
    level_main_file_output_path = os.path.join(output_level_dir, level_name) + os.extsep + 'level'
    xray.utils.copy_file(level_main_file_path, level_main_file_output_path, missing_files)
    for level_file in os.listdir(level_folder):
        part_name, part_ext = os.path.splitext(level_file)
        if part_ext == '.part':
            part_src = os.path.join(level_folder, level_file)
            part_out = os.path.join(os.path.join(output_level_dir, level_name), level_file)
            xray.utils.copy_file(part_src, part_out, missing_files)
    objects_list = set()
    textures = set()
    if os.path.exists(level_folder):
        for level_file in os.listdir(level_folder):
            if level_file == 'scene_object.part':
                try:
                    # cop
                    objects = xray.ltx.LtxParser()
                    objects.from_file(os.path.join(level_folder, level_file))
                    for section in objects.sections.values():
                        if section.name.startswith('object_'):
                            for param_name, param_value in section.params.items():
                                if param_name == 'reference_name':
                                    objects_list.add(param_value)
                except:
                    # soc
                    level_path = os.path.join(level_folder, level_file)
                    xray.scene_objects.read_scene_objects_part(level_path, objects_list)
            elif level_file == 'detail_object.part':
                details_path = os.path.join(level_folder, level_file)
                read_level_details(details_path, objects_list, textures)
            elif level_file == 'glow.part':
                try:
                    # cop
                    glows = xray.ltx.LtxParser()
                    glows.from_file(os.path.join(level_folder, level_file))
                    for section in glows.sections.values():
                        if section.name.startswith('object_'):
                            for param_name, param_value in section.params.items():
                                if param_name == 'texture_name':
                                    textures.add(param_value)
                except:
                    # soc
                    level_path = os.path.join(level_folder, level_file)
                    read_level_glows(level_path, textures)
            elif level_file == 'wallmark.part':
                wallmark_path = os.path.join(level_folder, level_file)
                read_level_wallmarks(wallmark_path, textures)
    objects_list = list(objects_list)
    objects_list.sort()
    objects_folder = os.path.join(fs_dir, fs.values['$objects$'])
    out_objects_folder = os.path.join(out_folder, fs.values['$objects$'])

    game_textures_folder = os.path.join(fs_dir, fs.values['$game_textures$'])
    raw_textures_folder = os.path.join(fs_dir, fs.values['$textures$'])
    out_game_tex_folder = os.path.join(out_folder, fs.values['$game_textures$'])
    out_raw_tex_folder = os.path.join(out_folder, fs.values['$textures$'])

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
                    xray.utils.copy_file(src, dist, missing_files)
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

    copy_textures(
        textures,
        missing_files,
        game_textures_folder,
        raw_textures_folder,
        out_game_tex_folder,
        out_raw_tex_folder
    )

    xray.utils.write_log(missing_files)
    save_settings(fs_path, out_folder)
    status_label.configure(text='')
    xray.utils.report_total_time(status_label, start_time)


def visit_repo_page(event):
    webbrowser.open(GITHUB_REPO_URL)


def set_output():
    dir_path = tkinter.filedialog.askdirectory()
    if dir_path:
        dir_path = dir_path.replace('\\', os.sep)
        dir_path = dir_path.replace('/', os.sep)
        output_path_ent.delete(0, last=tkinter.END)
        output_path_ent.insert(0, dir_path)


def add_levels_to_list(file_path):
    if file_path and os.path.exists(file_path):
        menu = level_list_menu['menu']
        menu.delete(0, "end")
        fs = xray.ltx.LtxParser()
        fs.from_file(file_path)
        fs_dir = os.path.dirname(file_path)
        maps_dir = os.path.join(fs_dir, fs.values['$maps$'])
        for root, dirs, files in os.walk(maps_dir):
            for level_file in files:
                level_abs_path = os.path.join(root, level_file)
                if os.path.isfile(level_abs_path):
                    level_name, level_ext = os.path.splitext(level_file)
                    level_path = level_abs_path[len(maps_dir) : -len(level_ext)]
                    if level_ext == '.level':
                        menu.add_command(
                            label=level_path,
                            command=lambda value=level_path: level_name_var.set(value)
                        )


def open_fs():
    file_path = tkinter.filedialog.askopenfilename()
    if file_path:
        file_path = file_path.replace('\\', os.sep)
        file_path = file_path.replace('/', os.sep)
        fs_path_ent.delete(0, last=tkinter.END)
        fs_path_ent.insert(0, file_path)
        add_levels_to_list(file_path)


WINDOW_WIDTH = 640
WINDOW_HEIGHT = 240
BACKGROUND_COLOR = '#808080'
ACTIVE_BACKGROUND_COLOR = '#A0A0A0'
BUTTON_COLOR = '#A0A0A0'
ERROR_COLOR = '#BC0000'
ACTIVE_BUTTON_COLOR = '#B3B3B3'
URL_COLOR = '#00007C'
BUTTON_FONT = ('Font', 10, 'bold')
LABEL_FONT = ('Font', 8, 'bold')
ENTRY_FONT = ('Font', 7, 'bold')
COPY_RES_TEXT = 'copy resource'
NONE_LEVEL = '-- none --'
BUTTON_WIDTH = 13
BUTTON_HEIGHT = 1

# root window
root = tkinter.Tk()
root.resizable(height=False, width=False)
root.minsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
root.maxsize(width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
root.title('S.T.A.L.K.E.R. Resource Copier')
root['bg'] = BACKGROUND_COLOR
display_center_x = (root.winfo_screenwidth()) / 2
display_center_y = (root.winfo_screenheight()) / 2
root_pos_x = display_center_x - WINDOW_WIDTH / 2
root_pos_y = display_center_y - WINDOW_HEIGHT / 2 - 50
root.geometry('+%d+%d' % (root_pos_x, root_pos_y))

frame = tkinter.Frame(root, bg=BACKGROUND_COLOR, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
# entry
fs_path_ent = tkinter.Entry(frame, width=105, font=ENTRY_FONT, bg=BUTTON_COLOR)
output_path_ent = tkinter.Entry(frame, width=105, font=ENTRY_FONT, bg=BUTTON_COLOR)
# buttons
copy_resource_button = tkinter.Button(
    frame,
    text=COPY_RES_TEXT,
    width=BUTTON_WIDTH,
    height=BUTTON_HEIGHT,
    bg=BUTTON_COLOR,
    activebackground=ACTIVE_BUTTON_COLOR,
    font=ENTRY_FONT,
    command=copy_resource
)
open_fs_button = tkinter.Button(frame, text='open', command=open_fs, bg=BUTTON_COLOR, font=ENTRY_FONT, width=5)
set_output_button = tkinter.Button(frame, text='set', command=set_output, bg=BUTTON_COLOR, font=ENTRY_FONT, width=5)
# labels
ver_label = tkinter.Label(frame, text='version:    {0}.{1}.{2}'.format(*VERSION), font=LABEL_FONT, bg=xray.const.LABEL_COLOR)
date_text = '{}.{:0>2}.{:0>2}'.format(*DATE)
date_label = tkinter.Label(frame, text=date_text, font=LABEL_FONT, bg=xray.const.LABEL_COLOR)
github_label = tkinter.Label(frame, text=GITHUB_REPO_URL, font=LABEL_FONT, bg=xray.const.LABEL_COLOR, fg=URL_COLOR, cursor="hand2")
status_text_label = tkinter.Label(frame, text='status:', font=LABEL_FONT, bg=xray.const.LABEL_COLOR)
status_label = tkinter.Label(frame, text='', font=LABEL_FONT, bg=xray.const.LABEL_COLOR)
fs_path_label = tkinter.Label(frame, text='fs.ltx:', font=LABEL_FONT, bg=xray.const.LABEL_COLOR)
output_path_label = tkinter.Label(frame, text='output:', font=LABEL_FONT, bg=xray.const.LABEL_COLOR)
mode_label = tkinter.Label(frame, text='mode:', font=LABEL_FONT, bg=xray.const.LABEL_COLOR)
level_name_label = tkinter.Label(frame, text='level:', font=LABEL_FONT, bg=xray.const.LABEL_COLOR)

# mode menu
modes = ['source level', 'game level']
mode_var = tkinter.StringVar()
mode_var.set(modes[0])
mode_menu = tkinter.OptionMenu(frame, mode_var, *modes)
mode_menu['menu'].config(font=LABEL_FONT, bg=BACKGROUND_COLOR)
mode_menu['highlightthickness'] = 0
mode_menu.config(
    font=LABEL_FONT,
    bg=BACKGROUND_COLOR,
    activebackground=ACTIVE_BACKGROUND_COLOR,
    width=32
)

# source files menu
level_list = [NONE_LEVEL, ]
level_name_var = tkinter.StringVar()
level_name_var.set(level_list[0])
level_list_menu = tkinter.OptionMenu(frame, level_name_var, *level_list)
level_list_menu['menu'].config(font=LABEL_FONT, bg=BACKGROUND_COLOR)
level_list_menu['highlightthickness'] = 0
level_list_menu.config(
    font=LABEL_FONT,
    bg=BACKGROUND_COLOR,
    activebackground=ACTIVE_BACKGROUND_COLOR,
    width=32
)

cur_row = 0
frame.grid(row=0, column=0, pady=0)

pad = 5
pad_x_rel = pad / WINDOW_WIDTH
pad_y_rel = pad / WINDOW_HEIGHT

ver_width = 100
ver_x = 1.0 - (ver_width+pad) / WINDOW_WIDTH
ver_height = 20
date_width = 70
ver_label.place(relx=ver_x, rely=pad_y_rel, width=ver_width, height=ver_height)
date_label.place(relx=pad_x_rel, rely=pad_y_rel, width=date_width, height=ver_height)

# fs.ltx
fs_y = (pad*2 + ver_height) / WINDOW_HEIGHT
fs_width = 70
fs_path_label.place(relx=pad_x_rel, rely=fs_y, width=fs_width, height=ver_height)

ent_x = fs_width / WINDOW_WIDTH + pad_x_rel * 2
ent_width = (WINDOW_WIDTH - pad*2 - ver_width) - (fs_width + pad*2)
fs_path_ent.place(relx=ent_x, rely=fs_y, width=ent_width, height=ver_height)

open_fs_button.place(relx=ver_x, rely=fs_y, width=ver_width, height=ver_height+1)

# output
fs_y += (pad + ver_height) / WINDOW_HEIGHT
output_path_label.place(relx=pad_x_rel, rely=fs_y, width=fs_width, height=ver_height)
output_path_ent.place(relx=ent_x, rely=fs_y, width=ent_width, height=ver_height)
set_output_button.place(relx=ver_x, rely=fs_y, width=ver_width, height=ver_height+1)

# mode
fs_y += (pad + ver_height) / WINDOW_HEIGHT
mode_label.place(relx=pad_x_rel, rely=fs_y, width=fs_width, height=ver_height)
mode_width = (WINDOW_WIDTH - pad) - (fs_width + pad*2)
mode_menu.place(relx=ent_x, rely=fs_y, width=mode_width, height=ver_height)

# level
fs_y += (pad + ver_height) / WINDOW_HEIGHT
level_name_label.place(relx=pad_x_rel, rely=fs_y, width=fs_width, height=ver_height)
level_width = (WINDOW_WIDTH - pad) - (fs_width + pad*2)
level_list_menu.place(relx=ent_x, rely=fs_y, width=level_width, height=ver_height)
fs_y += (pad + ver_height) / WINDOW_HEIGHT

github_label.place(relx=ent_x, rely=pad_y_rel, width=ent_width, height=ver_height)

status_text_label.place(relx=pad_x_rel, rely=fs_y, width=fs_width, height=ver_height)
status_label.place(relx=ent_x, rely=fs_y, width=ent_width, height=ver_height)

copy_resource_button.place(relx=ver_x, rely=fs_y, width=ver_width, height=ver_height)

# bind
github_label.bind('<Button-1>', visit_repo_page)

# settings
if os.path.exists(SETTINGS_FILE_NAME):
    settings_parser = xray.ltx.LtxParser()
    settings_parser.from_file(SETTINGS_FILE_NAME)
    default_settings = settings_parser.sections.get('default_settings', None)

    if default_settings:
        fs_path = default_settings.params[FS_PATH_PROP]
        fs_path = fs_path.replace('\\', os.sep)
        fs_path = fs_path.replace('/', os.sep)
        fs_path_ent.delete(0, last=tkinter.END)
        fs_path_ent.insert(0, fs_path)

        out_path = default_settings.params[OUT_FOLDER_PROP]
        out_path = out_path.replace('\\', os.sep)
        out_path = out_path.replace('/', os.sep)
        output_path_ent.delete(0, last=tkinter.END)
        output_path_ent.insert(0, out_path)

        add_levels_to_list(default_settings.params[FS_PATH_PROP])

root.mainloop()
