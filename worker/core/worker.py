#!/usr/bin/env python3

import json

import PortGlosa

from utils import configreader
from utils import queuewrapper

class Worker:

    def __init__(self):
        self.__consumer = queuewrapper.QueueConsumer()
        self.__publisher = queuewrapper.QueuePublisher()

    def __process_message(self, channel, method, properties, body):
        try:
            payload = json.loads(body)
            print("[+] Translating... ", end='')
            gloss = PortGlosa.traduzir(payload.get("text", ""))
            print("\033[92mdone\033[0m")

            self.__reply_message(
                route=properties.reply_to,
                message=json.dumps({ "translation": gloss }),
                id=properties.correlation_id)

        except json.JSONDecodeError:
            self.__reply_message(
                route=properties.reply_to,
                message=json.dumps({ "error": "Body is not a valid JSON" }),
                id=properties.correlation_id)

        except Exception as ex:
            print(str(ex))

    def __reply_message(self, route, message, id):
        if route is not None and id is not None:
            return self.__publisher.publish_to_queue(route, message, id)
        
        print("received invalid params")

    def start(self, queue):
        self.__consumer.consume_from_queue(queue, self.__process_message)

    def stop(self):
        self.__consumer.close_connection()
        self.__publisher.close_connection()

if __name__ == "__main__":

    workercfg = configreader.load_configs("Worker")

    if workercfg is None:
        print("[!] Could not load configs")
        raise SystemExit(1)

    try:
        worker = Worker()
        print("[*] Translation Worker Started")
        print("[*] Press CTRL+C to Exit\n")
        worker.start(workercfg.get("TranslatorQueue"))

    except KeyboardInterrupt:
        print("[*] Exiting...")
        worker.stop()
        raise SystemExit(0)
    