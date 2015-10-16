from __future__ import division, unicode_literals

# import pdb

import json

from textblob import TextBlob
import re
import time
from datetime import datetime
import os, sys, codecs

from gutenberg.acquire import load_etext
from gutenberg.cleanup import strip_headers

import math

import progressbar

# Do not store words shorter than this
minWordLength = 4

idfForWords = {}

def tf(word, blob):
    return blob.words.count(word) / len(blob.words)

def n_containing(word, bloblist):
    return sum(1 for blob in bloblist if word in blob)

def idf(word, bloblist):
    global idfForWords
    if word in idfForWords:
        return idfForWords[word]
    num = n_containing(word, bloblist)
    lenBlob = len(bloblist)
    idf = math.log(lenBlob / (1 + num))
    idfForWords[word] = idf
    return idf

def tfidf(word, blob, bloblist):
    return tf(word, blob) * idf(word, bloblist)

def milliseconds():
    return int(round(time.time() * 1000))


# http://www.gutenberg.org/wiki/Gutenberg:Information_About_Robot_Access_to_our_Pages
#  This is an example of how to get files using wget:
#
#      wget -w 2 -m -H "http://www.gutenberg.org/robot/harvest?filetypes[]=html"
# 
# ...implies that Gutenberg would like a 2s pause between fetching books.

gutenbergWaitTimeMS = 2000
timeAtLastFetch = milliseconds() - gutenbergWaitTimeMS

# Remove any word that contains a unicode character
removeUnicodeWords = re.compile(r"\b\w*[^\x00-\x7F]\w*\b", re.UNICODE)

# Remove all unicode characters like random spaces, question marks
removeUnicodeCharacters = re.compile(r"[^\x00-\x7F]")

removePossessive = re.compile(r"'s\b")

removeWordsWithApostrophe = re.compile(r"\b\w+[']\w+")

removeHyphens = re.compile(r"-+")

removeEllipsis = re.compile(r"\.\.\.")

removeChapterHeaders = re.compile(r"^\s*chapter .*$", re.IGNORECASE)

removeRomanNumerals = re.compile(r"\b[LIVXCM]+\b")

removeQuotes = re.compile(r"\'")
hyphenateSpaces = re.compile(" ")

checkAlpha = re.compile(r"[A-Z]+")

def fileNameForBook(bookDetails):
    bookname = bookDetails['title']

    filename = removeQuotes.sub('', bookname)
    filename = hyphenateSpaces.sub("-", filename)
    return filename.lower()



def getBook(bookDetails):
    global timeAtLastFetch
    cachedFilename = "cache/" + fileNameForBook(bookDetails) + ".txt"
    if os.path.isfile(cachedFilename):
        with open(cachedFilename) as bookfile:
            text = bookfile.read()
            return TextBlob(text)

    nowMS = milliseconds()
    timeSinceLastFetch = nowMS - timeAtLastFetch
    if timeSinceLastFetch < gutenbergWaitTimeMS:
        waitTime = gutenbergWaitTimeMS - timeSinceLastFetch
        print "    waiting {}ms for Gutenberg...".format(waitTime)
        time.sleep(waitTime / 1000)

    bookId = bookDetails['id']
    print "Fetching from Gutenberg id {}".format(bookId)
    source = load_etext(bookId)
    print "    cleaning...."
    source = removeUnicodeWords.sub("", source)
    source = removeUnicodeCharacters.sub("", source)
    source = removePossessive.sub("", source)
    source = removeWordsWithApostrophe.sub("", source)
    source = removeHyphens.sub(" ", source)
    source = removeChapterHeaders.sub("", source)
    source = removeRomanNumerals.sub("", source)
    source = removeEllipsis.sub("", source)
    text = strip_headers(source).strip()
    timeAtLastFetch = milliseconds()
    if not os.path.isdir("cache"):
        os.mkdir("cache")
    bookfile = open(cachedFilename, 'w')
    bookfile.write(text)
    bookfile.close()
    print "    fetched and cached " + bookDetails['title']
    return TextBlob(text)


print "Loading stop words..."
stopWordsList = open("stopwords.txt")
allWords = stopWordsList.read()
stopWordsList.close()
stopWords = allWords.split()
stopWords = [word for word in stopWords if not word.startswith('#')]
stopWordsDict = set(stopWords)

