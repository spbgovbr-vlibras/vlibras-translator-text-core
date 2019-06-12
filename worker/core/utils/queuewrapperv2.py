import pika

import configreader

class QueueWrapper:

    def __init__(self):
        self.__rabbitcfg = configreader.load_configs("RabbitMQ")

    def __open_asynchronous_connection(self):
        credentials = pika.PlainCredentials(
            self.__rabbitcfg.get("Username", "guest"),
            self.__rabbitcfg.get("Password", "guest"))

        connection_params = pika.ConnectionParameters(
            host=self.__rabbitcfg.get("Host", "localhost"),
            port=self.__rabbitcfg.get("Port", "5672"),
            credentials=credentials,
            heartbeat=0)

        print("Connecting to RabbitMQ")
        return pika.SelectConnection(
            parameters=connection_params,
            on_open_callback=self.__on_connection_open,
            on_open_error_callback=self.__on_connection_open_error,
            on_close_callback=self.__on_connection_closed)

     def __close_asynchronous_connection(self):
        print("Closing connection with RabbitMQ")
        if not (self.__connection.is_closing or self.__connection.is_closed):
            self.__connection.close()

    def __on_connection_open(self, _unused_connection):
        print("Creating a new channel")
        self.__connection.channel(on_open_callback=self.__on_channel_open)

    def __on_connection_open_error(self, _unused_connection, error):
        print("Connection open failed: %s", error)
        self.__stop()

    def __on_connection_closed(self, _unused_connection, error):
        print("Connection closed, reconnect necessary: %s", error)
        self.__channel = None
        self.__stop()

    def __on_channel_open(self, channel):
        print("Channel opened")
        self.__channel = channel
        self.__channel.add_on_close_callback(self.__on_channel_closed)
        self.__setup_queue()

    def __on_channel_closed(self, _unused_channel, error):
        print("Channel was closed")
        self.__close_asynchronous_connection()

    def __setup_queue(self):
        print("Declaring queue translate.to_text")
        self.__channel.queue_declare(
            queue="translate.to_text",
            durable=True
            callback=self.__on_queue_declareok)

    def __on_queue_declareok(self, _unused_frame):
        self.__channel.basic_qos(
            prefetch_count=1,
            callback=self.__on_basic_qos_ok)

    def __on_basic_qos_ok(self, _unused_frame):
        print("QOS set to: 1")
        self.__start_consuming()

    def __start_consuming(self):
        print("Adding consumer cancellation callback")
        self.__channel.add_on_cancel_callback(self.__on_consumer_cancelled)
        self._consumer_tag = self.__channel.basic_consume(
            queue="translate.to_text", 
            callback=self.__on_message)

    def __on_consumer_cancelled(self, method_frame):
        print("Consumer was cancelled remotely, shutting down: %r", method_frame)
        if self.__channel:
            self.__channel.close()

    def __stop_consuming(self):
        if self.__channel:
            self.__channel.basic_cancel(
                consumer_tag=self.__consumer_tag,
                callback=self.__on_cancelok)

    def __on_cancelok(self, _unused_frame):
        print("RabbitMQ acknowledged the cancellation of the consumer")
        self.__channel.close()

    def consume_from_queue(self):
        self.__connection = self.__open_asynchronous_connection()
        self.__connection.ioloop.start()