"""
   Copyright 2020 Yann Dumont

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""


__all__ = ("DeviceManager", )


from typing import Dict


class DeviceManagerError(Exception):
    pass


class DeviceManager:

    def __init__(self):
        self.__device_pool = dict()

    def set(self, device_id: str, data: dict) -> None:
        self.__device_pool[device_id] = data

    def delete(self, device_id: str) -> None:
        try:
            del self.__device_pool[device_id]
        except KeyError:
            raise DeviceManagerError("device '{}' not in pool".format(device_id))

    def get(self, device_id: str) -> dict:
        try:
            device = self.__device_pool[device_id]
        except KeyError:
            raise DeviceManagerError("device '{}' not in pool".format(device_id))
        return device

    def devices(self) -> Dict[str, dict]:
        devices = self.__device_pool.copy()
        return devices
