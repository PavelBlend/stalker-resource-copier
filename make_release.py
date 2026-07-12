import os
import zipfile
import stalker_resource_copier


prog_name = 'stalker resource copier'
readme_file = 'README'
xray_dir = 'xray'
py_ext = '.py'
pyw_ext = '.pyw'
md_ext = '.md'

source_name = prog_name.replace(' ', '_')
release_name = prog_name.replace(' ', '-')
ver_str = ('.'.join(map(str, stalker_resource_copier.VERSION)))
file_name = '{0}-{1}.zip'.format(release_name, ver_str)

compss_type = zipfile.ZIP_DEFLATED

# write .zip file
with zipfile.ZipFile(file_name, 'w') as release_zip:

    # write main source file
    main_src = source_name + py_ext
    main_dist = '{0}/{0}{1}'.format(source_name, pyw_ext)
    release_zip.write(main_src, main_dist, compress_type=compss_type)

    # write readme file
    readme_src = readme_file + md_ext
    readme_dist = '{0}/{1}{2}'.format(source_name, readme_file, md_ext)
    release_zip.write(readme_src, readme_dist, compress_type=compss_type)

    # write xray files
    for file in os.listdir(xray_dir):
        name, ext = os.path.splitext(file)

        if ext == py_ext:
            py_src = '{0}/{1}'.format(xray_dir, file)
            py_dist = '{0}/{1}/{2}'.format(source_name, xray_dir, file)
            release_zip.write(py_src, py_dist, compress_type=compss_type)

input('Finish!')
