from typing import Union
import platform
import secrets
import hashlib
import ctypes
import winreg
import uuid
import time
import os

import wmi



KEY_FILENAME = ".usbkey"


class FlashKeyAuth:
    FILE_ATTRIBUTE_NORMAL   = 0x80
    FILE_ATTRIBUTE_READONLY = 0x01
    FILE_ATTRIBUTE_HIDDEN   = 0x02
    FILE_ATTRIBUTE_SYSTEM   = 0x04
    FILE_ATTRIBUTE_ARCHIVE  = 0x020


    def  __init__(self, secret: Union[str, None] = None):
        self.c = wmi.WMI()

        if not isinstance(secret, str):
            raise TypeError(f"Object secret could be only string not {type(secret)}.")
        self.secret = secret or self._generate_secret()


    def _hash(self, pnp_id: str) -> str:
        return hashlib.sha256((pnp_id + (self.secret if self.secret else "")).encode()).hexdigest()


    def _hide_file(self, path: str):
        ctypes.windll.kernel32.SetFileAttributesW(path, self.FILE_ATTRIBUTE_HIDDEN)

    def _unhide_file(self, path: str):
        ctypes.windll.kernel32.SetFileAttributesW(path, self.FILE_ATTRIBUTE_NORMAL)


    def _get_machine_secret(self) -> str:
        with winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Microsoft\Cryptography"
        ) as key:
            guid, _ = winreg.QueryValueEx(key, "MachineGuid")

        return hashlib.sha256(guid.encode()).hexdigest()


    def _get_system_secret(self) -> str:
        data = (
            platform.node() +
            platform.processor() +
            str(uuid.getnode())
        )
        return hashlib.sha256(data.encode()).hexdigest()


    def _generate_secret_hex(self, bytes_len: int = 32) -> str:
        return secrets.token_hex(bytes_len)


    def _generate_secret(self) -> str:
        mode = 0
        while True:
            _mode = input("""
Выберите режим:
[1] - Сгенерировать *секрет* флешки
[2] - Ввести *секрет* флешки
[3] - *Секрет* флешки = HWID компьютера
[4] - *Секрет* флешки = HWID железа (меняется при апгрейде железа)
[5] - !!! Без *секрета* !!!

Ввод: """)
            try: _mode = int(_mode)
            except: continue
            if _mode < 1 or _mode > 5: continue

            mode = _mode; break

        secret = None
        if mode == 1:
            secret = self._generate_secret_hex()
        elif mode == 2:
            secret = input("\nВведите *секрет* (без повторной попытки; пусто=без секрета): ")
            if not secret:
                secret = None
        elif mode == 3:
            secret = self._get_machine_secret()
        elif mode == 4:
            secret = self._get_system_secret()
        elif mode == 5:
            secret = None

        return secret


    def find_usb_drives(self) -> list[tuple]:
        """
        Функция для поиска USB девайсов.
        
        :return: Возвращает список (drive_letter, pnp_id, volume_name)
        :rtype: list[tuple]
        """

        result = []
        for disk in self.c.Win32_DiskDrive(InterfaceType="USB"):
            for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
                for logical in partition.associators("Win32_LogicalDiskToPartition"):
                    result.append((logical.DeviceID + "\\", disk.PNPDeviceID, logical.VolumeName))

        return result


    def init_key(self, disk_id: Union[int, None] = None):
        """
        ОДИН РАЗ: создать ключ на флешке
        """
        if disk_id and not isinstance(disk_id, int):
            raise TypeError(f"Object disk_id could be only integer not {type(disk_id)}.")

        drives = self.find_usb_drives()
        if not drives:
            raise RuntimeError("USB флешка не найдена")

        print("\nВыберите диск:")
        i = 0
        for drive, _, volume_name in drives:
            print(f"[{i}]  =  {drive}  -  {volume_name}")
            i += 1

        if not disk_id:
            disk_id = 0
            while True:
                disk_id = input("\nВвод:  ")
                try: disk_id = int(disk_id)
                except: continue
                if disk_id < 0 or disk_id > len(drives)-1:
                    continue
                break

        drive, pnp_id, _ = drives[disk_id]
        key_path = os.path.join(drive, KEY_FILENAME)

        if os.path.exists(key_path):
            print("[WARNING] Ключ уже существует! Ожидание 5 секунд до перезаписи...")
            time.sleep(5)
            print("Перезапись...")
            self._unhide_file(key_path)

        key_hash = self._hash(pnp_id)
        with open(key_path, "w") as file:
            file.write(key_hash)

        self._hide_file(key_path)
        print(f"Ключ создан на [{drive}].")
        print(f"\nВаш секрет:  {self.secret}\n")


    def check_key(self) -> bool:
        """
        Проверка ключа
        
        :return: Статус проверки
        :rtype: bool
        """

        for drive, pnp_id, _ in self.find_usb_drives():
            key_path = os.path.join(drive, KEY_FILENAME)
            if not os.path.exists(key_path):
                continue

            with open(key_path, "r") as file:
                stored_hash = file.read().strip()

            if stored_hash == self._hash(pnp_id):
                return True

        return False
