from azure.storage.blob import AppendBlobService, BlockBlobService
from azure.storage.queue import QueueService

from secrets import ACCOUNT_KEY, ACCOUNT_NAME


class ImageQueue(object):

    queue_name = "imagesqueue"
    blob_name = "unsorted-images"

    def __init__(self, account_name, account_key):
        self.account_key = account_key
        self.account_name = account_name
        self.init_queue()
        self.init_blob()


    def init_blob(self):
        self.blob = BlockBlobService(account_name=self.account_name, account_key=self.account_key)
        self.blob.create_container(self.blob_name)


    def init_queue(self):
        self.queue = QueueService(account_name=self.account_name, account_key=self.account_key)
        self.queue.create_queue(self.queue_name)

    def peek(self):
        return [x.content for x in self.queue.peek_messages(self.queue_name)]

    def new_image(self, django_image):
        self.blob.create_blob_from_bytes(self.container_name, django_image.name, contents)



def main():
    status = ImageQueue(ACCOUNT_NAME, ACCOUNT_KEY)
