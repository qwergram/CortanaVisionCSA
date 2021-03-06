﻿import json
import shutil
from time import sleep, time
import requests
import sys
from PIL import Image, ImageDraw

from azure.storage.blob import BlockBlobService
from azure.storage.queue import QueueService

from secrets import ACCOUNT_KEY, ACCOUNT_NAME, COG_ACCOUNT_KEY


class ImageQueue(object):

    queue_name = "imagesqueue"
    container_name = "unsorted-images"
    face_container = "has-face-images"
    no_face_container = "no-face-images"
    

    def __init__(self, account_name=ACCOUNT_NAME, account_key=ACCOUNT_KEY, workerrole=False):
        self.account_key = account_key
        self.account_name = account_name
        self.workerrole = workerrole
        self.last_image = None
        self.init_queue()
        self.init_blob()

    def init_blob(self):
        self.blob = BlockBlobService(account_name=self.account_name, account_key=self.account_key)
        self.blob.create_container(self.container_name)
        self.blob.create_container(self.face_container)
        self.blob.create_container(self.no_face_container)

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
        self.last_image = message_content
        return message_content

    def upload_image_to_face_container(self, container_name, path):
        if self.last_image is None: return None
        new_name = str(time()).replace('.', '') + '.' + path.split('.')[-1]
        self.blob.create_blob_from_path(container_name, new_name, path)
        self.delete_last_image()

    # http://goo.gl/XN9zkJ :)
    def move_image_to_no_face_container(self):
        if self.last_image is None: return None
        new_name = str(time()).replace('.', '') + '.' + self.last_image['name'].split('.')[-1]
        blob_url = self.blob.make_blob_url(self.last_image['containername'], self.last_image['name'])
        self.blob.copy_blob(self.no_face_container, new_name, blob_url)
        self.delete_last_image()

    def delete_last_image(self):
        self.blob.delete_blob(self.last_image['containername'], self.last_image['name'])
        self.last_image = None

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


def show_faces(image_target, results):
    image = requests.get(image_target, stream=True).raw
    image_ext = image_target.split('.')[-1]
    image_path = "image.{}".format(image_ext) 
    with open(image_path, "wb") as context:
        image.decode_content = True
        shutil.copyfileobj(image, context)
    im_obj = Image.open(image_path)
    pen = ImageDraw.Draw(im_obj)

    for person in results:
        height = person['faceRectangle']['height']
        width = person['faceRectangle']['width']
        left = person['faceRectangle']['left']
        top = person['faceRectangle']['top']
        print(person['faceRectangle'], person['faceAttributes']['gender'], person['faceAttributes']['age'])
        pen_color = "blue" if person['faceAttributes']['gender'] == "male" else "pink"
        pen.rectangle([left, top, left+ width, top + height], outline = pen_color)
        for point in person['faceLandmarks'].values():
            x, y = point['x'], point['y']
            pen.ellipse([x - 1, y - 1, x + 1, y + 1], fill = pen_color)

    # im_obj.show()
    im_obj.save('image.png', 'png')
    


def process(imagequeue):
    image = imagequeue.get_image()
    print(image)
    if image:
        COG = CognativeServicesWrapper(image)
        image_target = COG.image_target
        results = COG.hit_api()
        if len(results):
            print("Moving to face")
            show_faces(image_target, results)
            # There are people in this photo
            imagequeue.upload_image_to_face_container(imagequeue.face_container, "image.png")
        else:
            print("Moving to noface")
            # There are no people in this photo
            imagequeue.move_image_to_no_face_container()
        # Okay, just chill for a second
        sleep(1)
    else:
        # Poison? Just wait it out.
        sleep(5)


if __name__ == '__main__':
    # try:
    IQ = ImageQueue()
    while True:
        process(IQ)
    # except Exception as error:
    #     with open("C:\\Users\\v-nopeng\\AppData\\Roaming\\error.txt", 'w') as context:
    #         context.write(str(error))
