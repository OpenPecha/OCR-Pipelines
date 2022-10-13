import shutil

from openpecha.core.pecha import OpenPechaFS
from openpecha.blupdate import update_single_base

def clean_dir(dir):
    if dir.is_dir():
        shutil.rmtree(str(dir))

def update_pecha(old_pecha, new_pecha):
    for new_base_name, new_base in new_pecha.bases.items():
        update_single_base(old_pecha, new_base_name, new_content=new_base)
    clean_dir(new_pecha.pecha_path)
    return old_pecha