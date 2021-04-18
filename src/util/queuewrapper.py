import logging
import pika
from retry import retry

from util import configreader


class QueueWrapper:

    def __init__(self):
        self._logger = logging.getLogger(self.__class__.__name__)
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
            heartbeat=60)

        self._logger.debug("Creating a new blocking connection.")
        self._connection = pika.BlockingConnection(connection_params)

    def close_connection(self):
        self._logger.debug("Closing blocking connection.")
        if self._connection is not None:
            try:
                self._connection.close()
            except pika.exceptions.ConnectionWrongStateError:
                self._logger.debug("Blocking connection already closed.")


class ConsumeSingleton(QueueWrapper):

    _instance = None

    def __init__(self):
        super().__init__()
        self._logger.debug("Opening a new consumer connection.")
        self._configure_blocking_connection()
        self.channel = self._connection.channel()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


class PublisherSingleton(QueueWrapper):

    _instance = None

    def __init__(self):
        super().__init__()
        self._configure_blocking_connection()
        self.channel = self._connection.channel()

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance


class QueueConsumer(QueueWrapper):

    def __init__(self):
        super().__init__()

    @retry(pika.exceptions.AMQPConnectionError, delay=1, max_delay=5, jitter=1)
    def consume_from_queue(self, queue, callback):
        if self._connection is not None:
            if self._connection.is_open:
                try:
                    self._logger.debug("Closing consumer connection.")
                    self._connection.close()
                except pika.exceptions.ConnectionWrongStateError:
                    self._logger.debug("Consumer connection already closed.")

        self._logger.debug("Opening a new consumer channel.")
        test = ConsumeSingleton.instance()
        self._logger.debug("Declaring queue '{}'.".format(queue))

        test.channel.queue_declare(queue)

        prefetch = self._rabbitcfg.get("PrefetchCount", "1")
        self._logger.debug("Setting prefetch count to '{}'.".format(prefetch))
        test.channel.basic_qos(prefetch_count=int(prefetch))

        self._logger.debug("Starting consuming from queue '{}'.".format(queue))
        test.channel.basic_consume(queue, on_message_callback=callback)
        test.channel.start_consuming()


class QueuePublisher(QueueWrapper):

    def __init__(self):
        super().__init__()
        self.__channel = None
        self.test = PublisherSingleton.instance()

    @retry(pika.exceptions.AMQPConnectionError, tries=3, delay=1)
    def publish_to_queue(self, route, payload, correlation_id):
        if self._connection is None or self._connection.is_closed:
            self._logger.debug("Opening a new publisher connection.")
            self._configure_blocking_connection()

        if self.__channel is None or self.__channel.is_closed:
            self._logger.debug("Opening a new publisher channel.")
            self.__channel = self._connection.channel()

        self._logger.debug(
            "Publishing message in the route '{}'.".format(route))
        try:
            self.test.channel.basic_publish(
                exchange="",
                routing_key=route,
                body=payload,
                properties=pika.BasicProperties(correlation_id=correlation_id))

        except AssertionError:
            self._logger.error("Failed to publish message.")
