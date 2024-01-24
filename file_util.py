import os
import zipfile
from pathlib import Path

MB = 1024 * 1024


def num_mb(num_bytes: int):
    return int(num_bytes / MB)


def zip_by_volume(file_path, block_size):
    """zip文件分卷压缩"""
    file_size = os.path.getsize(file_path)  # 文件字节数
    path, file_name = os.path.split(file_path)  # 除去文件名以外的path，文件名
    suffix = file_name.split('.')[-1]  # 文件后缀名
    # 添加到临时压缩文件
    zip_file = file_path + '.zip'
    with zipfile.ZipFile(zip_file, 'w') as zf:
        zf.write(file_path, arcname=file_name)
    # 小于分卷尺寸则直接返回压缩文件路径
    if file_size <= block_size:
        return zip_file
    else:
        fp = open(zip_file, 'rb')
        count = file_size // block_size + 1
        # 创建分卷压缩文件的保存路径
        save_dir = path + os.sep + file_name + '_split'
        if os.path.exists(save_dir):
            from shutil import rmtree
            rmtree(save_dir)
        os.mkdir(save_dir)
        # 拆分压缩包为分卷文件
        for i in range(1, count + 1):
            _suffix = 'z{:0>2}'.format(i) if i != count else 'zip'
            name = save_dir + os.sep + file_name.replace(str(suffix), _suffix)
            f = open(name, 'wb+')
            if i == 1:
                f.write(b'\x50\x4b\x07\x08')  # 添加分卷压缩header(4字节)
                f.write(fp.read(block_size - 4))
            else:
                f.write(fp.read(block_size))
        fp.close()
        os.remove(zip_file)  # 删除临时的 zip 文件
        return save_dir


def zip_split(src: Path, out: Path, volume_size: int):
    file_name = src.stem
    split_tmp = Path(f'{out / file_name}s.zip')
    if src.name.endswith('zip'):
        zip_tmp = src
    else:
        zip_tmp = Path(f'{out / file_name}.zip')
        if src.is_file():
            zip_cmd = f'zip -j {zip_tmp} {src.absolute()}'
        else:
            zip_cmd = f'zip -r {zip_tmp} {src.absolute()}'
        file_name = src.name
        print(f'Zip file {file_name} into {zip_tmp}')
        os.popen(zip_cmd).read()
    if num_mb(zip_tmp.stat().st_size) > volume_size:
        print(f'Split file[{file_name}] into {volume_size}MB')
        split_cmd = f'zip -s {volume_size}m {zip_tmp} --out {split_tmp}'
        os.popen(split_cmd).read()
        print('Split file succeed')
        files = [l for l in out.glob(f"{src.stem}s.*")]
        return files
    else:
        return [zip_tmp]

