import pika
import retry

import configreader

class QueueWrapper:

    def __init__(self):
        self.__rabbitcfg = configreader.load_configs("RabbitMQ")
        self.__connection = None
        self.__channel = None

    def __open_blocking_connection(self):
        credentials = pika.PlainCredentials(
            username=self.__rabbitcfg.get("Username", "guest"),
            password=self.__rabbitcfg.get("Password", "guest"))

        connection_params = pika.ConnectionParameters(
            host=self.__rabbitcfg.get("Host", "localhost"),
            port=self.__rabbitcfg.get("Port", "5672"),
            credentials=credentials,
            heartbeat=0)

        print("Connecting to RabbitMQ")
        return pika.BlockingConnection(connection_params)

    def __close_blocking_connection(self):
        if self.__channel is not None:
            self.__channel.stop_consuming()
            self.__channel.close()

            try:
                self.__connection.close()
            except pika.exceptions.ConnectionWrongStateError:
                print("Connection already closed")

            self.__channel = None
            self.__connection = None

    @retry(pika.exceptions.AMQPConnectionError, delay=5, jitter=(1,5))
    def consume_from_queue(self, queue, on_message_callback):
        self.__connection = self.__open_blocking_connection()
        self.__channel = connection.channel()

        self.__channel.basic_qos(prefetch_count=1)
        self.__channel.queue_declare(queue, durable=True)
        self.__channel.basic_consume(queue, callback=on_message_callback)

        try:
            self.__channel.start_consuming()
        except pika.exceptions.ConnectionClosedByBroker:
            print("Connection closed by broker")
        except pika.exceptions.ReentrancyError:
            print("StartConsuming called from a invalid scope")
        except pika.exceptions.ChannelClosed:
            print("Channel closed by broker")
        finally:
            self.__close_blocking_connection()

    def publish_to_queue(self, route, payload, correlation_id):
        if self.__channel is not None:
            try:
                properties = pika.BasicProperties(correlation_id=correlation_id)
                self.__channel.basic_publish(
                    exchange="",
                    routing_key=route,
                    body=payload,
                    properties=properties)

            except pika.exceptions.UnroutableError:
                print("Unroutable message returned by the broker")
            except pika.exceptions.NackError:
                print("Message nack’ed by the broker")
