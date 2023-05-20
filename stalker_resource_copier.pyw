import tkinter, time, os, shutil, webbrowser
from tkinter import filedialog

import xray


VERSION = (0, 0, 4)
DATE = (2021, 7, 26)
GITHUB_REPO_URL = 'https://github.com/PavelBlend/stalker-resource-copier'


def visit_repo_page(event):
    webbrowser.open(GITHUB_REPO_URL)


def copy_file(src, output, missing_files):
    if os.path.exists(src):
        out_dir_name = os.path.dirname(output.lower())
        if not os.path.exists(out_dir_name):
            os.makedirs(out_dir_name)
        shutil.copyfile(src, output.lower())
    else:
        missing_files.add(src)


def read_object_data(data):
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x0902:
            packed_reader = xray.reader.PackedReader(chunk_data)
            packed_reader.getf('<2I')    # file_version and unknown
            reference = packed_reader.gets()
            return reference


def read_scene_objects(data, objects_list):
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x3:    # TOOLS_CHUNK_OBJECTS
            objects_chunked_reader = xray.reader.ChunkedReader(chunk_data)
            for object_chunk_id, object_chunk_data in objects_chunked_reader:
                object_chunked_reader = xray.reader.ChunkedReader(object_chunk_data)
                for object_data_chunk_id, object_data_chunk_data in object_chunked_reader:
                    if object_data_chunk_id == 0x7777:    # TOOLS_CHUNK_OBJECT_DATA
                        reference = read_object_data(object_data_chunk_data)
                        objects_list.add(reference)


def read_level_objects(level_path, objects_list):
    with open(level_path, 'rb') as file:
        data = file.read()
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x8002:    # SCENE_CHUNK_SCENE_OBJECTS
            references = read_scene_objects(chunk_data, objects_list)


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


def read_level_details(details_path, objects_list, textures):
    with open(details_path, 'rb') as file:
        data = file.read()
    chunked_reader = xray.reader.ChunkedReader(data)
    for chunk_id, chunk_data in chunked_reader:
        if chunk_id == 0x800c:    # SCENE_CHUNK_DETAIL_OBJECTS
            det_reader = xray.reader.ChunkedReader(chunk_data)
            for det_obj_chunk_id, det_obj_chunk_data in det_reader:
                if det_obj_chunk_id == 0x0001:    # DETMGR_CHUNK_OBJECTS
                    det_objs_reader = xray.reader.ChunkedReader(det_obj_chunk_data)
                    for det_obj_index, det_obj_data in det_objs_reader:
                        det_obj_chunked_reader = xray.reader.ChunkedReader(det_obj_data)
                        for det_chunk_id, det_chunk_data in det_obj_chunked_reader:
                            if det_chunk_id == 0x0101:    # DETOBJ_CHUNK_REFERENCE
                                det_packed_reader = xray.reader.PackedReader(det_chunk_data)
                                reference_object = det_packed_reader.gets()
                                objects_list.add(reference_object)
                elif det_obj_chunk_id == 0x1002:    # DETMGR_CHUNK_TEXTURE
                    det_tex_reader = xray.reader.PackedReader(det_obj_chunk_data)
                    base_tex = det_tex_reader.gets()
                    textures.add(base_tex)


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


def copy_resource():
    start_time = time.time()
    fs_path = fs_path_ent.get()
    fs_path = fs_path.replace('/', os.sep)
    if not os.path.exists(fs_path):
        error_label.configure(text='ERROR: fs.ltx does not exist!')
        return
    fs = xray.ltx.LtxParser()
    fs.from_file(fs_path)
    fs_dir = os.path.dirname(fs_path)
    out_folder = output_path_ent.get()
    out_folder = out_folder.replace('/', os.sep)
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)
    if os.listdir(out_folder):
        error_label.configure(text='ERROR: Output folder is not empty!')
        return
    level_dir = os.path.join(fs_dir, fs.values['$maps$'])
    missing_files = set()
    output_level_dir = os.path.join(out_folder, fs.values['$maps$'])
    level_name = level_name_var.get()
    if level_name == '-- None --':
        error_label.configure(text='ERROR: Level not selected!')
        return
    level_folder = os.path.join(level_dir, level_name)
    level_main_file_path = os.path.join(level_dir, level_name) + os.extsep + 'level'
    level_main_file_output_path = os.path.join(output_level_dir, level_name) + os.extsep + 'level'
    copy_file(level_main_file_path, level_main_file_output_path, missing_files)
    for level_file in os.listdir(level_folder):
        part_name, part_ext = os.path.splitext(level_file)
        if part_ext == '.part':
            part_src = os.path.join(level_folder, level_file)
            part_out = os.path.join(os.path.join(output_level_dir, level_name), level_file)
            copy_file(part_src, part_out, missing_files)
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
                    read_level_objects(level_path, objects_list)
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
    with open('stalker_resource_copier.log', 'w', encoding='utf-8') as log_file:
        for log_line in log_lines:
            log_file.write(log_line)

    settings_text = '[default_settings]\n'
    settings_text += 'fs_path = "{}"\n'.format(fs_path)
    settings_text += 'out_folder = "{}"\n'.format(out_folder)

    with open(settings_file_name, 'w', encoding='utf-8') as file:
        file.write(settings_text)

    error_label.configure(text='')
    time_label_text = 'total time: {} sec'.format(round(time.time() - start_time, 2))
    timer_label.configure(text=time_label_text)


