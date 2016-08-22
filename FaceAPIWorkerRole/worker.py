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

    def __init__(self, account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY, workerrole=False):
        self.account_key = account_key
        self.account_name = account_name
        self.workerrole = workerrole
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
        
        if message.content == "test":
            return {}
        message_content = json.loads(message.content)
        return message_content

    def delete_last_images(self, message_content):
        self.blob.delete_blob(message_content['container_name'], message_content['name'])

    def __len__(self):
        return self.queue.get_queue_metadata(self.queue_name).approximate_message_count


class CognativeServicesWrapper(object):

    api_endpoint = "https://api.projectoxford.ai/face/v1.0/detect?returnFaceId=true&returnFaceLandmarks=true&returnFaceAttributes=age,gender,smile,facialHair,headPose,glasses"
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
        return "https://{}.blob.core.windows.net/{}/{}".format(image_dict['blobname'], image_dict['containername'], image_dict['name'])

    def hit_api(self):
        post_data = json.dumps({"url": self.image_target})
        header_data = {
            "Ocp-Apim-Subscription-Key": self.api_key
        }
        response = requests.post(self.api_endpoint, data=post_data, headers=header_data)
        return response.json()


def process(imagequeue):
    image = imagequeue.get_image()
    if image:
        COG = CognativeServicesWrapper(image)
        results = COG.hit_api()
        if len(results):
            # There are people in this photo
            pass
        else:
            # There are no people in this photo
            pass
        # Okay, just chill for a second
        sleep(1)
    else:
        # Poison? Just wait it out.
        sleep(5)


if __name__ == '__main__':
    IQ = ImageQueue()
    while True:
        process(IQ)