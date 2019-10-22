from zipfile import ZipFile, ZIP_DEFLATED
from os import path, walk


version = (0, 0, 2)
with ZipFile('stalker-resource-copier-' + ('.'.join(map(str, version))) + '.zip', 'w') as z:
    z.write(
        'stalker_resource_copier.pyw',
        'stalker_resource_copier/stalker_resource_copier.pyw',
        compress_type=ZIP_DEFLATED
    )
    z.write(
        'readme.txt',
        'stalker_resource_copier/readme.txt',
        compress_type=ZIP_DEFLATED
    )
    z.write(
        'xray\\__init__.py',
        'stalker_resource_copier/xray/__init__.py',
        compress_type=ZIP_DEFLATED
    )
    z.write(
        'xray\\lzhuf.py',
        'stalker_resource_copier/xray/lzhuf.py',
        compress_type=ZIP_DEFLATED
    )
    z.write(
        'xray\\xray_io.py',
        'stalker_resource_copier/xray/xray_io.py',
        compress_type=ZIP_DEFLATED
    )
    z.write(
        'xray\\xray_ltx.py',
        'stalker_resource_copier/xray/xray_ltx.py',
        compress_type=ZIP_DEFLATED
    )
input('Finish!')
