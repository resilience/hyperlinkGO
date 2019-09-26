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


# ------------------- To do:
#                         Upload URL's to a separate queue
#                         Build more comprehensive tests for internet connection, http responses, badly encoded data etc
#                         Build an overflow buffer to prevent queue ballooning and stale data representation


#                   This program parses a list of user defined URL's in .csv format
#                   Then extracts hyperlinks from their html blobs returned by the URL's parsed.
#                   The hyperlink output is in the form of a []

q = queue.Queue()
oEcount = 0

# ---------- logging setttings  -------------- #

logging.basicConfig(level=logging.DEBUG, format='(%(threadName)-9s) %(message)s', )

# --------- Directory and Storage settings --------- #

outputName = 'URL-list-1'
storage = 'DB ' + outputName + ' STORAGE'
root = tk.Tk()
root.withdraw()

hyperlinks = []

# The application runs 2 main functions called producer and consumer, each


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
    print('accessing page....')
    # ---------------- Get Markup from URL ----------------------- #
    html = urlopen(finalUrl)
    # ---------------- Add Markup to Queue ----------------------- #
    q.put(html)
    print('markup added to queue \n  ' + str(q.qsize()) + ' items in queue')

    # ---------------- Allow data to be retrieved for Unit Test ----------------------- #
    html = urlopen(finalUrl)
    data = html.read()

    data = data.decode('utf-8')

    return data


def extractHyperlink(html):

    # ---------------- retrieves all hyperlinks from html blob by extracting for all a tags and href tags. ---- #
    soup = BeautifulSoup(html, 'lxml')

    all_links = soup.find_all("a")

    for link in all_links:
        hyperlinks.append(link.get("href"))


    logging.debug(' \n hyperlinks extracted  \n' + str(q.qsize()) + ' items in queue')
    try:
        print(hyperlinks[0])
    except IndexError as iE:
        print('Index Error, list likely empty')
        print('List: ', hyperlinks)

    q.task_done()
    return hyperlinks[0]


# Defines the producer
def producer():
    global oEcount
    try:
        # currently received a temporary RuntimeError, because it's trying to open a filedialog for each producer thread
        # Next Step : Separate file path code from producer thread

        # ---------- File path code ---------------------------------------- #
        # --------- opens file path of URL's to be processed --------------- #

        file_path = tk.filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file", filetypes=[("ALL Files", "*.*")])

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

# Defines the consumer
def consumer():

    while True:
        try:
            # ---------- Retrieves markup from queue ------------------------------------------- #
            html = q.get()

            # ---------- Runs hyperlink extraction code ---------------------------------------- #
            extractHyperlink(html)

        except Exception as e:
            logging.error(traceback.format_exc())

# ---------- Set number of consumers -------------- #
for i in range(2):
    t = Thread(target=consumer)
    t.daemon = True
    t.start()

# ---------- Set number of producers --------------- #
for i in range(5):
    t = Thread(target=producer)
    t.daemon = True
    t.start()

producer()

q.join()

print('Hyperlinks: ', hyperlinks)


