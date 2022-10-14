#!/usr/bin/env python
from xml.etree.ElementTree import Comment
from keys import *
from config import *
import praw
import urllib.request
import sqlite3
import re
import os, shutil

from transformers import pipeline
from PIL import Image
import requests

pipe = pipeline("image-classification", "umm-maybe/AI-image-detector")

global reddit
global config

#enter user and app info here
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent='AI tagger bot v0.0.1',
                     username=username,
                     password=password)

def is_image(url):
    valid_extensions = ['.jpg', '.jpeg', '.bmp', '.png', '.tiff']
    isimage = False
    if url.endswith(tuple(valid_extensions)):
        isimage = True
    return isimage

def main(SUBREDDIT_NAMES):
    tempjpg = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp.jpg')
    SUBREDDIT_NAMES = SUBREDDIT_NAMES.replace(',','+').replace(' ', '')
    while True:
        con = sqlite3.connect('log.db')
        cur = con.cursor()
        try:
            for submission in reddit.subreddit(SUBREDDIT_NAMES).stream.submissions(pause_after=0, skip_existing=True):
                if submission:
                    print(f"Analyzing submission titled '{submission.title}'")
                    gallery = []
                    URL = submission.url
                    #add .jpg to image link if its an imgur link
                    if 'imgur.com' in URL:
                        URL += '.jpg'
                        gallery.append(URL)
                    #get inidividual images from gallery
                    elif 'reddit.com/gallery' in URL:
                        ids = [i['media_id'] for i in submission.gallery_data['items']]
                        for i in ids:
                            try:
                                url = submission.media_metadata[i]['p'][0]['u']
                                url = url.split("?")[0].replace("preview", "i")
                                if is_image(url):
                                    gallery.append(url)
                            except KeyError:
                                pass
                    #normal image url
                    else:
                        if is_image(URL):
                            gallery.append(URL)

                    for url in gallery:
                        image = Image.open(requests.get(url, stream=True).raw)
                        outputs = pipe(image)
                        results = {}
                        for result in outputs:
                            results[result['label']] = result['score']
                        #remove post if REMOVE_SUBMISSION is True
                        if results['artificial'] > AI_PROB_THRESHOLD: 
                            print("artificial")
                            if LOGGING_ON:
                                cur.execute("INSERT INTO logbook VALUES (?,?,?)", (submission.created_utc, str(submission.author), submission.permalink))
                                con.commit()
                            if not MOD_TEST:
                                if REMOVE_SUBMISSION:
                                    submission.mod.remove()
                                    submission.mod.send_removal_message(REMOVAL_MESSAGE)
                            #send mod mail to mod discussions for testing
                            else:
                                submission.subreddit.message("AI-generated image detected!", "post: "+submission.permalink+' p = '+str(prediction)+', threshold is currently '+str(AI_PROB_THRESHOLD))
                                commentStr = "I think that this post contains an AI-generated image... I'm about "+str(round(100*results['artificial'],1))+r"% sure."
                                submission.reply(body=commentStr)
                            break
                        else:
                            print("notAI")
                            # commentStr = "I think that this post doesn't contain any AI-generated images... I'm about "+str(round(100*results['human'],1))+r"% sure."
                            # submission.reply(body=commentStr)
                            pass
            # shutil.rmtree('gallery')
        except Exception as err:
            con.close()
            print('Error getting submission stream:')
            print(err)

    con.close()

if __name__ == "__main__":
    main(SUBREDDIT_NAMES)
