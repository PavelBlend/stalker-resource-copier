import os
import time
import shutil
import webbrowser
import tkinter
import tkinter.filedialog

import xray


VERSION = (1, 2, 0)
DATE = (2023, 5, 21)


def copy_resource():
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

    # get level path
    level_path = level_file.get()
    level_path = level_path.replace('/', os.sep)
    level_path = level_path.replace('\\', os.sep)

    if not level_path:
        status_label.configure(
            text='ERROR: Level file not specified!',
            bg=ERROR_COLOR
        )
        return

    if os.path.exists(level_path):

        if not os.path.isfile(level_path):
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

    maps_dir = os.path.join(fs_dir, fs.values['$maps$'])
    output_level_dir = os.path.join(out_folder, fs.values['$maps$'])

    # rawdata\maps
    if level_path.startswith(maps_dir):

        groups_dir = os.path.join(fs_dir, fs.values['$groups$'])

        level_folder = os.path.splitext(level_path)[0]

        if os.path.exists(level_folder):

            for file_name in os.listdir(level_folder):
                file_path = os.path.join(level_folder, file_name)

                if file_name == 'scene_object.part':
                    xray.scene_objects.read_scene_objects_part(file_path, objects)

                elif file_name == 'detail_object.part':
                    xray.scene_details.read_level_details(file_path, objects, textures)

                elif file_name == 'glow.part':
                    xray.scene_glows.read_level_glows(file_path, textures)

                elif file_name == 'wallmark.part':
                    xray.scene_wallmarks.read_level_wallmarks(file_path, textures)

                elif file_name == 'sound_src.part':
                    xray.scene_sound_source.read_sound_sources(file_path, sounds)

                elif file_name == 'group.part':
                    xray.scene_groups.read_level_groups(file_path, objects, groups_dir)

        else:
            status_label.configure(
                text='ERROR: level folder not found: "{}"'.format(level_folder),
                bg=ERROR_COLOR
            )
            return

    # gamedata\levels
    else:
        xray.game_level.read_game_level_textures(level_path, textures)

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

    if level_path.startswith(maps_dir):
        level_rel_path = os.path.splitext(level_path)[0][len(maps_dir) : ]

        # copy *.level file
        level_main_file_output_path = os.path.join(output_level_dir, level_rel_path, '.level')
        xray.utils.copy_file(level_path, level_main_file_output_path, missing_files)

        # copy *.part files
        for file_name in os.listdir(level_folder):
            part_name, part_ext = os.path.splitext(file_name)
            if part_ext == '.part':
                part_src = os.path.join(level_folder, file_name)
                part_out = os.path.join(os.path.join(output_level_dir, level_rel_path), file_name)
                xray.utils.copy_file(part_src, part_out, missing_files)

    # report
    xray.utils.write_log(missing_files)
    xray.utils.save_settings(fs_path, out_folder)
    xray.utils.report_total_time(status_label, start_time)


def _set_entry_value(entry, dialog_fun):
    path = dialog_fun()
    if path:
        path = path.replace('\\', os.sep)
        path = path.replace('/', os.sep)
        entry.delete(0, last=tkinter.END)
        entry.insert(0, path)


def set_output():
    _set_entry_value(output_path_ent, tkinter.filedialog.askdirectory)


def open_fs():
    _set_entry_value(fs_path_ent, tkinter.filedialog.askopenfilename)


def open_game_level():
    _set_entry_value(level_file, tkinter.filedialog.askopenfilename)