print "Checking Gutenberg books..."

books = [
        { 'id': 996, 'title': 'Don Quixote', 'author': 'Miguel de Cervantes', 'translated': 'John Ormsby', 'published': '1605', 'url':'http://www.gutenberg.org/cache/epub/996/pg996.txt' },
        { 'id': 0, 'title': '1984', 'author': 'George Orwell', 'published': '1949', 'url': 'http://gutenberg.net.au/ebooks01/0100021.txt' },
        { 'id': 76, 'title': 'The Adventures of Huckleberry Finn', 'author': 'Mark Twain', 'published': '1884', 'url': 'http://www.gutenberg.org/cache/epub/76/pg76.txt' },
        { 'id': 1399, 'title': 'Anna Karenina', 'author': 'Leo Tolstoy', 'translated': 'Constance Garnett', 'published': '1877', 'url':'http://www.gutenberg.org/files/1399/1399-0.txt' },
        { 'id': 4300, 'title': 'Ulysses', 'author': 'James Joyce', 'published': '1922', 'url':'http://www.gutenberg.org/cache/epub/4300/pg4300.txt' },
        { 'id': 0, 'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'published': '1925', 'url': 'http://gutenberg.net.au/ebooks02/0200041h.html' },
        { 'id': 2600, 'title': 'War and Peace', 'author': 'Leo Tolstoy', 'published': '1869', 'url': 'http://www.gutenberg.org/cache/epub/2600/pg2600.txt' },
        { 'id': 28054, 'title': 'The Brothers Karamazov', 'author': 'Fyodor Dostoyevsky', 'published': '1880', 'url':'http://www.gutenberg.org/files/28054/28054-0.txt' },
        { 'id': 145, 'title': 'Middlemarch', 'author': 'George Eliot', 'published': '1874', 'url':'http://www.gutenberg.org/cache/epub/145/pg145.txt' },
        { 'id': 5200, 'title': 'The Metamorphosis', 'author': 'Franz Kafka', 'published': '1915', 'translated':'David Wyllie', 'url':'http://www.gutenberg.org/cache/epub/5200/pg5200.txt' },
        { 'id': 829, 'title': 'Gulliver\'s Travels', 'author': 'Jonathon Swift', 'published': '1726', 'url':'https://www.gutenberg.org/files/829/829-0.txt' },
        { 'id': 2833, 'title': 'The Portrait of a Lady', 'author': 'Henry James', 'published': '1881', 'url':'http://www.gutenberg.org/cache/epub/2833/pg2833.txt', 'published_as': 'The Portrait of a Lady Volume I'},
        { 'id': 6130, 'title': 'The Iliad', 'author': 'Homer', 'translated': 'Alexander Pope', 'published': '1720', 'url':'http://www.gutenberg.org/cache/epub/6130/pg6130.txt' },
        { 'id': 1727, 'title': 'The Odyssey', 'author': 'Homer', 'translated': 'Samuel Butler', 'published': '1829', 'url':'http://www.gutenberg.org/cache/epub/1727/pg1727.txt' },
        { 'id': 0, 'title': 'Mrs Dalloway', 'author': 'Virginia Woolf', 'published': '1925', 'url':'http://gutenberg.net.au/ebooks02/0200991h.html' },
        { 'id': 1342, 'title': 'Pride and Prejudice', 'author': 'Jane Austen', 'published': '1813', 'url':'http://www.gutenberg.org/cache/epub/1342/pg1342.txt' },
        { 'id': 1260, 'title': 'Jane Eyre', 'author': 'Charlotte Bronte', 'published': '1847', 'url':'http://www.gutenberg.org/cache/epub/1260/pg1260.txt' },
        { 'id': 8800, 'title': 'The Divine Comedy', 'author': 'Dante Alighieri', 'translated':'Rev. H. F. Cary', 'published': '1472', 'url':'http://www.gutenberg.org/cache/epub/8800/pg8800.txt' },
        { 'id': 768, 'title': 'Wuthering Heights', 'author': 'Emily Bronte', 'published': '1847', 'url':'http://www.gutenberg.org/cache/epub/768/pg768.txt' },
        { 'id': 215, 'title': 'The Call of the Wild', 'author': 'Jack London', 'published': '1903', 'url':'http://www.gutenberg.org/cache/epub/215/pg215.txt' },
        { 'id': 84, 'title': 'Frankenstein', 'author': 'Mary Shelley', 'published': '1818', 'url':'http://www.gutenberg.org/cache/epub/84/pg84.txt' },
        { 'id': 11, 'title': 'Alice in Wonderland', 'author': 'Lewis Carroll', 'published': '1865', 'url':'http://www.gutenberg.org/cache/epub/11/pg11.txt' },
        { 'id': 521, 'title': 'Robinson Crusoe', 'author': 'Daniel Defoe', 'published': '1719', 'url':'https://www.gutenberg.org/files/521/521-0.txt' },
        { 'id': 14591, 'title': 'Faust', 'author': 'Johann Wolfgang von Goethe', 'published': '1808', 'translated': 'Bayard Taylor', 'url':'http://www.gutenberg.org/cache/epub/14591/pg14591.txt' },
        { 'id': 1184, 'title': 'The Count of Monte Cristo', 'author': 'Alexandre Dumas', 'published': '1884', 'url':'http://www.gutenberg.org/cache/epub/1184/pg1184.txt' },
        { 'id': 1400, 'title': 'Great Expectations', 'author': 'Charles Dickens', 'published': '1861', 'url':'http://www.gutenberg.org/cache/epub/1400/pg1400.txt' },
        { 'id': 110, 'title': 'Tess of the D\'urbervilles', 'author': 'Thomas Hardy', 'published': '1891', 'url':'http://www.gutenberg.org/cache/epub/110/pg110.txt' },
        { 'id': 42, 'title': 'The Strange Case of Dr Jekyll and Mr Hyde', 'author': 'Robert Louis Stevenson', 'published': '1886', 'url':'http://www.gutenberg.org/cache/epub/42/pg42.txt' },
        { 'id': 1000, 'title': 'The Picture of Dorian Gray', 'author': 'Oscar Wilde', 'published': '1890', 'url':'http://www.gutenberg.org/cache/epub/174/pg174.txt' },
        { 'id': 2148, 'title': 'The Pit and the Pendulum and other Stories', 'author': 'Edgar Allan Poe', 'published': '1846', 'published_as': 'The Complete Works of Edgar Allan Poe: The Raven Edition, Vol 2' },
        { 'id': 345, 'title': 'Dracula', 'author': 'Bram Stoker', 'published': '1897', 'url':'http://www.gutenberg.org/cache/epub/345/pg345.txt' },
        { 'id': 2701, 'title': 'Moby Dick', 'author': 'Herman Melville', 'published': '1851', 'url':'http://www.gutenberg.org/cache/epub/2701/pg2701.txt' },
        { 'id': 35, 'title': 'The Time Machine', 'author': 'H. G. Wells', 'published': '1895', 'url':'http://www.gutenberg.org/cache/epub/35/pg35.txt' },
        { 'id': 164, 'title': 'Twenty-thousand Leagues Under the Sea', 'author': 'Jules Verne', 'published': '1869', 'url':'http://www.gutenberg.org/cache/epub/164/pg164.txt' },
        { 'id': 5230, 'title': 'The Invisible Man', 'author': 'H. G. Wells', 'published': '1897', 'url':'http://www.gutenberg.org/cache/epub/5230/pg5230.txt' },
        { 'id': 36, 'title': 'The War of the Worlds', 'author': 'H. G. Wells', 'published': '1898', 'url':'http://www.gutenberg.org/cache/epub/36/pg36.txt' },
        { 'id': 55, 'title': 'The Wonderful Wizard of Oz', 'author': 'L. Frank Baum', 'published': '1899', 'url':'http://www.gutenberg.org/cache/epub/55/pg55.txt' },
        { 'id': 236, 'title': 'The Jungle Book', 'author': 'Rudyard Kipling', 'published': '1894', 'url':'http://www.gutenberg.org/cache/epub/236/pg236.txt' },
        { 'id': 514, 'title': 'Little Women', 'author': 'Louisa May Alcott', 'published': '1880', 'url':'http://www.gutenberg.org/cache/epub/514/pg514.txt' },
        { 'id': 2500, 'title': 'Siddhartha', 'author': 'Hermann Hesse', 'published': '1922', 'url':'http://www.gutenberg.org/cache/epub/2500/pg2500.txt' },
        { 'id': 0, 'title': 'Gone With the Wind', 'author': 'Margaret Mitchell', 'published': '1936', 'url':'http://gutenberg.net.au/ebooks02/0200161.txt' },
        { 'id': 203, 'title': 'Uncle Tom\'s Cabin', 'author': 'Harriet Beecher Stowe', 'published': '1852', 'url':'http://www.gutenberg.org/cache/epub/203/pg203.txt' },
        { 'id': 1257, 'title': 'The Three Musketeers', 'author': 'Alexandre Dumas', 'published': '1844', 'url':'https://www.gutenberg.org/files/1257/1257-0.txt' },
        { 'id': 2852, 'title': 'The Hound of the Baskervilles', 'author': 'Arthur Conan Doyle', 'published': '1902', 'url':'http://www.gutenberg.org/cache/epub/2852/pg2852.txt' },
        { 'id': 244, 'title': 'A Study in Scarlet', 'author': 'Arthur Conan Doyle', 'published': '1887', 'url':'http://www.gutenberg.org/cache/epub/244/pg244.txt' },
        { 'id': 0, 'title': 'At the Mountains of Madness', 'author': 'H. P. Lovecraft', 'published': '1936', 'url':'http://gutenberg.net.au/ebooks06/0600031h.html' },
        { 'id': 50133, 'title': 'The Dunwich Horror', 'author': 'H. P. Lovecraft', 'published': '1929', 'url':'http://www.gutenberg.org/cache/epub/50133/pg50133.txt' }
]

bloblist = []

if os.path.isfile("cache/tfidf.json"):
    with open("cache/tfidf.json") as tfidfCached:
        idfForWords = json.load(tfidfCached)
        print "Loaded {0} cached IDF entries".format(len(idfForWords))

if not os.path.isdir("json"):
    os.mkdir("json")

for book in books:
    if book['id'] == 0:
        continue
    print "Loading: " + book['title']
    bookBlob = getBook(book)
    bloblist.append(( bookBlob, book ))

# pdb.set_trace()

for i, blobrec in enumerate(bloblist):
    blob = blobrec[0]
    bookdata = blobrec[1]
    processedWords = set()
    processedBook = { 'bookInfo': bookdata }
    tagCount = 0
    totalTags = len(blob.tags)

    print "\n Processing {0} tags from: {1}".format(totalTags, bookdata['title'])

    bar = progressbar.ProgressBar(maxval=totalTags, widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()

    for tag in blob.tags:
        tagCount += 1
        word = tag[0].upper()
        if len(word) < minWordLength:
            continue
        if word in processedWords:
            continue
        if not checkAlpha.match(word):
            # print "Rejecting non-alpha word: \"{}\"".format(word)
            continue
        processedWords.add(word)
        pos = tag[1]
        # Use nouns & adjectives only
        # http://cs.nyu.edu/grishman/jet/guide/PennPOS.html
        if not pos.startswith("NN") and not pos.startswith("JJ"):
            #print "    " + word + " - pos " + pos + " ignored"
            continue
        if word.lower() in stopWordsDict:
            # print "    " + word + " - stop word ignored"
            continue
        score = int(1000000.0 * tfidf(word, blob, bloblist))
        lenTag = "{}".format(len(word))
        if not lenTag in processedBook:
            processedBook[lenTag] = []

        scoreRecord = {'score':score, 'word':word}
        wordsForLength = processedBook[lenTag]
        processedBook[lenTag].append(scoreRecord)
        bar.update(tagCount)
        # print "{0}/{1} - {2} - {3}".format(tagCount,totalTags, score, word)

    bar.finish()
    for key, bookDataEntry in processedBook.iteritems():
        if key == 'bookInfo':
            continue
        bookDataEntry.sort(reverse=True, key=lambda x: x['score'])

    jsonFileName = "json/" + fileNameForBook(bookdata) + ".json"
    with open(jsonFileName, 'w') as bookFile:
        json.dump(processedBook, bookFile)

    print "Wrote: {0}".format(jsonFileName)

    with open("cache/tfidf.json", 'w') as idfCached:
        json.dump(idfForWords, idfCached)
        print "    ...cached {0} IDF entries".format(len(idfForWords))

print "Done processing {} books".format(len(books))
