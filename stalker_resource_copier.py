import os
import time
import shutil
import webbrowser
import tkinter
import tkinter.filedialog

import xray


VERSION = (1, 2, 0)
DATE = (2023, 5, 21)


class CopyResource:

    def copy_resource(self):
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


class GUI:

    def __init__(self):
        self.init_params()
        self.create_root_window()
        self.create_main_frame()
        self.create_widgets()
        self.place_widgets()
        self.bind_buttons()
        self.load_settings()

        self.root.mainloop()

    def init_params(self):
        # windows size
        self.WINDOW_WIDTH = 640
        self.WINDOW_HEIGHT = 130

        # button size
        self.BUTTON_WIDTH = 13
        self.BUTTON_HEIGHT = 1

        # entry size
        self.ENTRY_WIDTH = 105

        # widget colors
        self.BACKGROUND_COLOR = '#808080'
        self.ACTIVE_BACKGROUND_COLOR = '#A0A0A0'
        self.BUTTON_COLOR = '#A0A0A0'
        self.ACTIVE_BUTTON_COLOR = '#B3B3B3'
        self.ERROR_COLOR = '#BC0000'
        self.URL_COLOR = '#00007C'

        # fonts
        self.BUTTON_FONT = ('Font', 10, 'bold')
        self.LABEL_FONT = ('Font', 8, 'bold')
        self.ENTRY_FONT = ('Font', 7, 'bold')

        # buttons text
        self.COPY_RES_TEXT = 'copy resource'

    def create_root_window(self):
        self.root = tkinter.Tk()

        self.root.resizable(height=False, width=False)
        self.root.minsize(width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT)
        self.root.maxsize(width=self.WINDOW_WIDTH, height=self.WINDOW_HEIGHT)

        self.root.title('S.T.A.L.K.E.R. Resource Copier')
        self.root['bg'] = self.BACKGROUND_COLOR

        display_center_x = (self.root.winfo_screenwidth()) / 2
        display_center_y = (self.root.winfo_screenheight()) / 2

        root_pos_x = display_center_x - self.WINDOW_WIDTH / 2
        root_pos_y = display_center_y - self.WINDOW_HEIGHT / 2 - 50

        self.root.geometry('+%d+%d' % (root_pos_x, root_pos_y))

    def create_main_frame(self):
        self.frame = tkinter.Frame(
            self.root,
            bg=self.BACKGROUND_COLOR,
            width=self.WINDOW_WIDTH,
            height=self.WINDOW_HEIGHT
        )

    def create_widgets(self):
        self.create_entries()
        self.create_labels()
        self.create_buttons()

    def create_entries(self):
        self.fs_path_ent = tkinter.Entry(
            self.frame,
            width=self.ENTRY_WIDTH,
            font=self.ENTRY_FONT,
            bg=self.BUTTON_COLOR
        )
        self.output_path_ent = tkinter.Entry(
            self.frame,
            width=self.ENTRY_WIDTH,
            font=self.ENTRY_FONT,
            bg=self.BUTTON_COLOR
        )
        self.level_file = tkinter.Entry(
            self.frame,
            width=self.ENTRY_WIDTH,
            font=self.ENTRY_FONT,
            bg=self.BUTTON_COLOR
        )

    def create_labels(self):
        ver_text = 'version:    {0}.{1}.{2}'.format(*VERSION)
        date_text = '{}.{:0>2}.{:0>2}'.format(*DATE)

        self.ver_label = tkinter.Label(
            self.frame,
            text=ver_text,
            font=self.LABEL_FONT,
            bg=xray.const.LABEL_COLOR
        )
        self.date_label = tkinter.Label(
            self.frame,
            text=date_text,
            font=self.LABEL_FONT,
            bg=xray.const.LABEL_COLOR
        )
        self.github_label = tkinter.Label(
            self.frame,
            text=xray.const.GITHUB_REPO_URL,
            font=self.LABEL_FONT,
            bg=xray.const.LABEL_COLOR,
            fg=self.URL_COLOR,
            cursor="hand2"
        )
        self.status_text_label = tkinter.Label(
            self.frame,
            text='status:',
            font=self.LABEL_FONT,
            bg=xray.const.LABEL_COLOR
        )
        self.status_label = tkinter.Label(
            self.frame,
            text='',
            font=self.LABEL_FONT,
            bg=xray.const.LABEL_COLOR
        )
        self.fs_path_label = tkinter.Label(
            self.frame,
            text='fs.ltx:',
            font=self.LABEL_FONT,
            bg=xray.const.LABEL_COLOR
        )
        self.output_path_label = tkinter.Label(
            self.frame,
            text='output:',
            font=self.LABEL_FONT,
            bg=xray.const.LABEL_COLOR
        )
        self.mode_label = tkinter.Label(
            self.frame,
            text='mode:',
            font=self.LABEL_FONT,
            bg=xray.const.LABEL_COLOR
        )
        self.level_name_label = tkinter.Label(
            self.frame,
            text='level:',
            font=self.LABEL_FONT,
            bg=xray.const.LABEL_COLOR
        )

    def create_buttons(self):
        copy_res = CopyResource()

        self.copy_resource_button = tkinter.Button(
            self.frame,
            text=self.COPY_RES_TEXT,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg=self.BUTTON_COLOR,
            activebackground=self.ACTIVE_BUTTON_COLOR,
            font=self.ENTRY_FONT,
            command=copy_res.copy_resource
        )
        self.open_fs_button = tkinter.Button(
            self.frame,
            text='set',
            command=open_fs,
            bg=self.BUTTON_COLOR,
            font=self.ENTRY_FONT,
            width=5
        )
        self.set_output_button = tkinter.Button(
            self.frame,
            text='set',
            command=set_output,
            bg=self.BUTTON_COLOR,
            font=self.ENTRY_FONT,
            width=5
        )
        self.open_level_button = tkinter.Button(
            self.frame,
            text='set',
            command=open_game_level,
            bg=self.BUTTON_COLOR,
            font=self.ENTRY_FONT,
            width=5
        )

    def place_widgets(self):
        self.init_place_params()
        self.place_frame()
        self.place_entries()
        self.place_labels()
        self.place_buttons()

    def init_place_params(self):
        # padding values
        pad = 5
        self.pad_x_rel = pad / self.WINDOW_WIDTH
        self.pad_y_rel = pad / self.WINDOW_HEIGHT

        # columns width
        self.column_1_width = 70
        self.column_3_width = 100
        self.column_2_width = (self.WINDOW_WIDTH - pad * 2 - self.column_3_width) - (self.column_1_width + pad * 2)

        # columns x offset
        self.column_1_x = self.pad_x_rel
        self.column_2_x = self.column_1_width / self.WINDOW_WIDTH + self.pad_x_rel * 2
        self.column_3_x = 1.0 - (self.column_3_width + pad) / self.WINDOW_WIDTH

        self.row_height = 20
        offset_y = (pad + self.row_height) / self.WINDOW_HEIGHT

        # rows y offset
        self.row_1_y = self.pad_y_rel
        self.row_2_y = (pad * 2 + self.row_height) / self.WINDOW_HEIGHT
        self.row_3_y = self.row_2_y + offset_y
        self.row_4_y = self.row_3_y + offset_y
        self.row_5_y = self.row_4_y + offset_y

    def place_frame(self):
        self.frame.grid(row=0, column=0, pady=0)

    def place_entries(self):
        # fs.ltx entry
        self.fs_path_ent.place(
            relx=self.column_2_x,
            rely=self.row_2_y,
            width=self.column_2_width,
            height=self.row_height
        )

        # output entry
        self.output_path_ent.place(
            relx=self.column_2_x,
            rely=self.row_3_y,
            width=self.column_2_width,
            height=self.row_height
        )

        # level entry
        self.level_file.place(
            relx=self.column_2_x,
            rely=self.row_4_y,
            width=self.column_2_width,
            height=self.row_height
        )

    def place_labels(self):
        # date label
        self.date_label.place(
            relx=self.column_1_x,
            rely=self.row_1_y,
            width=self.column_1_width,
            height=self.row_height
        )

        # github url
        self.github_label.place(
            relx=self.column_2_x,
            rely=self.row_1_y,
            width=self.column_2_width,
            height=self.row_height
        )

        # version label
        self.ver_label.place(
            relx=self.column_3_x,
            rely=self.row_1_y,
            width=self.column_3_width,
            height=self.row_height
        )

        # fs.ltx label
        self.fs_path_label.place(
            relx=self.column_1_x,
            rely=self.row_2_y,
            width=self.column_1_width,
            height=self.row_height
        )

        # output label
        self.output_path_label.place(
            relx=self.column_1_x,
            rely=self.row_3_y,
            width=self.column_1_width,
            height=self.row_height
        )

        # level label
        self.level_name_label.place(
            relx=self.column_1_x,
            rely=self.row_4_y,
            width=self.column_1_width,
            height=self.row_height
        )

        # status text
        self.status_text_label.place(
            relx=self.column_1_x,
            rely=self.row_5_y,
            width=self.column_1_width,
            height=self.row_height
        )

        # status label
        self.status_label.place(
            relx=self.column_2_x,
            rely=self.row_5_y,
            width=self.column_2_width,
            height=self.row_height
        )

    def place_buttons(self):
        # fs.ltx button
        self.open_fs_button.place(
            relx=self.column_3_x,
            rely=self.row_2_y,
            width=self.column_3_width,
            height=self.row_height+1
        )

        # output button
        self.set_output_button.place(
            relx=self.column_3_x,
            rely=self.row_3_y,
            width=self.column_3_width,
            height=self.row_height+1
        )

        # level button
        self.open_level_button.place(
            relx=self.column_3_x,
            rely=self.row_4_y,
            width=self.column_3_width,
            height=self.row_height+1
        )

        # copy resource button
        self.copy_resource_button.place(
            relx=self.column_3_x,
            rely=self.row_5_y,
            width=self.column_3_width,
            height=self.row_height
        )

    def bind_buttons(self):
        self.github_label.bind('<Button-1>', xray.utils.visit_repo_page)

    def load_settings(self):
        if os.path.exists(xray.const.SETTINGS_FILE_NAME):
            settings_parser = xray.ltx.LtxParser()
            settings_parser.from_file(xray.const.SETTINGS_FILE_NAME)
            default_settings = settings_parser.sections.get('default_settings', None)

            if default_settings:

                # set fs.ltx path
                fs_path = default_settings.params[xray.const.FS_PATH_PROP]
                fs_path = fs_path.replace('\\', os.sep)
                fs_path = fs_path.replace('/', os.sep)
                self.fs_path_ent.delete(0, last=tkinter.END)
                self.fs_path_ent.insert(0, fs_path)

                # set output path
                out_path = default_settings.params[xray.const.OUT_FOLDER_PROP]
                out_path = out_path.replace('\\', os.sep)
                out_path = out_path.replace('/', os.sep)
                self.output_path_ent.delete(0, last=tkinter.END)
                self.output_path_ent.insert(0, out_path)


if __name__ == '__main__':
    GUI()
