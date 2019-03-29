#!/usr/bin/env python3

import json

import PortGlosa

from utils import configreader
from utils import queuewrapper

class Worker:

    def __init__(self):
        self.__queue_wrapper = queuewrapper.QueueWrapper()

    def __process_message(self, channel, method, properties, body):
        try:
            payload = json.loads(body)
            print("[+] Translating... ", end='')
            translation = PortGlosa.traduzir(payload.get("text", ""))
            print("\033[92mdone\033[0m")

            self.__queue_wrapper.send_to_queue(
                properties.correlation_id,
                properties.reply_to, 
                json.dumps({ "translation": translation }))

            channel.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError as error:
            self.__queue_wrapper.send_to_queue(
                properties.correlation_id,
                properties.reply_to,
                json.dumps({ "error": str(error) }))

            channel.basic_nack(delivery_tag=method.delivery_tag)

    def start_consuming(self, queue):
        self.__queue_wrapper.consume_from_queue(queue, self.__process_message)

    def stop_consuming(self):
        self.__queue_wrapper.close_connection()

if __name__ == "__main__":

    workercfg = configreader.load_configs("Worker")

    if workercfg is None:
        print("[!] Could not load configs")
        raise SystemExit(1)

    try:
        worker = Worker()
        print("[*] Translation Worker Started")
        print("[*] Press CTRL+C to Exit\n")
        worker.start_consuming(workercfg.get("WorkerQueue"))

    except KeyboardInterrupt:
        print("[*] Exiting...")
        worker.stop_consuming()
        raise SystemExit(0)
    