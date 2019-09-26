import unittest
import time


from extractor import clean, handleMarkup, extractHyperlink

# Currently q.task_done() in init.py is causing a non-consequential error while running test.py
# A better implementation of handing off the task could prevent this error.

class TestConsumer(unittest.TestCase):

    # Test the clean function from the extractor init.py
    def test_clean(self):
        print('\ntesting clean function \n')
        url = 'ttp://anat.co.za/'
        resultUrl = clean(url)
        self.assertEqual(resultUrl, 'http://www.anat.co.za/')

    # Test the markup handling function from the extractor init.py
    def test_handleMarkup(self):
        print('\ntesting markup handling function\n')
        finalUrl = 'http://www.anat.co.za/'
        # retrieve snippet of data
        resultSnippet = handleMarkup(finalUrl)

        self.assertEqual(resultSnippet[0:100], '<!DOCTYPE html>\n<html lang="en-US" class="html_stretched responsive av-preloader-disabled av-default')

    # Test the hyperlink extraction function from the extractor init.py
    def test_extractHyperlink(self):
        print('\ntesting the extract hyperlink function\n')
        with open("anat.co.za.html", encoding="utf-8") as f:
            data = f.read()
            print('data: ', data)
            time.sleep(1)
            resultLink = extractHyperlink(data)
            self.assertEqual(resultLink, 'https://www.youtube.com/channel/UCIMo2otmOvVuTzkXV9FHFTg')


if __name__ == "__main__":
    unittest.main()

    print("Everything passed")