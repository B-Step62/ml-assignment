import logging
import os
import pika
import time


class TaskQueue:
    MAX_CONN_RETRY = 3
    QUEUE_NAME = "task_queue"

    def __init__(self):
        self.conn = None
        self.connect()
            
        self.channel = self.conn.channel()
        self.channel.queue_declare(queue=self.QUEUE_NAME, durable=True)
    
    
    def connect(self):
        retry = 0
        while retry < self.MAX_CONN_RETRY:
            try:
                credentials = pika.PlainCredentials(
                    os.environ.get("RABBITMQ_USER"),
                    os.environ.get("RABBITMQ_PASSWORD")
                )
                self.conn = pika.BlockingConnection(pika.ConnectionParameters(
                    host=os.environ.get("RABBITMQ_HOST"),
                    port=os.environ.get("RABBITMQ_PORT"),
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
        self.channel.basic_consume(queue=self.QUEUE_NAME, on_message_callback=callback)
        
        self.channel.start_consuming()
