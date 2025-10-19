# 6.0001/6.00 Problem Set 5 - RSS Feed Filter
# Name:
# Collaborators:
# Time:

import feedparser
import string
import time
import threading
from project_util import translate_html
from mtTkinter import *
from datetime import datetime
import pytz


#-----------------------------------------------------------------------
#======================
# Code for retrieving and parsing
# Google and Yahoo News feeds
#======================

def process(url):
    """
    Fetches news items from the rss url and parses them.
    Returns a list of NewsStory-s.
    """
    feed = feedparser.parse(url)
    entries = feed.entries
    ret = []
    for entry in entries:
        guid = entry.guid
        title = translate_html(entry.title)
        link = entry.link
        description = translate_html(entry.description)
        pubdate = translate_html(entry.published)

        try:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %Z")
            pubdate.replace(tzinfo=pytz.timezone("GMT"))
        except ValueError:
            pubdate = datetime.strptime(pubdate, "%a, %d %b %Y %H:%M:%S %z")

        newsStory = NewsStory(guid, title, description, link, pubdate)
        ret.append(newsStory)
    return ret


#======================
# Data structure design
#======================

# Problem 1
class NewsStory:
    def __init__(self, guid, title, description, link, pubdate):
        self.guid = guid
        self.title = title
        self.description = description
        self.link = link
        self.pubdate = pubdate

    def get_guid(self):
        return self.guid

    def get_title(self):
        return self.title

    def get_description(self):
        return self.description

    def get_link(self):
        return self.link

    def get_pubdate(self):
        return self.pubdate


#======================
# Triggers
#======================

class Trigger(object):
    def evaluate(self, story):
        """
        Returns True if an alert should be generated
        for the given news item, or False otherwise.
        """
        raise NotImplementedError


#======================
# PHRASE TRIGGERS
#======================

# Problem 2
class PhraseTrigger(Trigger):
    def __init__(self, phrase):
        self.phrase = phrase.lower()

    def is_phrase_in(self, text):
        text = text.lower()
        for p in string.punctuation:
            text = text.replace(p, ' ')
        words = text.split()
        normalized = ' '.join(words)
        return f' {self.phrase} ' in f' {normalized} '


# Problem 3
class TitleTrigger(PhraseTrigger):
    def evaluate(self, story):
        return self.is_phrase_in(story.get_title())


# Problem 4
class DescriptionTrigger(PhraseTrigger):
    def evaluate(self, story):
        return self.is_phrase_in(story.get_description())


#======================
# TIME TRIGGERS
#======================

# Problem 5
class TimeTrigger(Trigger):
    def __init__(self, time_str):
        time_format = "%d %b %Y %H:%M:%S"
        est = pytz.timezone("EST")
        time = datetime.strptime(time_str, time_format)
        self.time = est.localize(time)


# Problem 6
class BeforeTrigger(TimeTrigger):
    def evaluate(self, story):
        story_time = story.get_pubdate()
        if story_time.tzinfo is None:
            story_time = pytz.timezone("EST").localize(story_time)
        return story_time < self.time


class AfterTrigger(TimeTrigger):
    def evaluate(self, story):
        story_time = story.get_pubdate()
        if story_time.tzinfo is None:
            story_time = pytz.timezone("EST").localize(story_time)
        return story_time > self.time


#======================
# COMPOSITE TRIGGERS
#======================

# Problem 7
class NotTrigger(Trigger):
    def __init__(self, trigger):
        self.trigger = trigger

    def evaluate(self, story):
        return not self.trigger.evaluate(story)


# Problem 8
class AndTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2

    def evaluate(self, story):
        return self.trigger1.evaluate(story) and self.trigger2.evaluate(story)


# Problem 9
class OrTrigger(Trigger):
    def __init__(self, trigger1, trigger2):
        self.trigger1 = trigger1
        self.trigger2 = trigger2

    def evaluate(self, story):
        return self.trigger1.evaluate(story) or self.trigger2.evaluate(story)


