import json
from time import sleep

from azure.storage.blob import BlockBlobService
from azure.storage.queue import QueueService

from secrets import ACCOUNT_KEY, ACCOUNT_NAME


class ImageQueue(object):

    queue_name = "imagesqueue"
    container_name = "unsorted-images"
    max_unsorted_allowed = 50

    def __init__(self, account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY, workerrole=False):
        self.account_key = account_key
        self.account_name = account_name
        self.workerrole = workerrole
        self.dequeued = []
        self.init_queue()
        self.init_blob()

    def init_blob(self):
        self.blob = BlockBlobService(account_name=self.account_name, account_key=self.account_key)
        self.blob.create_container(self.container_name)

    def init_queue(self):
        self.queue = QueueService(account_name=self.account_name, account_key=self.account_key)
        self.queue.create_queue(self.queue_name)

    def peek(self):
        return [x.content for x in self.queue.peek_messages(self.queue_name)]

    def get_image(self):
        message = json.loads(self.queue.get_messages(self.queue_name, num_messages=1)[0])
        self.queue.delete_message(self.queue_name, message.id, message.pop_receipt)
        if len(self.dequeued) > self.max_unsorted_allowed:
            self.delete_last_images()
        self.dequeued.append(message.content)

        return message.content

    def delete_last_images(self):
        for item in self.dequeued:
            self.blob.delete_blob(self.container_name, item['name'])
        self.dequeued = []

    def __len__(self):
        return self.queue.get_queue_metadata(self.queue_name).approximate_message_count




if __name__ == '__main__':
    IQ = ImageQueue()
    while True:
        if len(IQ) == 0:
            # if there's no work. Take a nap for 5 seconds
            sleep(5)
        else:
            image = IQ.get_image()

        #
        # Write your worker process here.
        #
        # You will probably want to call a blocking function such as
        #    bus_service.receive_queue_message('queue name', timeout=seconds)
        # to avoid consuming 100% CPU time while your worker has no work.
        #
        sleep(1.0)
