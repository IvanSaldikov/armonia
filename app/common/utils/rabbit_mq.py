import os
from typing import Callable, Tuple, Any

import pika
from pika import BlockingConnection, PlainCredentials
from pika.adapters.blocking_connection import BlockingChannel


class RabbitMQ:
    is_queue_durable = True

    @classmethod
    def send_message_to_rabbit_mq(cls, queue_name: str, data: Any, exchange_name: str = "") -> None:
        connection, channel = cls._set_up_connection_and_channel(queue_name=queue_name)
        # in case of durable queue we need to mark messages as PERSISTENT
        # https://www.rabbitmq.com/tutorials/tutorial-two-python.html
        if cls.is_queue_durable:
            props = pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVERY_MODE
                )
        else:
            props = None
        convertable_types = {int,
                             }
        if type(data) in convertable_types:
            data = str(data)
        channel.basic_publish(exchange=exchange_name,
                              routing_key=queue_name,
                              body=data,
                              properties=props,
                              )
        connection.close()

    @classmethod
    def set_callback_function(cls, queue_name: str,
                              callback: Callable,
                              auto_ack: bool = True,
                              ) -> Tuple[BlockingConnection, BlockingChannel]:
        connection, channel = cls._set_up_connection_and_channel(queue_name=queue_name)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue_name,
                              on_message_callback=callback,
                              auto_ack=auto_ack,
                              )
        return connection, channel

    @classmethod
    def _set_up_connection_and_channel(cls, queue_name: str) -> Tuple[BlockingConnection, BlockingChannel]:
        # https://pika.readthedocs.io/en/stable/examples/heartbeat_and_blocked_timeouts.html
        creds = PlainCredentials(username=os.environ.get("RABBITMQ_DEFAULT_USER", "guest"),
                                 password=os.environ.get("RABBITMQ_DEFAULT_PASS", "guest"),
                                 )
        connection = BlockingConnection(pika.ConnectionParameters(host=cls._get_host(),
                                                                  credentials=creds,
                                                                  heartbeat=200,
                                                                  blocked_connection_timeout=100,
                                                                  )
                                        )
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=cls.is_queue_durable)
        return connection, channel

    @staticmethod
    def _get_host():
        return os.environ.get("RABBITMQ_HOST", "rabbitmq")
