#!/usr/bin/env python
from nudenet import NudeClassifier
from keys import *
from config import *
import praw
import urllib.request
import sqlite3
import re
import os

global reddit
global config

#enter user and app info here
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent='NSFW tagger bot v1.0.0',
                     username=username,
                     password=password)

def main(SUBREDDIT_NAMES): 
    tempjpg = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'temp.jpg')  
    classifier = NudeClassifier()
    valid_extensions = ['.jpg', '.jpeg', '.bmp', '.png', '.tiff']
    SUBREDDIT_NAMES = SUBREDDIT_NAMES.replace(',','+').replace(' ', '')    
    while True:  
        con = sqlite3.connect('log.db')
        cur = con.cursor()
        try:

            for submission in reddit.subreddit(SUBREDDIT_NAMES).stream.submissions():          
                                
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
                            gallery.append(url)
                        except KeyError:
                            pass
                #normal image url
                else:
                    gallery.append(URL)

                for i in gallery:
                    isimage = False
                    if i.endswith(tuple(valid_extensions)):
                        isimage = True
                    if isimage == True:
                        try:
                            #save image as temp file
                            with urllib.request.urlopen(i) as url:
                                with open(tempjpg, 'wb') as f:
                                    f.write(url.read())
                                    f.close()
                        except Exception as err:
                            print(err)

                        prediction = classifier.classify(tempjpg)[tempjpg]['unsafe']
                        #remove post if REMOVE_SUBMISSION is True
                        if prediction > NSFW_PROB_THRESHOLD:
                            #print("nsfw")
                            if LOGGING_ON:
                                cur.execute("INSERT INTO logbook VALUES (?,?,?)", (submission.created_utc, str(submission.author), submission.permalink))
                                con.commit()
                            if not MOD_TEST:
                                submission.mod.nsfw()
                                if REMOVE_SUBMISSION:
                                    submission.mod.remove()
                                    submission.mod.send_removal_message(REMOVAL_MESSAGE)                
                            #send mod mail to mod discussions for testing
                            else:
                                submission.subreddit.message("NSFW image detected!", "post: "+submission.permalink+' p = '+str(prediction)+', threshold is currently '+str(NSFW_PROB_THRESHOLD))
                            break                    
                        else:
                            #print("notnsfw")
                            pass

        except Exception as err:
            con.close()
            print(err)

    con.close()
                
if __name__ == "__main__":
    main(SUBREDDIT_NAMES)
