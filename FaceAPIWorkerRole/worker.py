import json
from time import sleep
import requests
import sys

from azure.storage.blob import BlockBlobService
from azure.storage.queue import QueueService

from secrets import ACCOUNT_KEY, ACCOUNT_NAME, COG_ACCOUNT_KEY


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
        try:
            message = self.queue.get_messages(self.queue_name, num_messages=1)[0]
        except IndexError:  # there is no message
            return {}
        self.queue.delete_message(self.queue_name, message.id, message.pop_receipt)
        if len(self.dequeued) > self.max_unsorted_allowed:
            self.delete_last_images()
        if message.content == "test":
            return {}
        message_content = json.loads(message.content)
        self.dequeued.append(message_content)
        return message_content

    def delete_last_images(self):
        for item in self.dequeued:
            self.blob.delete_blob(self.container_name, item['name'])
        self.dequeued = []

    def __len__(self):
        return self.queue.get_queue_metadata(self.queue_name).approximate_message_count


class CognativeServicesWrapper(object):

    api_endpoint = "https://api.projectoxford.ai/face/v1.0/detect"
    api_key = COG_ACCOUNT_KEY

    def __init__(self, image_dict):
        try:
            assert isinstance(image_dict, dict)
            assert 'name' in image_dict.keys()
            assert 'blobname' in image_dict.keys()
            assert 'containername' in image_dict.keys()
        except AssertionError as e:
            raise ValueError(e)

        self.image_target = self.to_uri(image_dict)

    def to_uri(self, image_dict):
        return "https://{}.blob.core.windows.net/{}/{}?returnFaceId=true&returnFaceLandmarks=true".format(image_dict['blobname'], image_dict['containername'], image_dict['name'])

    def hit_api(self):
        while True:
            post_data = json.dumps({"url": self.image_target})
            header_data = {
                "Ocp-Apim-Subscription-Key": self.api_key
            }
            response = requests.post(self.api_endpoint, data=post_data, headers=header_data)
            if json.loads(response) == []:
                continue
            return response


if __name__ == '__main__':
    input("Stop it.")
    IQ = ImageQueue()
    image = IQ.get_image()
    if image:
        COG = CognativeServicesWrapper(image)
        test = COG.hit_api()
        import pdb; pdb.set_trace()
    else:
        sys.exit()


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
