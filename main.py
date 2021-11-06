from __future__ import print_function
import tornado.ioloop
import tornado.web
import os
import json
import subprocess
import shlex
from tornado.web import URLSpec as url_spec
import boto3

# Let's use Amazon S3
s3 = boto3.resource('s3')


class MainHandler(tornado.web.RequestHandler):
    def post(self):
        data = json.loads(self.request.body)
        manifestURL = data.get('sourceURL')
        desContentIdentifier = data.get('destinationKey')

        ffmpeg_cmd = "ffmpeg -i \"" + manifestURL + "\" -c copy \"" +  desContentIdentifier+"\".mp4"
        command1 = shlex.split(ffmpeg_cmd)
        print(command1)
        p1 = subprocess.run(command1, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(p1.stdout)
        scenedetector_cmd = "scenedetect -i \"" +  desContentIdentifier+"\".mp4 detect-content list-scenes"
        command2 = shlex.split(scenedetector_cmd)
        p2 = subprocess.run(command2, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(p2.stdout)
        sceneFileName = "\"" + desContentIdentifier+ "\"-Scenes.csv"
        fsceneFileName = shlex.split(sceneFileName)
        data = open(fsceneFileName[0], 'rb')
        s3.Bucket('contentconverted').put_object(Key=fsceneFileName[0], Body=data)
        videoFileName = "\"" + desContentIdentifier+ "\".mp4"
        fvideoFileName = shlex.split(videoFileName)
        data = open(fvideoFileName[0], 'rb')
        s3.Bucket('contentconverted').put_object(Key=fvideoFileName[0], Body=data)
        #command3 = "rm \"" + desContentIdentifier + "\"*"
        #fcommand3 = shlex.split(command3)
        #print(fcommand3)
        #p3 = subprocess.run('ls -al' , stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #print(p3.stdout)
        self.write("Extracted Completed and content moved to S3")


def make_app():
    return tornado.web.Application([
        (r"/startscenedetection", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
