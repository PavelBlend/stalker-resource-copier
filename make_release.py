import os
import zipfile


version = (0, 0, 4)
file_name = 'stalker-resource-copier-' + ('.'.join(map(str, version))) + '.zip'

with zipfile.ZipFile(file_name, 'w') as z:
    z.write(
        'stalker_resource_copier.py',
        'stalker_resource_copier/stalker_resource_copier.pyw',
        compress_type=zipfile.ZIP_DEFLATED
    )
    z.write(
        'README.md',
        'stalker_resource_copier/README.md',
        compress_type=zipfile.ZIP_DEFLATED
    )
    for file in os.listdir('xray'):
        name, ext = os.path.splitext(file)
        if ext == '.py':
            z.write(
                'xray\\{}.py'.format(name),
                'stalker_resource_copier/xray/{}.py'.format(name),
                compress_type=zipfile.ZIP_DEFLATED
            )

input('Finish!')