if __name__ == '__main__':

    WINDOW_WIDTH = 640
    WINDOW_HEIGHT = 130
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

    # main frame
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

    # level file
    level_file = tkinter.Entry(frame, width=105, font=ENTRY_FONT, bg=BUTTON_COLOR)
    open_game_level_button = tkinter.Button(frame, text='set', command=open_game_level, bg=BUTTON_COLOR, font=ENTRY_FONT, width=5)

    frame.grid(row=0, column=0, pady=0)

    # padding values
    pad = 5
    pad_x_rel = pad / WINDOW_WIDTH
    pad_y_rel = pad / WINDOW_HEIGHT

    # columns width
    column_1_width = 70
    column_3_width = 100
    column_2_width = (WINDOW_WIDTH - pad*2 - column_3_width) - (column_1_width + pad*2)

    # columns x offset
    column_1_x = pad_x_rel
    column_2_x = column_1_width / WINDOW_WIDTH + pad_x_rel * 2
    column_3_x = 1.0 - (column_3_width+pad) / WINDOW_WIDTH

    row_height = 20
    offset_y = (pad + row_height) / WINDOW_HEIGHT

    # rows y offset
    row_1_y = pad_y_rel
    row_2_y = (pad*2 + row_height) / WINDOW_HEIGHT
    row_3_y = row_2_y + offset_y
    row_4_y = row_3_y + offset_y
    row_5_y = row_4_y + offset_y

    # date label
    date_label.place(relx=column_1_x, rely=row_1_y, width=column_1_width, height=row_height)

    # github url
    github_label.place(relx=column_2_x, rely=row_1_y, width=column_2_width, height=row_height)

    # version label
    ver_label.place(relx=column_3_x, rely=row_1_y, width=column_3_width, height=row_height)

    # fs.ltx label
    fs_path_label.place(relx=column_1_x, rely=row_2_y, width=column_1_width, height=row_height)

    # fs.ltx entry
    fs_path_ent.place(relx=column_2_x, rely=row_2_y, width=column_2_width, height=row_height)

    # fs.ltx button
    open_fs_button.place(relx=column_3_x, rely=row_2_y, width=column_3_width, height=row_height+1)

    # output label
    output_path_label.place(relx=column_1_x, rely=row_3_y, width=column_1_width, height=row_height)

    # output entry
    output_path_ent.place(relx=column_2_x, rely=row_3_y, width=column_2_width, height=row_height)

    # output button
    set_output_button.place(relx=column_3_x, rely=row_3_y, width=column_3_width, height=row_height+1)

    # level label
    level_name_label.place(relx=column_1_x, rely=row_4_y, width=column_1_width, height=row_height)

    # level entry
    level_file.place(relx=column_2_x, rely=row_4_y, width=column_2_width, height=row_height)

    # level button
    open_game_level_button.place(relx=column_3_x, rely=row_4_y, width=column_3_width, height=row_height+1)

    # status text
    status_text_label.place(relx=column_1_x, rely=row_5_y, width=column_1_width, height=row_height)

    # status label
    status_label.place(relx=column_2_x, rely=row_5_y, width=column_2_width, height=row_height)

    # copy resource button
    copy_resource_button.place(relx=column_3_x, rely=row_5_y, width=column_3_width, height=row_height)

    # bind
    github_label.bind('<Button-1>', xray.utils.visit_repo_page)

    # settings
    if os.path.exists(xray.const.SETTINGS_FILE_NAME):
        settings_parser = xray.ltx.LtxParser()
        settings_parser.from_file(xray.const.SETTINGS_FILE_NAME)
        default_settings = settings_parser.sections.get('default_settings', None)

        if default_settings:

            # set fs.ltx path
            fs_path = default_settings.params[xray.const.FS_PATH_PROP]
            fs_path = fs_path.replace('\\', os.sep)
            fs_path = fs_path.replace('/', os.sep)
            fs_path_ent.delete(0, last=tkinter.END)
            fs_path_ent.insert(0, fs_path)

            # set output path
            out_path = default_settings.params[xray.const.OUT_FOLDER_PROP]
            out_path = out_path.replace('\\', os.sep)
            out_path = out_path.replace('/', os.sep)
            output_path_ent.delete(0, last=tkinter.END)
            output_path_ent.insert(0, out_path)

    root.mainloop()
