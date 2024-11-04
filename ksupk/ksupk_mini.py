# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import hashlib
import datetime
import shutil
import json
import string
import random
from threading import Thread


class ThreadWithReturnValue(Thread):
    """
    x1 = ThreadWithReturnValue(1, target=some_func, args=(arg1, arg2), kwargs={"kwarg1": kwarg1, "kwarg2": kwarg2,})
    x2 = ThreadWithReturnValue(2, target=some_func, args=(arg1, arg2), kwargs={"kwarg1": kwarg1, "kwarg2": kwarg2,})
    x1.start(), x2.start()
    return_of_some_func_1, return_of_some_func_2 = x1.join(), x2.join()
    """

    def __init__(self, index: int = -1, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._index = index
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                        **self._kwargs)

    def get_index(self):
        return self._index

    def join(self, *args):
        Thread.join(self, *args)
        return self._return


def get_files_list(dirPath: str) -> list:
    return [os.path.join(path, name) for path, subdirs, files in os.walk(dirPath) for name in files]


def get_dirs_list(dirPath: str) -> list:
    dirs = [os.path.join(path, name) for path, subdirs, files in os.walk(dirPath) for name in subdirs]
    return list(set(dirs))


def is_folder_empty(folder_path: str) -> bool:
    if(len(os.listdir(folder_path)) == 0):
        return True
    else:
        return False


def rel_path(file_path: str, folder_path: str) -> str:
    return os.path.relpath(file_path, folder_path)


def get_rel_path_of_files(files: list, folder_path: str) -> list:
    return [rel_path(file_i, folder_path) for file_i in files]


def get_abs_path_of_files(files: list) -> list:
    return [os.path.abspath(file_i) for file_i in files]


def rm_folder_content(folder_path: str, root_dir_too: bool = False, does_not_exists_is_ok = False):
    """Удаляет всё содержимое папки. Саму папку не трогает, если root_dir_too == False"""
    if(does_not_exists_is_ok == True and is_folder(folder_path) == False):
        return
    for root, dirs, files in os.walk(folder_path, topdown=False):
        for file_i in files:
            os.remove(os.path.join(root, file_i))
        for dir in dirs:
            os.rmdir(os.path.join(root, dir))
    if(root_dir_too == True):
        os.rmdir(folder_path)


def write_to_file_str(file_name : str, s : str) -> None:
    with open(file_name, 'w', encoding="utf-8") as fd:
        fd.write(s)
        fd.flush()


def read_from_file_str(file_name : str) -> str:
    with open(file_name, 'r', encoding="utf-8") as fd:
        S = fd.read()
    return S


def save_json(save_path: str, d: dict, indents: int = 4):
    write_to_file_str(save_path, json.dumps(d, indent=indents))


def restore_json(json_path: str) -> dict:
    return json.loads(read_from_file_str(json_path))


def mkdir_with_p(path: str, p: bool = True):
    """
    Создаст директорию, даже если ещё нет родительских.
    Если конечная уже существует, то не вернёт ошибку
    """
    os.makedirs(path, exist_ok=True)


def get_link_unwinding(link_path: str) -> str or None:
    """Вернёт конечный файл, на который (рекурсивно) ссылаются сылки. """
    if(os.path.exists(link_path) == False):
        return None
    elif(os.path.islink(link_path) == False):
        return link_path
    else:
        linkto = os.readlink(link_path)
        if(os.path.islink(linkto) == False):
            return linkto
        else:
            return get_link_unwinding(linkto)


def get_time_str(template="%y.%m.%d %H:%M:%S.%f") -> str:
    # time_str = datetime.datetime.now().strftime("[%y.%m.%d %H:%M:%S.%f]")
    time_str = datetime.datetime.now().strftime(template)
    return time_str


def get_datetime_from_str(s: str, tamplate: str) -> "datetime.datetime":
    """
    like this:
    get_datetime_from_str("24.11.07 10:12:36.590061", "%y.%m.%d %H:%M:%S.%f")
    get_datetime_from_str("2024-08-07 13:36", "%Y-%m-%d %H:%M")
    """
    return datetime.datetime.strptime(s, tamplate)


def get_timestamp_of_file(file_path: str, tamplate: str = "%Y-%m-%d_%H-%M-%S") -> str:
    dt_m = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
    return dt_m.strftime(tamplate)


def calc_hash_of_file(file_path: str, retun_str: bool = True, algo = hashlib.sha256) -> str or bytes:
    buff_BLOCKSIZE = 65536  # 64 kB
    sha = algo()
    with open(file_path, "rb") as temp:
        file_buffer = temp.read(buff_BLOCKSIZE)
        while len(file_buffer) > 0:
            sha.update(file_buffer)
            file_buffer = temp.read(buff_BLOCKSIZE)
    if retun_str:
        return sha.hexdigest()
    else:
        return sha.digest()


def calc_hash_of_str(s: str, retun_str: bool = True, algo = hashlib.sha256) -> str or bytes:
    hl = algo( s.encode("utf-8") )
    if retun_str:
        return hl.hexdigest()
    else:
        return hl.digest()


def calc_hash_of_hashes(hashes: list, retun_str: bool = True, algo = hashlib.sha256) -> str:
    hash_files = ""
    li = 0
    for hash_i in hashes:
        hash_files += hash_i
        li-=-1
        if(li == 30):
            hash_files = get_hash_str(hash_files)
            li = 0
    hash_files = get_hash_str(hash_files, algo=algo, retun_str=retun_str)
    return hash_files


