import os
import zipfile
import stalker_resource_copier


prog_name = 'stalker resource copier'
readme_file = 'README.md'
xray_dir = 'xray'
py_ext = '.py'
pyw_ext = '.pyw'

source_name = prog_name.replace(' ', '_')
release_name = prog_name.replace(' ', '-')
ver_str = ('.'.join(map(str, stalker_resource_copier.VERSION)))
file_name = '{0}-{1}.zip'.format(release_name, ver_str)

# write .zip file
with zipfile.ZipFile(file_name, 'w') as release_zip:

    # write main source file
    main_src = source_name + py_ext
    main_dist = '{0}/{0}{1}'.format(source_name, pyw_ext)
    release_zip.write(main_src, main_dist, compress_type=zipfile.ZIP_DEFLATED)

    release_zip.write(
        readme_file,
        '{0}/{1}'.format(source_name, readme_file),
        compress_type=zipfile.ZIP_DEFLATED
    )
    for file in os.listdir(xray_dir):
        name, ext = os.path.splitext(file)
        if ext == py_ext:
            release_zip.write(
                '{0}\\{1}{2}'.format(xray_dir, name, py_ext),
                '{0}/{1}/{2}.py'.format(source_name, xray_dir, name),
                compress_type=zipfile.ZIP_DEFLATED
            )

input('Finish!')
