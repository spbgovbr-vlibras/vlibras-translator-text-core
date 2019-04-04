import pika

from utils import configreader

class QueueWrapper:

    def __init__(self):
        self.__rabbitcfg = configreader.load_configs("RabbitMQ")
        self.__add_credentials()
        self.__configure_blocking_connection()
        self.__configure_channel()

    def __add_credentials(self):
        self.__credentials = pika.PlainCredentials(
            self.__rabbitcfg.get("Username"),
            self.__rabbitcfg.get("Password"))

    def __configure_blocking_connection(self):
        connection_params = pika.ConnectionParameters(
            host=self.__rabbitcfg.get("Host"),
            port=self.__rabbitcfg.get("Port"),
            credentials=self.__credentials,
            heartbeat=0)

        self.__connection = pika.BlockingConnection(connection_params)

    def __configure_channel(self):
        self.__channel = None

        MAX_ATTEMPTS = 3

        for attempts in range(MAX_ATTEMPTS):
            try:
                self.__channel = self.__connection.channel()
                break
            except:
                self.__reload_connection()
                print("Channel setup failed: Attempt(" + str(attempts) + ")")

    def __reload_connection(self):
        try:
            self.__connection.close(reply_text="Reloading Connection")
        finally:
            self.__configure_blocking_connection()

    def send_to_queue(self, id, route, payload):
        if self.__channel is not None:
            try:
                self.__channel.publish(
                    exchange="",
                    properties=pika.BasicProperties(correlation_id=id),
                    routing_key=route,
                    body=payload)

            except (pika.exceptions.UnroutableError, pika.exceptions.NackError) as ex:
                self.close_connection()
                print("Broker error: " + str(ex))

    def consume_from_queue(self, queue, callback):
        if self.__channel is not None:
            self.__channel.queue_declare(queue=queue, durable=True)
            self.__channel.basic_qos(prefetch_count=1)
            self.__channel.basic_consume(callback, queue=queue, no_ack=False)

            try:
                self.__channel.start_consuming()
            except pika.exceptions.RecursionError as ex:
                self.close_connection()
                print("Channel RecursionError: " + str(ex))

    def close_connection(self):
        try:
            self.__channel.stop_consuming()
            self.__connection.close()
        except:
            print("Connection already closed")
