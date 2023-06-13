import os
import time
import shutil
import webbrowser
import tkinter
import tkinter.filedialog

import xray


VERSION = (1, 1, 0)
DATE = (2023, 5, 21)


def copy_resource():
    mode = mode_var.get()

    start_time = time.time()

    fs_path = fs_path_ent.get()
    fs_path = fs_path.replace('/', os.sep)
    fs_path = fs_path.replace('\\', os.sep)

    if not os.path.exists(fs_path):
        status_label.configure(
            text='ERROR: fs.ltx does not exist!',
            bg=ERROR_COLOR
        )
        return

    fs = xray.ltx.LtxParser()
    fs.from_file(fs_path)
    fs_dir = os.path.dirname(fs_path)

    out_folder = output_path_ent.get()
    out_folder = out_folder.replace('/', os.sep)
    out_folder = out_folder.replace('\\', os.sep)

    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    if os.listdir(out_folder):
        status_label.configure(
            text='ERROR: Output folder is not empty!',
            bg=ERROR_COLOR
        )
        return

    # collect objects and textures
    objects = set()
    textures = set()
    sounds = set()
    missing_files = set()

    if mode == 'source level':
        maps_dir = os.path.join(fs_dir, fs.values['$maps$'])
        output_level_dir = os.path.join(out_folder, fs.values['$maps$'])
        level_name = level_name_var.get()
        level_name = level_name.replace('/', os.sep)
        level_name = level_name.replace('\\', os.sep)

        groups_dir = os.path.join(fs_dir, fs.values['$groups$'])

        if level_name == NONE_LEVEL:
            status_label.configure(
                text='ERROR: Level not selected!',
                bg=ERROR_COLOR
            )
            return

        level_folder = os.path.join(maps_dir, level_name)

        if os.path.exists(level_folder):
            for level_file in os.listdir(level_folder):
                file_path = os.path.join(level_folder, level_file)

                if level_file == 'scene_object.part':
                    xray.scene_objects.read_scene_objects_part(file_path, objects)

                elif level_file == 'detail_object.part':
                    xray.scene_details.read_level_details(file_path, objects, textures)

                elif level_file == 'glow.part':
                    xray.scene_glows.read_level_glows(file_path, textures)

                elif level_file == 'wallmark.part':
                    xray.scene_wallmarks.read_level_wallmarks(file_path, textures)

                elif level_file == 'sound_src.part':
                    xray.scene_sound_source.read_sound_sources(file_path, sounds)

                elif level_file == 'group.part':
                    xray.scene_groups.read_level_groups(file_path, objects, groups_dir)

        else:
            status_label.configure(
                text='ERROR: level folder not found: "{}"'.format(level_name),
                bg=ERROR_COLOR
            )
            return

    else:
        # game level
        file_path = game_level_file.get()
        file_path = file_path.replace('/', os.sep)
        file_path = file_path.replace('\\', os.sep)

        if not file_path:
            status_label.configure(
                text='ERROR: Level file not specified!',
                bg=ERROR_COLOR
            )
            return

        if os.path.exists(file_path):

            if os.path.isfile(file_path):
                xray.game_level.read_game_level_textures(file_path, textures)
            else:
                status_label.configure(
                    text='ERROR: Level file not exists!',
                    bg=ERROR_COLOR
                )
                return

        else:
            status_label.configure(
                text='ERROR: Level file not exists!',
                bg=ERROR_COLOR
            )
            return

    objects = list(objects)
    objects.sort()

    objects_folder = os.path.join(fs_dir, fs.values['$objects$'])
    out_objects_folder = os.path.join(out_folder, fs.values['$objects$'])

    game_tex_folder = os.path.join(fs_dir, fs.values['$game_textures$'])
    out_game_tex_folder = os.path.join(out_folder, fs.values['$game_textures$'])

    raw_tex_folder = os.path.join(fs_dir, fs.values['$textures$'])
    out_raw_tex_folder = os.path.join(out_folder, fs.values['$textures$'])

    if objects:
        if not os.path.exists(out_objects_folder):
            os.makedirs(out_objects_folder)

        # copy *.object and *.thm for objects
        for object_name in objects:

            # *.object
            object_path = os.path.join(objects_folder, object_name + os.extsep + 'object')
            if os.path.exists(object_path):
                out_object_path = os.path.join(out_objects_folder, object_name + os.extsep + 'object')
                object_dir = os.path.dirname(out_object_path)
                if not os.path.exists(object_dir):
                    os.makedirs(object_dir)
                shutil.copyfile(object_path, out_object_path)
                object_type = xray.object_format.get_object_textures(object_path, textures)

                # copy lod textures
                if object_type == 'MULIPLE_USAGE':
                    lod_tex_path = 'lod' + os.sep + 'lod_' + object_name.replace(os.sep, '_')
                    # source paths
                    game_tex_path = os.path.join(game_tex_folder, lod_tex_path + os.extsep + 'dds')
                    raw_tex_path = os.path.join(raw_tex_folder, lod_tex_path + os.extsep + 'tga')
                    game_thm_path = os.path.join(game_tex_folder, lod_tex_path + os.extsep + 'thm')
                    raw_thm_path = os.path.join(raw_tex_folder, lod_tex_path + os.extsep + 'thm')
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

            # *.thm
            thm_path = os.path.join(objects_folder, object_name + os.extsep + 'thm')
            if os.path.exists(thm_path):
                out_thm_path = os.path.join(out_objects_folder, object_name + os.extsep + 'thm')
                thm_dir = os.path.dirname(out_thm_path)
                if not os.path.exists(thm_dir):
                    os.makedirs(thm_dir)
                shutil.copyfile(thm_path, out_thm_path)
            else:
                missing_files.add(thm_path)

    # copy textures *.dds, *.tga, *.thm
    xray.utils.copy_files(
        textures,
        missing_files,
        game_tex_folder,
        raw_tex_folder,
        out_game_tex_folder,
        out_raw_tex_folder,
        'dds',
        'tga'
    )

    # copy sounds *.ogg, *.wav, *.thm
    game_sounds_folder = os.path.join(fs_dir, fs.values['$game_sounds$'])
    out_game_sounds_folder = os.path.join(out_folder, fs.values['$game_sounds$'])

    raw_sounds_folder = os.path.join(fs_dir, fs.values['$sounds$'])
    out_raw_sounds_folder = os.path.join(out_folder, fs.values['$sounds$'])

    xray.utils.copy_files(
        sounds,
        missing_files,
        game_sounds_folder,
        raw_sounds_folder,
        out_game_sounds_folder,
        out_raw_sounds_folder,
        'ogg',
        'wav'
    )

    if mode == 'source level':
        # copy *.level file
        level_main_file_path = os.path.join(maps_dir, level_name) + os.extsep + 'level'
        level_main_file_output_path = os.path.join(output_level_dir, level_name) + os.extsep + 'level'
        xray.utils.copy_file(level_main_file_path, level_main_file_output_path, missing_files)

        # copy *.part files
        for level_file in os.listdir(level_folder):
            part_name, part_ext = os.path.splitext(level_file)
            if part_ext == '.part':
                part_src = os.path.join(level_folder, level_file)
                part_out = os.path.join(os.path.join(output_level_dir, level_name), level_file)
                xray.utils.copy_file(part_src, part_out, missing_files)

    # report
    xray.utils.write_log(missing_files)
    xray.utils.save_settings(fs_path, out_folder)
    xray.utils.report_total_time(status_label, start_time)


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


