import os
import time
import shutil
import webbrowser
import tkinter
import tkinter.filedialog

import xray


VERSION = (1, 3, 0)
DATE    = (2026, 7, 13)


class ResourceCopier:

    STATUS_OK = True
    LEVEL_EXT = os.extsep + 'level'
    PART_EXT  = os.extsep + 'part'

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
        self.LABEL_COLOR = '#707070'
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
        # fs.ltx entry
        self.fs_path_ent = tkinter.Entry(
            self.frame,
            width=self.ENTRY_WIDTH,
            font=self.ENTRY_FONT,
            bg=self.BUTTON_COLOR
        )

        # output entry
        self.output_path_ent = tkinter.Entry(
            self.frame,
            width=self.ENTRY_WIDTH,
            font=self.ENTRY_FONT,
            bg=self.BUTTON_COLOR
        )

        # level entry
        self.level_file_ent = tkinter.Entry(
            self.frame,
            width=self.ENTRY_WIDTH,
            font=self.ENTRY_FONT,
            bg=self.BUTTON_COLOR
        )

    def create_labels(self):
        # label text
        ver_text = 'version:    {0}.{1}.{2}'.format(*VERSION)
        date_text = '{}.{:0>2}.{:0>2}'.format(*DATE)

        # version label
        self.ver_label = tkinter.Label(
            self.frame,
            text=ver_text,
            font=self.LABEL_FONT,
            bg=self.LABEL_COLOR
        )

        # date label
        self.date_label = tkinter.Label(
            self.frame,
            text=date_text,
            font=self.LABEL_FONT,
            bg=self.LABEL_COLOR
        )

        # url label
        self.github_label = tkinter.Label(
            self.frame,
            text=xray.const.GITHUB_REPO_URL,
            font=self.LABEL_FONT,
            bg=self.LABEL_COLOR,
            fg=self.URL_COLOR,
            cursor="hand2"
        )

        # status text label
        self.status_text_label = tkinter.Label(
            self.frame,
            text='status:',
            font=self.LABEL_FONT,
            bg=self.LABEL_COLOR
        )

        # status label
        self.status_label = tkinter.Label(
            self.frame,
            text='',
            font=self.LABEL_FONT,
            bg=self.LABEL_COLOR
        )

        # fs.ltx label
        self.fs_path_label = tkinter.Label(
            self.frame,
            text='fs.ltx:',
            font=self.LABEL_FONT,
            bg=self.LABEL_COLOR
        )

        # output label
        self.output_path_label = tkinter.Label(
            self.frame,
            text='output:',
            font=self.LABEL_FONT,
            bg=self.LABEL_COLOR
        )

        # lavel label
        self.level_name_label = tkinter.Label(
            self.frame,
            text='level:',
            font=self.LABEL_FONT,
            bg=self.LABEL_COLOR
        )

    def create_buttons(self):
        # copy resource button
        self.copy_resource_button = tkinter.Button(
            self.frame,
            text=self.COPY_RES_TEXT,
            width=self.BUTTON_WIDTH,
            height=self.BUTTON_HEIGHT,
            bg=self.BUTTON_COLOR,
            activebackground=self.ACTIVE_BUTTON_COLOR,
            font=self.ENTRY_FONT,
            command=self.copy_resource
        )

        # open fs.ltx button
        self.open_fs_button = tkinter.Button(
            self.frame,
            text='set',
            command=self.open_fs,
            bg=self.BUTTON_COLOR,
            font=self.ENTRY_FONT,
            width=5
        )

        # set output button
        self.set_output_button = tkinter.Button(
            self.frame,
            text='set',
            command=self.set_output,
            bg=self.BUTTON_COLOR,
            font=self.ENTRY_FONT,
            width=5
        )

        # set level button
        self.open_level_button = tkinter.Button(
            self.frame,
            text='set',
            command=self.open_level,
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
        self.level_file_ent.place(
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
            def_stngs = settings_parser.sections.get('default_settings', None)

            if def_stngs:

                # set fs.ltx path
                fs_path = def_stngs.params.get(xray.const.FS_PATH_PROP)
                if fs_path:
                    fs_path = self.get_path(fs_path)
                    self.fs_path_ent.delete(0, last=tkinter.END)
                    self.fs_path_ent.insert(0, fs_path)

                # set output path
                out_path = def_stngs.params.get(xray.const.OUT_FOLDER_PROP)
                if out_path:
                    out_path = self.get_path(out_path)
                    self.output_path_ent.delete(0, last=tkinter.END)
                    self.output_path_ent.insert(0, out_path)

                # set level path
                level_path = def_stngs.params.get(xray.const.LEVEL_PATH_PROP)
                if level_path:
                    level_path = self.get_path(level_path)
                    self.level_file_ent.delete(0, last=tkinter.END)
                    self.level_file_ent.insert(0, level_path)

    def get_path(self, path):
        path = path.replace('\\', os.sep)
        path = path.replace('/', os.sep)
        return path

    def _set_entry_value(self, entry, dialog_fun):
        path = dialog_fun()
        if path:
            path = self.get_path(path)
            entry.delete(0, last=tkinter.END)
            entry.insert(0, path)

    def set_output(self):
        self._set_entry_value(
            self.output_path_ent,
            tkinter.filedialog.askdirectory
        )

    def open_fs(self):
        self._set_entry_value(
            self.fs_path_ent,
            tkinter.filedialog.askopenfilename
        )

    def open_level(self):
        self._set_entry_value(
            self.level_file_ent,
            tkinter.filedialog.askopenfilename
        )

    ###########################################################################

    def copy_resource(self):
        self.start_time = time.time()

        stages = (
            self.read_fs_ltx,
            self.get_output_folder,
            self.init_collections,
            self.get_level_path,
            self.get_maps_dir,
            self.collect_files,
            self.get_folders,
            self.copy_objects,
            self.copy_textures,
            self.copy_sounds,
            self.copy_level
        )

        for stage in stages:
            status = stage()

            if not status:
                return

        self.report()

    def read_fs_ltx(self):
        self.fs_path = self.fs_path_ent.get()
        self.fs_path = self.get_path(self.fs_path)

        if not os.path.exists(self.fs_path):
            self.status_label.configure(
                text='ERROR: fs.ltx does not exist!',
                bg=self.ERROR_COLOR
            )
            return

        self.fs = xray.ltx.LtxParser()
        self.fs.from_file(self.fs_path)
        self.fs_dir = os.path.dirname(self.fs_path)

        return self.STATUS_OK

    def get_output_folder(self):
        self.out_folder = self.output_path_ent.get()
        self.out_folder = self.get_path(self.out_folder)

        if not os.path.exists(self.out_folder):
            os.makedirs(self.out_folder)

        if os.listdir(self.out_folder):
            self.status_label.configure(
                text='ERROR: Output folder is not empty!',
                bg=self.ERROR_COLOR
            )
            return

        return self.STATUS_OK

    def init_collections(self):
        self.objects = set()
        self.textures = set()
        self.sounds = set()
        self.missing_files = set()
        return self.STATUS_OK

    def get_level_path(self):
        self.level_path = self.level_file_ent.get()
        self.level_path = self.get_path(self.level_path)

        if not self.level_path:
            self.status_label.configure(
                text='ERROR: Level file not specified!',
                bg=self.ERROR_COLOR
            )
            return

        if os.path.exists(self.level_path):

            if not os.path.isfile(self.level_path):
                self.status_label.configure(
                    text='ERROR: Level file not exists!',
                    bg=self.ERROR_COLOR
                )
                return

        else:
            self.status_label.configure(
                text='ERROR: Level file not exists!',
                bg=self.ERROR_COLOR
            )
            return

        return self.STATUS_OK

    def get_maps_dir(self):
        maps = self.fs.values['$maps$']
        self.maps_dir         = os.path.join(self.fs_dir,     maps)
        self.output_level_dir = os.path.join(self.out_folder, maps)
        return self.STATUS_OK

    def collect_files(self):
        is_raw_level = False

        if self.level_path.startswith(self.maps_dir):
            is_raw_level = True

        if os.path.splitext(self.level_path)[-1] == self.LEVEL_EXT:
            is_raw_level = True

        if is_raw_level:
            status = self.collect_rawdata_files()
        else:
            xray.game_level.read_game_level_textures(self.level_path, self.textures)
            status = self.STATUS_OK

        return status

    def collect_rawdata_files(self):
        groups = self.fs.values['$groups$']
        self.groups_dir = os.path.join(self.fs_dir, groups)
        self.level_folder = os.path.splitext(self.level_path)[0]

        if os.path.exists(self.level_folder):
            self.collect_map_files()
            self.objects = list(self.objects)
            self.objects.sort()

        else:
            self.status_label.configure(
                text='ERROR: level folder not found: "{}"'.format(self.level_folder),
                bg=self.ERROR_COLOR
            )
            return

        return self.STATUS_OK

    def collect_map_files(self):

        for file_name in os.listdir(self.level_folder):

            file_name = file_name.lower()
            file_path = os.path.join(self.level_folder, file_name)

            if file_name == 'scene_object.part':
                xray.scene_objects.read_scene_objects_part(file_path, self.objects)

            elif file_name == 'detail_object.part':
                xray.scene_details.read_level_details(file_path, self.objects, self.textures)

            elif file_name == 'glow.part':
                xray.scene_glows.read_level_glows(file_path, self.textures)

            elif file_name == 'wallmark.part':
                xray.scene_wallmarks.read_level_wallmarks(file_path, self.textures)

            elif file_name == 'sound_src.part':
                xray.scene_sound_source.read_sound_sources(file_path, self.sounds)

            elif file_name == 'group.part':
                xray.scene_groups.read_level_groups(file_path, self.objects, self.groups_dir)

    def get_folders(self):

        # relative path
        objects       = self.fs.values['$objects$']
        game_textures = self.fs.values['$game_textures$']
        raw_textures  = self.fs.values['$textures$']

        # objects
        self.objects_folder      = os.path.join(self.fs_dir,     objects)
        self.out_objects_folder  = os.path.join(self.out_folder, objects)

        # game textures
        self.game_tex_folder     = os.path.join(self.fs_dir,     game_textures)
        self.out_game_tex_folder = os.path.join(self.out_folder, game_textures)

        # raw textures
        self.raw_tex_folder = os.path.join(self.fs_dir,          raw_textures)
        self.out_raw_tex_folder = os.path.join(self.out_folder,  raw_textures)

        return self.STATUS_OK

    def copy_lod(self, object_name, object_path):
        # copy lod textures

        object_type = xray.object_format.get_object_textures(object_path, self.textures)

        if object_type == 'MULIPLE_USAGE':

            lod_tex_path = 'lod' + os.sep + 'lod_' + object_name.replace(os.sep, '_')

            # source paths
            game_tex_path = os.path.join(self.game_tex_folder, lod_tex_path + os.extsep + 'dds')
            raw_tex_path  = os.path.join(self.raw_tex_folder,  lod_tex_path + os.extsep + 'tga')
            game_thm_path = os.path.join(self.game_tex_folder, lod_tex_path + os.extsep + 'thm')
            raw_thm_path  = os.path.join(self.raw_tex_folder,  lod_tex_path + os.extsep + 'thm')

            # output paths
            out_game_tex_path = os.path.join(self.out_game_tex_folder, lod_tex_path + os.extsep + 'dds')
            out_raw_tex_path  = os.path.join(self.out_raw_tex_folder,  lod_tex_path + os.extsep + 'tga')
            out_thm_path      = os.path.join(self.out_game_tex_folder, lod_tex_path + os.extsep + 'thm')

            texs = [
                [game_tex_path, out_game_tex_path],
                [raw_tex_path,  out_raw_tex_path],
                [game_thm_path, out_thm_path],
                [raw_thm_path,  out_thm_path]
            ]

            for src, dist in texs:
                xray.utils.copy_file(src, dist, self.missing_files)

    def copy_object(self, object_name, object_path):
        # copy *.object file

        out_object_path = os.path.join(self.out_objects_folder, object_name + os.extsep + 'object')

        object_dir = os.path.dirname(out_object_path)
        if not os.path.exists(object_dir):
            os.makedirs(object_dir)

        shutil.copyfile(object_path, out_object_path)

    def copy_object_thm(self, object_name):
        thm_path = os.path.join(self.objects_folder, object_name + os.extsep + 'thm')

        if os.path.exists(thm_path):
            out_thm_path = os.path.join(self.out_objects_folder, object_name + os.extsep + 'thm')

            thm_dir = os.path.dirname(out_thm_path)
            if not os.path.exists(thm_dir):
                os.makedirs(thm_dir)

            shutil.copyfile(thm_path, out_thm_path)

        else:
            self.missing_files.add(thm_path)

    def copy_objects(self):
        if self.objects:
            if not os.path.exists(self.out_objects_folder):
                os.makedirs(self.out_objects_folder)

            # copy *.object and *.thm for objects
            for object_name in self.objects:

                # *.object
                object_path = os.path.join(self.objects_folder, object_name + os.extsep + 'object')
                if os.path.exists(object_path):
                    self.copy_object(object_name, object_path)
                    self.copy_lod(object_name, object_path)
                else:
                    self.missing_files.add(object_path)

                # *.thm
                self.copy_object_thm(object_name)

        return self.STATUS_OK

    def copy_textures(self):
        # copy textures *.dds, *.tga, *.thm

        xray.utils.copy_files(

            self.textures,
            self.missing_files,

            self.game_tex_folder,
            self.raw_tex_folder,

            self.out_game_tex_folder,
            self.out_raw_tex_folder,

            'dds',
            'tga'

        )

        return self.STATUS_OK

    def copy_sounds(self):
        # copy sounds *.ogg, *.wav, *.thm

        game_sounds = self.fs.values['$game_sounds$']
        raw_sounds  = self.fs.values['$sounds$']

        game_sounds_folder     = os.path.join(self.fs_dir,     game_sounds)
        out_game_sounds_folder = os.path.join(self.out_folder, game_sounds)

        raw_sounds_folder      = os.path.join(self.fs_dir,     raw_sounds)
        out_raw_sounds_folder  = os.path.join(self.out_folder, raw_sounds)

        xray.utils.copy_files(

            self.sounds,
            self.missing_files,

            game_sounds_folder,
            raw_sounds_folder,

            out_game_sounds_folder,
            out_raw_sounds_folder,

            'ogg',
            'wav'

        )

        return self.STATUS_OK

    def copy_level_main_file(self):
        # copy *.level file
        path = os.path.join(self.output_level_dir, self.level_rel_path) + self.LEVEL_EXT
        xray.utils.copy_file(self.level_path, path, self.missing_files)

    def copy_level_part_files(self):
        # copy *.part files
        for file_name in os.listdir(self.level_folder):
            part_name, part_ext = os.path.splitext(file_name)
            if part_ext.lower() == self.PART_EXT:
                part_src = os.path.join(self.level_folder, file_name)
                part_out = os.path.join(self.output_level_dir, self.level_rel_path, file_name)
                xray.utils.copy_file(part_src, part_out, self.missing_files)

    def copy_level(self):
        # copy rawdata\maps\level_name files
        if self.level_path.startswith(self.maps_dir):
            self.level_rel_path = os.path.splitext(self.level_path)[0][len(self.maps_dir) : ]

            self.copy_level_main_file()
            self.copy_level_part_files()

        return self.STATUS_OK

    def report(self):
        xray.utils.write_log(self.missing_files)
        xray.utils.save_settings(self.fs_path, self.out_folder, self.level_path)
        xray.utils.report_total_time(self.status_label, self.start_time, self.LABEL_COLOR)


if __name__ == '__main__':
    ResourceCopier()
