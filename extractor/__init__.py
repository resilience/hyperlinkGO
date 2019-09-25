from threading import Thread
import tkinter as tk
import tkinter.filedialog
import os
import logging
import traceback
from unidecode import unidecode
from urllib.request import urlopen
from bs4 import BeautifulSoup


try:
    import queue
except ImportError:
    import Queue as queue

q = queue.Queue()
oEcount = 0


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


def clean(line):

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
        url = url.replace('www.', '')
        finalUrl = 'http://www.' + url
        print('cleaned URL: ', finalUrl)
        return finalUrl



def handleMarkup(finalUrl):


        # ---------------- Get Markup from URL ----------------------- #
        html = urlopen(finalUrl)
        # ---------------- Add Markup to Queue ----------------------- #
        q.put(html)
        print('added markup to queue ')



def extractHyperlink(html):
    soup = BeautifulSoup(html, 'lxml')

    all_links = soup.find_all("a")
    for link in all_links:
        print(link.get("href"))
        hyperlinks.append(link.get("href"))

    q.task_done()
    logging.debug(' \n line done:  ' + str(q.qsize()) + ' items in queue')


def producer():
    global oEcount
    try:
        with open(file_path, encoding='utf8', errors='surrogateescape') as input, open(storage + '.csv', 'w',
                                                                                   encoding='utf8') as output:
            non_blank = (line for line in input if line.strip())

            output.writelines(non_blank)

        with open(storage + '.csv', encoding='utf8') as f:
            for line in f:

                handleMarkup(clean(line))
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

            extractHyperlink(html)

        except Exception as e:
            logging.error(traceback.format_exc())


for i in range(5):

    t = Thread(target=consumer)
    t.daemon = True
    t.start()

producer()

q.join()


print('Hyperlinks: ', hyperlinks)


