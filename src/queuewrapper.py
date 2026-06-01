import logging
import random
import time
from typing import Any, Callable

import pika
from pika.exceptions import (
    AMQPConnectionError,
    AMQPError,
    ConnectionClosedByBroker,
    StreamLostError,
    ConnectionWrongStateError,
)
from retry import retry

from config import settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def initialise_pika_connection(
    host: str,
    username: str,
    password: str,
    port: str | int = 5672,
    connection_attempts: int = 20,
    retry_delay_in_seconds: float = 5,
    heartbeat: int = 60,
) -> pika.BlockingConnection:
    """Create a Pika `BlockingConnection`.
    Args:
        host: Pika host
        username: username for authentication with Pika host
        password: password for authentication with Pika host
        port: port of the Pika host
        connection_attempts: number of channel attempts before giving up
        retry_delay_in_seconds: delay in seconds between channel attempts
        heartbeat: heartbeat delay in seconds
    Returns:
        Pika `BlockingConnection` with provided parameters
    """

    import pika

    parameters = _get_pika_parameters(
        host,
        username,
        password,
        port,
        connection_attempts,
        retry_delay_in_seconds,
        heartbeat,
    )
    return pika.BlockingConnection(parameters)


def _get_pika_parameters(
    host: str,
    username: str,
    password: str,
    port: str | int = 5672,
    connection_attempts: int = 20,
    retry_delay_in_seconds: float = 5,
    heartbeat: int = 60,
) -> pika.ConnectionParameters | pika.URLParameters:
    """Create Pika `Parameters`.
    Args:
        host: Pika host
        username: username for authentication with Pika host
        password: password for authentication with Pika host
        port: port of the Pika host
        connection_attempts: number of channel attempts before giving up
        retry_delay_in_seconds: delay in seconds between channel attempts
        heartbeat: heartbeat delay in seconds
    Returns:
        Pika `Paramaters` which can be used to create a new connection to a broker.
    """

    import pika

    if host.startswith("amqp"):
        # user supplied a amqp url containing all the info
        parameters = pika.URLParameters(host)
        parameters.connection_attempts = connection_attempts
        parameters.retry_delay = retry_delay_in_seconds
        parameters.heartbeat = heartbeat
        if username:
            parameters.credentials = pika.PlainCredentials(username, password)
    else:
        # host seems to be just the host, so we use our parameters
        parameters = pika.ConnectionParameters(
            host,
            port=port,
            credentials=pika.PlainCredentials(username, password),
            connection_attempts=connection_attempts,
            retry_delay=retry_delay_in_seconds,
            heartbeat=heartbeat,
        )

    return parameters


def close_pika_channel(channel) -> None:
    """Attempt to close Pika channel."""

    try:
        channel.close()
        logger.debug("Successfully closed Pika channel.")
    except AMQPError:
        logger.exception("Failed to close Pika channel.")


def close_pika_connection(connection: pika.BlockingConnection) -> None:
    """Attempt to close Pika connection."""

    try:
        connection.close()
        logger.debug("Successfully closed Pika connection with host.")
    except (AMQPError, ConnectionWrongStateError):
        logger.exception("Failed to close Pika connection with host.")


class QueueWrapper:
    """A Pika based rabbitmq client."""

    def __init__(
        self,
        host: str = settings.AMQP_HOST,
        username: str = settings.AMQP_USER,
        password: str = settings.AMQP_PASS,
        port: str | int = settings.AMQP_PORT,
        heartbeat: int = settings.AMQP_HEART_BEAT,
        connection_attempts: int = 20,
        retry_delay_in_seconds: int = 5,
        prefetch: int = settings.AMQP_PREFETCH_COUNT,
        **kwargs: Any,
    ):

        self._host = host
        self._username = username
        self._password = password
        self._heartbeat = heartbeat
        self._connection_attempts = connection_attempts
        self._retry_delay_in_seconds = retry_delay_in_seconds
        self._prefetch = prefetch

        try:
            self._port = int(port)
        except ValueError:
            raise ValueError("Port could not be converted to integer.")

        self._connection = None

    def _reset_connection(self) -> None:
        self.close_connection()
        self._connection = None

    def _configure_blocking_connection(self):
        """Initialize RabbitMQ connection"""

        logger.debug("Creating a new blocking connection.")
        self._connection = initialise_pika_connection(
            host=self._host,
            username=self._username,
            password=self._password,
            port=self._port,
            connection_attempts=self._connection_attempts,
            retry_delay_in_seconds=self._retry_delay_in_seconds,
            heartbeat=self._heartbeat,
        )
        logger.info("AMQP connection established with host '%s:%s'.", self._host, self._port)

    def close_connection(self):
        logger.debug("Closing blocking connection.")
        if self._connection is not None and not self._connection.is_closed:
            close_pika_connection(self._connection)