def calc_hash_of_dir(dir_path: str, hierarchy: bool = False, retun_str: bool = True, algo = hashlib.sha256) -> str:
    files = get_files_list(dir_path)
    sha = algo()

    for file_i in files:
        buff_BLOCKSIZE = 65536  # 64 kB
        with open(file_i, "rb") as fd:
            file_buffer = fd.read(buff_BLOCKSIZE)
            while len(file_buffer) > 0:
                sha.update(file_buffer)
                file_buffer = fd.read(buff_BLOCKSIZE)
    
    if hierarchy:
        files_sorted = sorted(get_rel_path_of_files(files + get_dirs_list(dir_path), dir_path))
        for file_i in files_sorted:
            sha.update(file_i.encode("utf-8"))

    if retun_str:
        return sha.hexdigest()
    else:
        return sha.digest()


def get_dirs_needed_for_files(files: list) -> list:
    dirs = set()
    for file_i in files:
        dir_i = os.path.dirname(file_i)
        dirs.add(dir_i)
    dirs = sorted(list(dirs))
    return dirs


def get_file_size(file: str) -> int:
    file = os.path.abspath(file)
    return os.path.getsize(file)
    # return os.stat(file).st_size


def get_dir_size(dir_path: str) -> int:
    files = get_files_list(os.path.abspath(dir_path))
    res = 0
    for file_i in files:
        res += get_file_size(file_i)
    return res


def str_to_bytes(s: str) -> bytes:
    a = list(map(int, s[1:len(s)-1].split(", ")))
    return bytes(a)


def bytes_to_str(bs: bytes) -> str:
    a = list(bs)  # list of ints
    res = ", ".join(map(str, a))
    return f"[{res}]"


def int_to_bytes(x: int) -> bytes:
    return x.to_bytes(length=(max(x.bit_length(), 1) + 7) // 8, byteorder='big')


def bytes_to_int(bs: bytes, set_auto_max_str_digits: bool = True) -> int:
    if set_auto_max_str_digits:
        sys.set_int_max_str_digits(0)
    res = int.from_bytes(bs, byteorder='big')
    return res


def is_int(x: int) -> bool:
    try:
        int(a);
        return True
    except ValueError : 
        return False

def utf8_to_bytes(s: str) -> bytes:
    return s.encode("utf-8")


def bytes_to_utf8(bs: bytes) -> str:
    return str(bs, "utf-8")


def gen_random_string(_lenght : int = 20, pool: str = None) -> str:
    if pool is None:
        pool = string.ascii_letters + string.digits
    S = ''.join(random.choices(pool, k=_lenght))
    return S


def exe_lowout(command: str, debug: bool = True, std_out_pipe: bool = False, std_err_pipe: bool = False) -> tuple:
    '''
    Аргумент command - команда для выполнения в терминале. Например: "ls -lai ."
    Возвращает кортеж, где элементы:
        0 - строка stdout or None if std_out_pipe == False
        1 - строка stderr or None if std_err_pipe == False
        2 - returncode
    '''
    if(debug):
        pout(f"> {command}")
    
    if(std_out_pipe == True):
        if(std_err_pipe == True):
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # https://stackoverflow.com/questions/1180606/using-subprocess-popen-for-process-with-large-output
            out = process.stdout.read().decode("utf-8")
            err = process.stderr.read().decode("utf-8")
        else:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE)
            out = process.stdout.read().decode("utf-8")
            err = None
    else:
        if(std_err_pipe == True):
            process = subprocess.Popen(command, shell=True, stderr=subprocess.PIPE)
            out = None
            err = process.stderr.read().decode("utf-8")
        else:
            process = subprocess.Popen(command, shell=True)
            out = None
            err = None
    errcode = process.returncode
    return (out, err, errcode)


def exe(command: str, debug: bool = True, std_out_fd = subprocess.PIPE, std_err_fd = subprocess.PIPE, stdin_msg: str = None) -> tuple:
    '''
    Аргумент command - команда для выполнения в терминале. Например: "ls -lai ."
    if(std_out_fd or std_err_fd) == subprocess.DEVNULL   |=>    No output enywhere
    if(std_out_fd or std_err_fd) == subprocess.PIPE      |=>    All output to return
    if(std_out_fd or std_err_fd) == open(path, "w")      |=>    All output to file path
    Возвращает кортеж, где элементы:
        0 - строка stdout
        1 - строка stderr
        2 - returncode
    '''
    _ENCODING = "utf-8"

    if(debug):
        #pout(f"> " + " ".join(command))
        if(stdin_msg != None):
            pout(f"> {command}, with stdin=\"{stdin_msg}\"")
        else:
            pout(f"> {command}")

    #proc = subprocess.run(command, shell=True, capture_output=True, input=stdin_msg.encode("utf-8"))
    if(stdin_msg == None):
        proc = subprocess.run(command, shell=True, stdout=std_out_fd, stderr=std_err_fd)
    else:
        proc = subprocess.run(command, shell=True, stdout=std_out_fd, stderr=std_err_fd, input=stdin_msg.encode("utf-8"))
    
    #return (proc.stdout.decode("utf-8"), proc.stderr.decode("utf-8"))

    res_stdout = proc.stdout.decode("utf-8") if proc.stdout != None else None
    res_errout = proc.stderr.decode("utf-8") if proc.stderr != None else None
    return (res_stdout, res_errout, proc.returncode)
