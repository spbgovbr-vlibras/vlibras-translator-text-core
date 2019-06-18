import pika
from retry import retry

from utils import configreader

class QueueWrapper:

    def __init__(self):
        self._rabbitcfg = configreader.load_configs("RabbitMQ")
        self._connection = None

    def _configure_blocking_connection(self):
        credentials = pika.PlainCredentials(
            username=self._rabbitcfg.get("Username", "guest"),
            password=self._rabbitcfg.get("Password", "guest"))

        connection_params = pika.ConnectionParameters(
            host=self._rabbitcfg.get("Host", "localhost"),
            port=self._rabbitcfg.get("Port", "5672"),
            credentials=credentials,
            heartbeat=0)

        print("Connecting to RabbitMQ")
        self._connection = pika.BlockingConnection(connection_params)

    def close_connection(self):
        if self._connection is not None:
            try:
                self._connection.close()
            except pika.exceptions.ConnectionWrongStateError:
                print("Connection already closed")

class QueueConsumer(QueueWrapper):

    def __init__(self):
        super().__init__()

    @retry(pika.exceptions.AMQPConnectionError, delay=1, max_delay=5, jitter=1)
    def consume_from_queue(self, queue, callback):
        if self._connection is not None:
            if self._connection.is_open:
                self._connection.close()

        self._configure_blocking_connection()
        channel = self._connection.channel()

        channel.queue_declare(queue)
        channel.basic_consume(
            queue, 
            on_message_callback=callback, 
            auto_ack=True)
        channel.start_consuming()

class QueuePublisher(QueueWrapper):

    def __init__(self):
        super().__init__()
        self.__channel = None

    @retry(pika.exceptions.AMQPConnectionError, tries=3, delay=1)
    def publish_to_queue(self, route, payload, correlation_id):
        if self._connection is None or self._connection.is_closed:
            self._configure_blocking_connection()

        if self.__channel is None or self.__channel.is_closed:
            self.__channel = self._connection.channel()

        self.__channel.basic_publish(
            exchange="",
            routing_key=route,
            body=payload,
            properties=pika.BasicProperties(correlation_id=correlation_id))