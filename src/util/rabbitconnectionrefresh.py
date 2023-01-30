import threading
import time
import schedule
import logging

class RabbitRefreshConnection:

    def __init__(self, consumer, publisher):

        self._logger = logging.getLogger(self.__class__.__name__)
        self.consumer = consumer
        self.publisher = publisher
        self.thread_test = threading.Thread(target=self.process)
        schedule.every().day.at("00:00").do(self.run_threaded, self.job)
        
    def start(self):
        self.thread_test.start()

    def job(self):
        self._logger.info("Refreshing RabbitMQ connection")
        self.consumer.close_connection()
        self.publisher.close_connection()

    def run_threaded(self,job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()


    def process(self):
        while 1:
            schedule.run_pending()
            time.sleep(1)
        