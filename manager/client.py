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

__all__ = ("Client", )


from .logger import getLogger, logging_levels
from .configuration import dm_conf
from .model import validator, ValidationError, Method
from .manager import DeviceManager, DeviceManagerError
from .util import genRegExp, matchTopic, setOffline
import paho.mqtt.client
import logging
import threading
import time
import json


logger = getLogger(__name__.split(".", 1)[-1])

mqtt_logger = logging.getLogger("mqtt-client")
mqtt_logger.setLevel(logging_levels.setdefault(dm_conf.Logger.mqtt_level, "info"))


device_topic_regex = genRegExp(dm_conf.Client.device_topic)
lw_topic_regex = genRegExp(dm_conf.Client.lw_topic)


class Client(threading.Thread):
    def __init__(self, dm: DeviceManager):
        super().__init__(name="client", daemon=True)
        self.__dm = dm
        self.__mqtt = paho.mqtt.client.Client(
            client_id=dm_conf.Client.name,
            clean_session=dm_conf.Client.clean_session
        )
        self.__mqtt.on_connect = self.__onConnect
        self.__mqtt.on_disconnect = self.__onDisconnect
        self.__mqtt.on_message = self.__onMessage
        self.__mqtt.enable_logger(mqtt_logger)
        self.__discon_count = 0

    def run(self) -> None:
        while True:
            try:
                self.__mqtt.connect(dm_conf.MB.host, dm_conf.MB.port, keepalive=dm_conf.Client.keep_alive)
            except Exception as ex:
                logger.error(
                    "could not connect to '{}' on '{}' - {}".format(dm_conf.MB.host, dm_conf.MB.port, ex)
                )
            try:
                self.__mqtt.loop_forever()
            except Exception as ex:
                logger.error("mqtt loop broke - {}".format(ex))
            time.sleep(dm_conf.Client.reconnect)

    def __onConnect(self, client, userdata, flags, rc):
        if rc == 0:
            self.__discon_count = 0
            logger.info("connected to '{}'".format(dm_conf.MB.host))
            self.__mqtt.subscribe(dm_conf.Client.device_topic)
            self.__mqtt.subscribe(dm_conf.Client.lw_topic)
        else:
            logger.error("could not connect to '{}' - {}".format(dm_conf.MB.host, paho.mqtt.client.connack_string(rc)))

    def __onDisconnect(self, client, userdata, rc):
        if self.__discon_count < 1:
            if rc == 0:
                logger.info("disconnected from '{}'".format(dm_conf.MB.host))
            else:
                logger.warning("disconnected from '{}' unexpectedly".format(dm_conf.MB.host))
            self.__discon_count += 1

    def __onMessage(self, client, userdata, message: paho.mqtt.client.MQTTMessage):
        if matchTopic(message.topic, device_topic_regex):
            try:
                mod_id = message.topic.split("/")[dm_conf.Client.lw_topic.split("/").index("+")]
                payload = json.loads(message.payload)
                validator(payload)
                logger.debug("method='{}' device_id='{}' module_id='{}'".format(payload["method"], payload["device_id"], mod_id))
                if payload["method"] == Method.set:
                    if not payload["data"]:
                        raise ValueError("missing data")
                    payload["data"]["module_id"] = mod_id
                    self.__dm.set(payload["device_id"], payload["data"])
                if payload["method"] == Method.delete:
                    self.__dm.delete(payload["device_id"])
            except ValueError as ex:
                logger.warning("malformed message - {}".format(ex))
            except DeviceManagerError as ex:
                logger.error("error handling device - {}".format(ex))
            except ValidationError:
                logger.warning("message could not be validated")
            except Exception as ex:
                logger.error("error handling message - {}".format(ex))
        elif matchTopic(message.topic, lw_topic_regex):
            try:
                mod_id = message.topic.split("/")[dm_conf.Client.lw_topic.split("/").index("+")]
                logger.debug("received lwt from module_id='{}'".format(mod_id))
                setOffline(self.__dm, mod_id)
            except DeviceManagerError as ex:
                logger.error("error handling device - {}".format(ex))
            except Exception as ex:
                logger.error("error handling message - {}".format(ex))
