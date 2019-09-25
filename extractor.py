from threading import Thread
import tkinter as tk
import tkinter.filedialog
import os
import logging
import traceback
from urllib.request import FancyURLopener
from unidecode import unidecode
from urllib.request import urlopen
from bs4 import BeautifulSoup
import unittest

try:
    import queue
except ImportError:
    import Queue as queue

q = queue.Queue()


# ----------- MyOpener header info & settings --------------- #

mz = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
apple = ' AppleWebKit/537.36 (KHTML, like Gecko) '
chrome = 'Chrome/66.0.3359.181 Safari/537.36'


class MyOpener(FancyURLopener): version = mz + apple + chrome


myopener = MyOpener()

# ---------- logging setttings  -------------- #

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )

# --------- Directory and Storage settings --------- #

outputName = 'URL-list-1'
storage = 'DB ' + outputName + ' STORAGE'
root = tk.Tk()
root.withdraw()
file_path = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
                                          filetypes=[("ALL Files", "*.*")])


hyperlinks = []

def producer():

        oEcount = 0
        with open(file_path, encoding='utf8', errors='surrogateescape') as input, open(storage + '.csv', 'w',
                                                                                   encoding='utf8') as output:
            non_blank = (line for line in input if line.strip())

            output.writelines(non_blank)

        with open(storage + '.csv', encoding='utf8') as f:
            for line in f:
                try:
                    line.encode('ascii', 'ignore').decode('ascii')

                    # ------------------Pre-emptively Cleaning URLs -------------------------#

                    url = line.replace(' ', '%20')
                    url = url.replace('\ufeff', '')
                    url = url.replace('\xa0hion\n', '')
                    url = url.replace('\udca0', '')
                    url = url.replace("'", "")
                    url = unidecode(url)

                    url = url.replace('"', '')
                    url = url.replace('http://', '')

                    url = url.replace('ttp://', '')
                    url = url.replace('ttps://', '')
                    url = url.replace('https://', '')
                    url = url.replace('www.','')
                    finalUrl = 'http://www.' + url
                    print('cleaned URL: ',finalUrl)

                    # ---------------- Get Markup from URL ----------------------- #
                    html = urlopen(finalUrl)
                    # ---------------- Add Markup to Queue ----------------------- #
                    q.put(html)
                    print('added markup to queue ')
                except OSError as oE:
                    print(oE)
                    oEcount = oEcount + 1
                    print(oEcount, ' OS error/s experienced so far')

                except Exception as e:
                    logging.error(traceback.format_exc())


def consumer():
    while True:
        try:
            html = q.get()
            soup = BeautifulSoup(html, 'lxml')

            all_links = soup.find_all("a")
            for link in all_links:
                print(link.get("href"))
                hyperlinks.append(link.get("href"))

            q.task_done()
            logging.debug(' \n line done:  ' + str(q.qsize()) + ' items in queue')
        except Exception as e:
            logging.error(traceback.format_exc())

for i in range(5):
    t = Thread(target=consumer)
    t.daemon = True
    t.start()

producer()

q.join()


print('Hyperlinks: ', hyperlinks)