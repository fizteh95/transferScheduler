import os


# как часто ходим в базу за не обновленными группами
VK_UPDATE_INTERVAL: int = int(os.getenv('VK_UPDATE_INTERVAL') or 10)
# перерыв между запросами к вк
VK_CHECK_INTERVAL: int = int(os.getenv('VK_UPDATE_INTERVAL') or 20)

RABBIT_ADDRESS: str = os.getenv('RABBIT_ADDRESS') or 'amqp://guest:guest@rabbitmq:5672'
RABBIT_READING_QUEUE: str = os.getenv('RABBIT_READING_QUEUE') or 'reading_queue'
RABBIT_SENDING_QUEUE: str = os.getenv('RABBIT_SENDING_QUEUE') or 'sending_queue'

# как часто проверяем новые сообщения для каналов
TG_UPDATE_INTERVAL: int = int(os.getenv('TG_UPDATE_INTERVAL') or 40)
