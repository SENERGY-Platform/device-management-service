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

__all__ = ("DeviceState", "ValidationError", "validator")


class ValidationError(Exception):
    pass


class DeviceState:
    online = "online"
    offline = "offline"


class Method:
    set = "set"
    delete = "delete"


message = {
    "method": str,
    "device_id": str,
    "data": (dict, type(None))
}

data = {
    "name": str,
    "state": (str, type(None)),
    "device_type": str,
    "attributes": (list, type(None)),
}

attribute = {
    "key": str,
    "value": str,
}


def validate(candidate, model):
    if not isinstance(candidate, dict):
        raise ValidationError
    for key in candidate.keys():
        if key not in model.keys():
            raise ValidationError
    for key, typ in model.items():
        if key not in candidate:
            if not issubclass(type(None), typ):
                raise ValidationError
        elif not isinstance(candidate[key], typ):
            raise ValidationError


def validator(candidate):
    validate(candidate, message)
    if not candidate["method"] in Method.__dict__.values():
        raise ValidationError
    if "data" in candidate:
        validate(candidate["data"], data)
        if "state" in candidate["data"]:
            if not candidate["data"]["state"] in DeviceState.__dict__.values():
                raise ValidationError
        if "attributes" in candidate["data"]:
            for att in candidate["data"]["attributes"]:
                validate(att, attribute)