def set_output():
    dir_path = filedialog.askdirectory()
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
    file_path = filedialog.askopenfilename()
    fs_path_ent.delete(0, last=tkinter.END)
    fs_path_ent.insert(0, file_path)
    add_levels_to_list(file_path)


WINDOW_HEIGHT = 240
WINDOW_WIDTH = 640
BACKGROUND_COLOR = '#808080'
ACTIVE_BACKGROUND_COLOR = '#A0A0A0'
BUTTON_COLOR = '#A0A0A0'
ACTIVE_BUTTON_COLOR = '#B3B3B3'
URL_COLOR = '#00007C'
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
root.title('S.T.A.L.K.E.R. Resource Copier {0}.{1}.{2}'.format(*VERSION))
root['bg'] = BACKGROUND_COLOR
root_pos_x = (root.winfo_screenwidth()) / 2
root_pos_y = (root.winfo_screenheight()) / 2
root.geometry('+%d+%d' % (root_pos_x - WINDOW_WIDTH / 2, root_pos_y - WINDOW_HEIGHT / 2 - 50))

frame = tkinter.Frame(root, bg=BACKGROUND_COLOR, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
# entry
fs_path_ent = tkinter.Entry(frame, width=105, font=ENTRY_FONT, bg=BUTTON_COLOR)
output_path_ent = tkinter.Entry(frame, width=105, font=ENTRY_FONT, bg=BUTTON_COLOR)
# buttons
copy_resource_button = tkinter.Button(
    frame, text=COPY_RES_TEXT, width=BUTTON_WIDTH, height=BUTTON_HEIGHT,
    bg=BUTTON_COLOR, activebackground=ACTIVE_BUTTON_COLOR, font=BUTTON_FONT,
    command=copy_resource
)
open_fs_button = tkinter.Button(frame, text='Open', command=open_fs, bg=BUTTON_COLOR, font=ENTRY_FONT, width=5)
set_output_button = tkinter.Button(frame, text='Set', command=set_output, bg=BUTTON_COLOR, font=ENTRY_FONT, width=5)
# labels
ver_label = tkinter.Label(frame, text='version {0}.{1}.{2}'.format(*VERSION), font=LABEL_FONT, bg=BACKGROUND_COLOR)
date_text = '{}.{:0>2}.{:0>2}'.format(*DATE)
date_label = tkinter.Label(frame, text=date_text, font=LABEL_FONT, bg=BACKGROUND_COLOR)
github_label = tkinter.Label(frame, text=GITHUB_REPO_URL, font=LABEL_FONT, bg=BACKGROUND_COLOR, fg=URL_COLOR, cursor="hand2")
timer_label = tkinter.Label(frame, text='', font=LABEL_FONT, bg=BACKGROUND_COLOR)
error_label = tkinter.Label(frame, text='', font=LABEL_FONT, bg=BACKGROUND_COLOR, fg='#BC0000')
fs_path_label = tkinter.Label(frame, text='fs.ltx', font=LABEL_FONT, bg=BACKGROUND_COLOR)
output_path_label = tkinter.Label(frame, text='output', font=LABEL_FONT, bg=BACKGROUND_COLOR)
level_name_label = tkinter.Label(frame, text='level path', font=LABEL_FONT, bg=BACKGROUND_COLOR)
# menus
level_list = ['-- None --', ]
level_name_var = tkinter.StringVar()
level_name_var.set(level_list[0])
level_list_menu = tkinter.OptionMenu(frame, level_name_var, *level_list)
level_list_menu['menu'].config(font=LABEL_FONT, bg=BACKGROUND_COLOR)
level_list_menu.config(
    font=LABEL_FONT, bg=BACKGROUND_COLOR,
    activebackground=ACTIVE_BACKGROUND_COLOR, width=32
)

frame.grid(row=0,  column=0, pady=10)
cur_row = 0
fs_path_label.grid(row=cur_row,  column=0, padx=10)
fs_path_ent.grid(row=cur_row,  column=1, padx=0)
open_fs_button.grid(row=cur_row,  column=2, padx=0)
cur_row += 1
output_path_label.grid(row=cur_row,  column=0, padx=10)
output_path_ent.grid(row=cur_row,  column=1, padx=0)
set_output_button.grid(row=cur_row,  column=2, padx=0)
cur_row += 1
level_name_label.grid(row=cur_row,  column=0, padx=0)
level_list_menu.grid(row=cur_row,  column=1, padx=0)
cur_row += 1
copy_resource_button.grid(row=cur_row,  column=1, padx=10)
cur_row += 1
ver_label.grid(row=cur_row,  column=1, padx=10)
cur_row += 1
date_label.grid(row=cur_row,  column=1, padx=10)
cur_row += 1
github_label.grid(row=cur_row,  column=1, padx=10)
cur_row += 1
timer_label.grid(row=cur_row,  column=1, padx=10)
cur_row += 1
error_label.grid(row=cur_row,  column=1, padx=10)
cur_row += 1

# bind
github_label.bind('<Button-1>', visit_repo_page)

# settings
settings_file_name = 'stalker_resource_copier.ini'
if os.path.exists(settings_file_name):
    settings_parser = xray.ltx.LtxParser()
    settings_parser.from_file(settings_file_name)
    default_settings = settings_parser.sections.get('default_settings', None)
    if default_settings:
        fs_path_ent.delete(0, last=tkinter.END)
        fs_path_ent.insert(0, default_settings.params['fs_path'])
        add_levels_to_list(default_settings.params['fs_path'])
        output_path_ent.delete(0, last=tkinter.END)
        output_path_ent.insert(0, default_settings.params['out_folder'])
root.mainloop()
