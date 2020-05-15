import progressbar
import base64
import sys
from typing import List
from Crypto.Cipher import AES
from hashlib import md5

from resources.config import Config
from resources.haste import HasteDocument

args = sys.argv[1:]


def make_AES(key):
    allowed_bytes = [16, 24, 32]
    target_size = None
    for ab in allowed_bytes:
        if len(key) <= ab:
            target_size = ab
            break
    if target_size is None:
        print("Your key is longer than 32!")
        exit(1)
    length = len(key)
    new_key = key * (target_size // length)
    if target_size % length != 0:
        rest = target_size % length
        new_key += key[:rest]
    return AES.new(new_key)


if len(args) == 2:
    # upload
    input_file = args[0]
    password = args[1]
    print("Reading file")
    with open(input_file, "rb") as file:
        content = file.read()
    print("Hashing")
    file_hash = md5()
    file_hash.update(content)
    print("Splitting")
    splitted_bytes: List[List[int]] = [[]]
    for b in content:
        element = splitted_bytes[len(splitted_bytes) - 1]
        if len(element) >= Config.SPLITTING:
            splitted_bytes.append([b])
        else:
            splitted_bytes[len(splitted_bytes) - 1].append(b)
    print(f"File has been splitted in {len(splitted_bytes)} section(s)")
    print("Encrypting")
    aes = make_AES(password)
    encrypted_bytes = []
    for b in splitted_bytes:
        data = bytes(b)
        length = 16 - (len(data) % 16)
        data += bytes([length]) * length
        encrypted_bytes.append(base64.b64encode(aes.encrypt(data)).decode("utf-8"))
    assert len(encrypted_bytes) == len(splitted_bytes)
    print(f"Uploading {len(encrypted_bytes)} sections")
    hastes = []
    with progressbar.ProgressBar(max_value=len(encrypted_bytes)) as bar:
        for b in encrypted_bytes:
            hastes.append(HasteDocument.create(b))
            bar.update(len(hastes))
    server_hash = md5()
    server_hash.update(Config.API_PATH.encode("utf-8"))
    key = f"{server_hash.hexdigest()}-{file_hash.hexdigest()}-"
    for h in hastes:
        key += h.key + "-"
    key = key[:len(key) - 1]
    key = base64.b64encode(key.encode("utf-8")).decode("utf-8")

    print(f"Uploading finished, the key is {key}")

elif len(args) == 3:
    # download
    hastebin_key = base64.b64decode(args[0].encode("utf-8")).decode("utf-8")
    password = args[1]
    output_file = args[2]

    keys = hastebin_key.split("-")
    server_hash_out = keys[0]
    file_hash_out = keys[1]
    keys = keys[2:]
    server_hash = md5()
    server_hash.update(Config.API_PATH.encode("utf-8"))
    if server_hash.hexdigest() != server_hash_out:
        print("The file has been uploaded to a other haste server!")
        exit(1)

    print(f"Reading {len(keys)} sections")
    with progressbar.ProgressBar(max_value=len(keys)) as bar:
        file_bytes_raw = []
        aes = make_AES(password)
        for key in keys:
            h = HasteDocument.get(key)
            data = aes.decrypt(base64.b64decode(h.data.encode("utf-8")))
            data = data[:-data[-1]]
            file_bytes_raw.append(data)
            bar.update(len(file_bytes_raw))
    print("Checking hash")
    file_bytes = b''
    for file_byte_raw in file_bytes_raw:
        file_bytes += file_byte_raw
    file_hash = md5()
    file_hash.update(file_bytes)
    if file_hash_out != file_hash.hexdigest():
        print("The file hash is incorrect. Check your password!")
        exit(1)
    print("Writing file")
    with open(output_file, 'wb') as file:
        file.write(file_bytes)


else:
    print("Help:")
    print("run with arguments for upload: <input_file> <password>")
    print("run with arguments for download: <hastebin_key> <password> <output_file>")
    exit(1)
