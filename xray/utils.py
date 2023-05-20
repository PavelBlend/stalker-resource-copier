import os
import shutil
import time
import webbrowser

from . import const


LOG_FILE_NAME = 'stalker_resource_copier.log'
ALL_COPIED = 'All files are copied.'
MISSIGNG_FILES = 'These files are not copied because they are missing:\n\n'


def read_file(path):
    with open(path, 'rb') as file:
        data = file.read()
    return data


def copy_file(src, output, missing_files):
    if os.path.exists(src):
        out_dir_name = os.path.dirname(output.lower())
        if not os.path.exists(out_dir_name):
            os.makedirs(out_dir_name)
        shutil.copyfile(src, output.lower())

    else:
        missing_files.add(src)


def write_log(missing_files):
    missing_files = list(missing_files)
    missing_files.sort()

    log_lines = []
    if len(missing_files):
        log_lines.append(MISSIGNG_FILES)
        for file in missing_files:
            log_lines.append('{}\n'.format(file))

    else:
        log_lines.append(ALL_COPIED)

    with open(LOG_FILE_NAME, 'w', encoding='utf-8') as log_file:
        for log_line in log_lines:
            log_file.write(log_line)


def save_settings(fs_path, out_folder):
    settings_text = '[default_settings]\n'
    settings_text += '{0} = "{1}"\n'.format(const.FS_PATH_PROP, fs_path)
    settings_text += '{0} = "{1}"\n'.format(const.OUT_FOLDER_PROP, out_folder)

    with open(const.SETTINGS_FILE_NAME, 'w', encoding='utf-8') as file:
        file.write(settings_text)


def report_total_time(status_label, start_time):
    end_time = time.time()
    total_time = end_time - start_time
    total_time_str = 'total time:    {} sec'.format(round(total_time, 2))
    status_label.configure(text='')
    status_label.configure(text=total_time_str, bg=const.LABEL_COLOR)


def visit_repo_page(event):
    webbrowser.open(GITHUB_REPO_URL)


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
            copy_file(src, dist, missing_files)
