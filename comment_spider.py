# -*- coding:utf-8 -*-

import time
import threading
import matplotlib.pyplot as plt
from selenium import webdriver
import matplotlib.animation as animation

period = 1
bufs = []
urls = open("urls.txt", "r").readlines()
threads = []
axes = []
lines = []
anis = []


class MyThread(threading.Thread):
    def __init__(self, url, num):
        threading.Thread.__init__(self)
        self.url = url
        self.num = num

    def run(self):
        print "openning:" + self.url
        chrome = webdriver.Chrome()
        chrome.get(self.url)
        comments = get_comments(chrome)
        start = time.time()
        while True:
            time.sleep(period * 0.8)
            new_comments = get_comments(chrome)
            result = new_comments[len(comments):]
            comments = new_comments
            number = len(result)
            print self.url.split("/")[-1] + ":" + str(number / float(period))
            + u"comments per second"
            bufs[self.num].append(number)
            if time.time() - start >= 60:
                try:
                    hostname = get_hostname(chrome)
                    hostname = hostname + " " * (15 - len(hostname))
                    livecount = get_livecount(chrome).encode("utf-8")
                    activitycount = get_activitycount(chrome).encode("utf-8")
                    goldnum = get_goldnum(chrome).encode("utf-8")
                    chatnum = get_chatnum(chrome).encode("utf-8")
                    comments_num = len(get_comments(chrome))
                except Exception:
                    print self.url[:-1] + u" 发生错误已关闭\n"
                    chrome.close()
                    return
                f.write("%s\t%s\t%s\t%s\t%s\t%d\n" % (hostname.encode("utf-8"), livecount,
                                                      activitycount, goldnum, chatnum, comments_num))
                f.flush()
                print self.url[:-1] + u" 爬取完成\n"
                chrome.close()
                return


def get_hostname(chrome):
    hostname = chrome.find_element_by_class_name("host-name")
    return hostname.text


def get_livecount(chrome):
    livecount = chrome.find_element_by_id(
        "live-count").text.replace(",", "")
    return livecount


def get_activitycount(chrome):
    activityCount = chrome.find_element_by_id("activityCount").text
    return activityCount


def get_goldnum(chrome):
    chrome.execute_script("$('ul').mouseover()")
    week_rank_list = chrome.find_element_by_id("week-rank-list").text
    goldnum = sum([int(i.replace(",", ""))
                   for i in week_rank_list.encode("utf-8").split("\n")[2::3]])
    return unicode(goldnum)


def get_chatnum(chrome):
    chatnum = chrome.find_element_by_xpath(
        "//*[@id='chatRoom']/div[1]/span[2]").text[5:-1]
    return chatnum


def get_comments(chrome):
    comments = chrome.find_element_by_class_name("chat-room__list")
    comments = comments.text.split("\n")
    comments = [comments[i] + comments[i + 1]
                for i in range(1, len(comments) / 2)[::2]]
    return comments


def update(data, num):
    length = len(bufs[num])
    if length >= 10:
        axes[num].set_xlim(length - 10, length)
        axes[num].set_xticks(range(length - 10, length))
        axes[num].bar(range(length - 10, length), bufs[num]
                      [length - 10:length], 0.5, color='m')
    else:
        axes[num].bar(range(length), bufs[num][:length], 0.5, color='m')


fig = plt.figure(figsize=(20, 10))
plt.grid()
f = open("data.txt", "a")
for i in range(len(urls)):
    axes.append(fig.add_subplot(101 + len(urls) * 10 + i))
    bufs.append([])
    threads.append(MyThread(urls[i], i))
    threads[i].start()
    time.sleep(20)

pause = raw_input(u"输入enter键继续")

for i in range(len(urls)):
    line = axes[i].bar([], [], 1, color="b")
    lines.append(line)
    print line
    axes[i].set_title(urls[i])
    axes[i].set_xlabel("Time/s")
    axes[i].set_ylabel("comments")
    axes[i].set_xticks(range(11))
    axes[i].set_yticks([item * 5 for item in range(11)])
    axes[i].set_xlim(0, 10)
    axes[i].set_ylim(0, 50)
    anis.append(animation.FuncAnimation(
        fig, update, fargs=[i], interval=1, repeat=True))

plt.show()
