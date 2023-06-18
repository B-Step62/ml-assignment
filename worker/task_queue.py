import logging
import pika
import time

MAX_CONN_RETRY = 3
RABBITMQ_HOST = "rabbitmq"
RABBITMQ_PORT = 5672
RABBITMQ_QUEUE = "task_queue"
# Writing credential inline for convenience. This must be stored in a secure place in production.
RABBITMQ_USER = "test"
RABBITMQ_PASSWORD = "test"

class TaskQueue:
    def __init__(self):
        self.conn = None
        self.connect()
            
        self.channel = self.conn.channel()
        self.channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    
    
    def connect(self):
        retry = 0
        while retry < MAX_CONN_RETRY:
            try:
                credentials = pika.PlainCredentials('test', 'test')
                self.conn = pika.BlockingConnection(pika.ConnectionParameters(
                    host=RABBITMQ_HOST,
                    port=RABBITMQ_PORT,
                    credentials=credentials)
                )
                return
            except:
                # Sometimes worker container may start before RabbitMQ server accepts connection.
                # https://github.com/pika/pika/issues/1318
                logging.warn("Failed to connect to RabbitMQ. Retrying after 10 sec...")
                time.sleep(10) 
                retry += 1
                
    def consume(self, callback):
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
        
        self.channel.start_consuming()
        
    def publish(self, body: str):
        self.channel.basic_publish(exchange="", routing_key=RABBITMQ_QUEUE, body=body)
