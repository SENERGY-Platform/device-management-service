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

__all__ = ("genRegExp", "matchTopic", "setOffline")


from .manager import DeviceManager
from .model import DeviceState
import re


def genRegExp(topic: str):
    topic = topic.replace("/", "\/")
    if topic.endswith("+"):
        topic = topic.rstrip("+")
        topic = topic + "[^\/]*"
    topic = topic.replace("+", ".*")
    topic = topic.replace("#", ".*")
    return r"{}$".format(topic)


def matchTopic(topic: str, regex):
    if re.fullmatch(regex, topic):
        return True
    return False


def setOffline(dm: DeviceManager, mod_id):
    devices = dm.devices()
    for key, data in devices.items():
        if data["module_id"] == mod_id:
            data["state"] = DeviceState.offline
            dm.set(key, data)