class QueueConsumer(QueueWrapper):
    def __init__(self):
        super().__init__()
        self._channel = None
        self._should_stop = False

    def _reset_channel(self) -> None:
        if self._channel is not None and self._channel.is_open:
            close_pika_channel(self._channel)
        self._channel = None

    def _configure_blocking_channel(self, queue: str) -> None:
        self._channel = self._connection.channel()
        self._channel.queue_declare(queue, durable=False)
        self._channel.basic_qos(prefetch_count=self._prefetch)

    def consume_from_queue(self, queue: str, callback: Callable) -> None:
        self._should_stop = False
        retry_delay = 1.0

        while not self._should_stop:
            try:
                logger.debug("Starting AMQP consumer for queue '%s'.", queue)
                self._reset_channel()
                self._reset_connection()

                self._configure_blocking_connection()
                self._configure_blocking_channel(queue)
                logger.info("AMQP consumer reconnected and ready for queue '%s'.", queue)
                retry_delay = 1.0

                self._channel.basic_consume(queue, on_message_callback=callback)
                self._channel.start_consuming()
            except (
                AMQPConnectionError,
                ConnectionClosedByBroker,
                ConnectionWrongStateError,
                StreamLostError,
            ) as error:
                if self._should_stop:
                    logger.info("Consumer stop requested. Closing AMQP consumer loop.")
                    break
                logger.warning("AMQP consumer connection lost. Reconnecting: %s", error)
                sleep_for = retry_delay + random.uniform(0, 1)
                logger.info("Retrying AMQP consumer connection in %.2f seconds.", sleep_for)
                time.sleep(sleep_for)
                retry_delay = min(retry_delay * 2, 8.0)
            finally:
                self._reset_channel()
                self._reset_connection()

    def stop_consuming(self) -> None:
        self._should_stop = True

        if self._connection is not None and self._connection.is_open:
            self._connection.add_callback_threadsafe(self._stop_consuming_callback)

    def _stop_consuming_callback(self) -> None:
        if self._channel is not None and self._channel.is_open:
            self._channel.stop_consuming()


class QueuePublisher(QueueWrapper):
    def __init__(self):
        super().__init__()
        self._channel = None

    def _configure_blocking_channel(self) -> None:
        if self._channel is None or self._channel.is_closed:
            logger.debug("Opening a new publisher channel.")
            self._channel = self._connection.channel()

    def _reset_channel(self) -> None:
        if self._channel is not None and self._channel.is_open:
            close_pika_channel(self._channel)
        self._channel = None

    @retry(
        (AMQPConnectionError, StreamLostError, ConnectionWrongStateError),
        tries=5,
        delay=1,
        max_delay=8,
        backoff=2,
        jitter=(0, 1),
    )
    def publish_to_queue(self, route: str, payload: dict[str, Any], id: str) -> None:
        if self._connection is None or self._connection.is_closed:
            # Try to reset connection
            logger.debug("Opening a new publisher connection.")
            self._configure_blocking_connection()

        # If we got an open connection process data event
        # to ensure the connection is still alive
        try:
            self._connection.process_data_events(0)
        except ConnectionClosedByBroker as error:
            logger.warning(
                "Publisher connection was closed by broker. Reconnecting: %s",
                error,
            )
            self._reset_channel()
            self._configure_blocking_connection()
        except (AMQPConnectionError, StreamLostError, ConnectionWrongStateError) as error:
            logger.warning("Publisher connection was lost. Reconnecting: %s", error)
            self._reset_channel()
            self._configure_blocking_connection()

        self._configure_blocking_channel()
        logger.info("AMQP publisher connection ready for route '%s'.", route)

        logger.debug(f"Publishing message in the route '{route}'.")
        try:
            self._channel.basic_publish(
                exchange="",
                routing_key=route,
                body=payload,
                properties=pika.BasicProperties(correlation_id=id)
            )

        except (
            AMQPConnectionError,
            AMQPError,
            AssertionError,
            StreamLostError,
            ConnectionWrongStateError,
        ):
            self._reset_channel()
            self._reset_connection()
            logger.error("Failed to publish message.")
            raise
