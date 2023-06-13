import os
import shutil
import time
import webbrowser

from . import const
from . import ltx


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
    webbrowser.open(const.GITHUB_REPO_URL)


def copy_files(
        files,
        missing_files,
        game_folder,
        raw_folder,
        out_game_folder,
        out_raw_folder,
        game_ext,
        raw_ext
    ):

    files = list(files)

    bumps = {}

    if game_ext == 'dds':
        tex_ltx_path = os.path.join(game_folder, 'textures.ltx')

        if os.path.exists(tex_ltx_path):
            tex_ltx = ltx.LtxParser()
            tex_ltx.from_file(tex_ltx_path)
            bumps_sect = tex_ltx.sections['specification']

            for tex_name, tex_param in bumps_sect.params.items():
                if 'bump_mode[use:' in tex_param:
                    bump = tex_param.split('bump_mode[use:')[1].split(']')[0]
                    if bump:
                        bumps[tex_name] = bump

    if bumps:

        for file in files:
            bump_file = bumps.get(file, None)

            if bump_file:
                files.append(bump_file)
                files.append(bump_file + '#')

    files.sort()

    for file in files:
        # source paths
        game_file_path = os.path.join(game_folder, file + os.extsep + game_ext)
        game_thm_path = os.path.join(game_folder, file + os.extsep + 'thm')
        raw_file_path = os.path.join(raw_folder, file + os.extsep + raw_ext)
        raw_thm_path = os.path.join(raw_folder, file + os.extsep + 'thm')

        # output paths
        out_game_path = os.path.join(out_game_folder, file + os.extsep + game_ext)
        out_raw_path = os.path.join(out_raw_folder, file + os.extsep + raw_ext)
        out_thm_path = os.path.join(out_game_folder, file + os.extsep + 'thm')

        copy_files_list = [
            [game_file_path, out_game_path],
            [raw_file_path, out_raw_path],
            [game_thm_path, out_thm_path],
            [raw_thm_path, out_thm_path]
        ]

        for src, dist in copy_files_list:
            copy_file(src, dist, missing_files)