def open_game_level():
    file_path = tkinter.filedialog.askopenfilename()
    if file_path:
        file_path = file_path.replace('\\', os.sep)
        file_path = file_path.replace('/', os.sep)
        game_level_file.delete(0, last=tkinter.END)
        game_level_file.insert(0, file_path)


def change_mode(event):
    if mode_var.get() == 'source level':
        game_level_file.place_forget()
        open_game_level_button.place_forget()
        level_list_menu.place(relx=file_x, rely=file_y, width=level_width, height=ver_height)
    else:
        level_list_menu.place_forget()
        game_level_file.place(relx=file_x, rely=file_y, width=ent_width, height=ver_height)
        open_game_level_button.place(relx=ver_x, rely=open_level_y, width=ver_width, height=ver_height+1)


WINDOW_WIDTH = 640
WINDOW_HEIGHT = 154
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
open_fs_button = tkinter.Button(frame, text='set', command=open_fs, bg=BUTTON_COLOR, font=ENTRY_FONT, width=5)
set_output_button = tkinter.Button(frame, text='set', command=set_output, bg=BUTTON_COLOR, font=ENTRY_FONT, width=5)
# labels
ver_label = tkinter.Label(frame, text='version:    {0}.{1}.{2}'.format(*VERSION), font=LABEL_FONT, bg=xray.const.LABEL_COLOR)
date_text = '{}.{:0>2}.{:0>2}'.format(*DATE)
date_label = tkinter.Label(frame, text=date_text, font=LABEL_FONT, bg=xray.const.LABEL_COLOR)
github_label = tkinter.Label(frame, text=xray.const.GITHUB_REPO_URL, font=LABEL_FONT, bg=xray.const.LABEL_COLOR, fg=URL_COLOR, cursor="hand2")
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
mode_menu = tkinter.OptionMenu(frame, mode_var, *modes, command=change_mode)
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

game_level_file = tkinter.Entry(frame, width=105, font=ENTRY_FONT, bg=BUTTON_COLOR)
open_game_level_button = tkinter.Button(frame, text='set', command=open_game_level, bg=BUTTON_COLOR, font=ENTRY_FONT, width=5)

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

file_x = ent_x
file_y = fs_y
open_level_y = fs_y

change_mode(None)

fs_y += (pad + ver_height) / WINDOW_HEIGHT

github_label.place(relx=ent_x, rely=pad_y_rel, width=ent_width, height=ver_height)

status_text_label.place(relx=pad_x_rel, rely=fs_y, width=fs_width, height=ver_height)
status_label.place(relx=ent_x, rely=fs_y, width=ent_width, height=ver_height)

copy_resource_button.place(relx=ver_x, rely=fs_y, width=ver_width, height=ver_height)

# bind
github_label.bind('<Button-1>', xray.utils.visit_repo_page)

# settings
if os.path.exists(xray.const.SETTINGS_FILE_NAME):
    settings_parser = xray.ltx.LtxParser()
    settings_parser.from_file(xray.const.SETTINGS_FILE_NAME)
    default_settings = settings_parser.sections.get('default_settings', None)

    if default_settings:
        fs_path = default_settings.params[xray.const.FS_PATH_PROP]
        fs_path = fs_path.replace('\\', os.sep)
        fs_path = fs_path.replace('/', os.sep)
        fs_path_ent.delete(0, last=tkinter.END)
        fs_path_ent.insert(0, fs_path)

        out_path = default_settings.params[xray.const.OUT_FOLDER_PROP]
        out_path = out_path.replace('\\', os.sep)
        out_path = out_path.replace('/', os.sep)
        output_path_ent.delete(0, last=tkinter.END)
        output_path_ent.insert(0, out_path)

        add_levels_to_list(default_settings.params[xray.const.FS_PATH_PROP])

root.mainloop()
