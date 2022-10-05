import shutil

from openpecha.core.pecha import OpenPechaFS
from openpecha.blupdate import update_single_base

def clean_dir(dir):
    if dir.is_dir():
        shutil.rmtree(str(dir))

def update_pecha(pecha_id, old_pecha_path, new_pecha_path):
    old_pecha = OpenPechaFS(pecha_id=pecha_id, path=old_pecha_path)
    new_base_paths = list((new_pecha_path / "base").iterdir())
    new_base_paths.sort()
    for base_path in new_base_paths:
        new_base = base_path.read_text(encoding='utf-8')
        update_single_base(old_pecha, base_path.stem, new_content=new_base)
    return old_pecha_path