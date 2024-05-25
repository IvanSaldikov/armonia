from __django_loader import load_django

load_django()

from notifications.utils.notification_manager import NotificationManager
from common.utils.rabbit_mq import RabbitMQ
from config.logger import get_module_logger

logger = get_module_logger("notificator")


class RabbitMQNotificationsCommandsHandler:

    @classmethod
    def listen_rabbit_mq_messages(cls):
        logger.info(f"Listening for RabbitMQ Notifications messages...")
        # connection = None
        # while not connection:
        logger.info(f"Setting up Rabbit MQ callback...")
        connection, channel = RabbitMQ.set_callback_function(queue_name=NotificationManager.RABBIT_MQ_QUEUE_NAME,
                                                             callback=cls._callback,
                                                             auto_ack=False,
                                                             )
        logger.info(f"Starting consumption messages from RabbitMQ...")
        channel.start_consuming()

    @classmethod
    def _callback(cls, ch, method, properties, body: bytes):
        message_id = int(body.decode())
        logger.info(f"Callback for Message ID: `{message_id=}`")
        NotificationManager.notify_all_connections(message_id=message_id)
        ch.basic_ack(delivery_tag=method.delivery_tag)
        logger.info(f"Notificator to Message ID {message_id=} has successfully finished its task")


if __name__ == "__main__":
    RabbitMQNotificationsCommandsHandler.listen_rabbit_mq_messages()
    # event_loop = asyncio.get_event_loop()
    # ch = RabbitMQCommandsHandler(event_loop)
    # event_loop.run_until_complete(ch.main())