#======================
# FILTERING
#======================

# Problem 10
def filter_stories(stories, triggerlist):
    filtered = []
    for story in stories:
        for trigger in triggerlist:
            if trigger.evaluate(story):
                filtered.append(story)
                break
    return filtered


#======================
# USER-SPECIFIED TRIGGERS
#======================

# Problem 11
def read_trigger_config(filename):
    """
    filename: the name of a trigger configuration file
    Returns: a list of trigger objects specified by the trigger configuration file.
    """
    trigger_file = open(filename, 'r')
    lines = []
    for line in trigger_file:
        line = line.rstrip()
        if not (len(line) == 0 or line.startswith('//')):
            lines.append(line)

    trigger_map = {}
    triggers = []

    for line in lines:
        parts = line.split(',')

        if parts[0] == "ADD":
            for name in parts[1:]:
                triggers.append(trigger_map[name])
        else:
            name, trigger_type = parts[0], parts[1]
            if trigger_type == "TITLE":
                trigger_map[name] = TitleTrigger(parts[2])
            elif trigger_type == "DESCRIPTION":
                trigger_map[name] = DescriptionTrigger(parts[2])
            elif trigger_type == "AFTER":
                trigger_map[name] = AfterTrigger(parts[2])
            elif trigger_type == "BEFORE":
                trigger_map[name] = BeforeTrigger(parts[2])
            elif trigger_type == "NOT":
                trigger_map[name] = NotTrigger(trigger_map[parts[2]])
            elif trigger_type == "AND":
                trigger_map[name] = AndTrigger(trigger_map[parts[2]], trigger_map[parts[3]])
            elif trigger_type == "OR":
                trigger_map[name] = OrTrigger(trigger_map[parts[2]], trigger_map[parts[3]])

    return triggers


#======================
# MAIN THREAD
#======================

SLEEPTIME = 120  # seconds -- how often we poll

def main_thread(master):
    try:
        # Example hard-coded triggers
        t1 = TitleTrigger("election")
        t2 = DescriptionTrigger("Trump")
        t3 = DescriptionTrigger("Clinton")
        t4 = AndTrigger(t2, t3)
        triggerlist = [t1, t4]

        # Uncomment after Problem 11
        # triggerlist = read_trigger_config('triggers.txt')

        frame = Frame(master)
        frame.pack(side=BOTTOM)
        scrollbar = Scrollbar(master)
        scrollbar.pack(side=RIGHT, fill=Y)

        t = "Google & Yahoo Top News"
        title = StringVar()
        title.set(t)
        ttl = Label(master, textvariable=title, font=("Helvetica", 18))
        ttl.pack(side=TOP)
        cont = Text(master, font=("Helvetica", 14), yscrollcommand=scrollbar.set)
        cont.pack(side=BOTTOM)
        cont.tag_config("title", justify='center')
        button = Button(frame, text="Exit", command=root.destroy)
        button.pack(side=BOTTOM)
        guidShown = []

        def get_cont(newstory):
            if newstory.get_guid() not in guidShown:
                cont.insert(END, newstory.get_title() + "\n", "title")
                cont.insert(END, "\n---------------------------------------------------------------\n", "title")
                cont.insert(END, newstory.get_description())
                cont.insert(END, "\n*********************************************************************\n", "title")
                guidShown.append(newstory.get_guid())

        while True:
            print("Polling . . .", end=' ')
            stories = process("http://news.google.com/news?output=rss")
            stories.extend(process("http://news.yahoo.com/rss/topstories"))
            stories = filter_stories(stories, triggerlist)
            list(map(get_cont, stories))
            scrollbar.config(command=cont.yview)
            print("Sleeping...")
            time.sleep(SLEEPTIME)

    except Exception as e:
        print(e)


if __name__ == '__main__':
    root = Tk()
    root.title("RSS Feed Filter")
    t = threading.Thread(target=main_thread, args=(root,))
    t.start()
    root.mainloop()
