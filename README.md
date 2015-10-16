## GutenWords

### Get Interesting Words From Gutenberg Books

For my game "Word Monsters!" which features monsters attacking your city, that you defend by typing words, I need a list of words from classic books.  I get the books from project Gutenberg, so that part is not too hard.

But I want the words to capture the flavor of the books: subjectively the "important" words from the book.  Turns out that TF-IDF is not too bad at this.  :-)

I also need the words organized by length, and some meta data about the book.  Python modules to the rescue!

Here's the-dunwich-horror.json and some length 10 words:

    "10": [
        {
            "score": 795,
            "word": "MISKATONIC"
        },
        {
            "score": 715,
            "word": "MANUSCRIPT"
        },
        {
            "score": 477,
            "word": "UNIVERSITY"
        },
        {
            "score": 477,
            "word": "STICKINESS"
        },
        {
            "score": 397,
            "word": "UNDERBRUSH"
        },
        {
            "score": 318,
            "word": "RHYTHMICAL"
        },
        {
            "score": 238,
            "word": "TREMENDOUS"
        },
        {
            "score": 238,
            "word": "SUFFICIENT"
        },
        {
            "score": 238,
            "word": "REMARKABLE"
        },

Some length 12 words:

    "12": [
        {
            "score": 477,
            "word": "NECRONOMICON"
        },
        {
            "score": 238,
            "word": "CONSIDERABLE"
        },
        {
            "score": 159,
            "word": "INTELLIGENCE"
        },
        {
            "score": 159,
            "word": "CIRCUMSTANCE"
        },
        {
            "score": 159,
            "word": "SIGNIFICANCE"
        },
        {
            "score": 159,
            "word": "UNMISTAKABLE"
        },
        {
            "score": 79,
            "word": "SUPERSTITION"
        },


Surprisingly in the length 7 words that which we should not name starting with "C" and ending in "u" doesn't come in the top 20 by IDF at all.  Here's the front-runners:

    "7": [
        {
            "score": 3022,
            "word": "DUNWICH"
        },
        {
            "score": 1431,
            "word": "STRANGE"
        },
        {
            "score": 1352,
            "word": "CERTAIN"
        },
        {
            "score": 1033,
            "word": "VILLAGE"
        },
        {
            "score": 1033,
            "word": "SOTHOTH"
        },
        {
            "score": 954,
            "word": "ANCIENT"
        },
        {
            "score": 795,
            "word": "NOTHING"
        },
        {
            "score": 715,
            "word": "NATIVES"
        },
        {
            "score": 715,
            "word": "LAVINIA"
        },
        {
            "score": 715,
            "word": "GOATISH"
        },

`getbooks.py` is the script that does the fetching from Gutenberg and all the scoring stuff.  If you go completely mad and want to run it on Mac its just a case of installing the required packages via pip.  If you don't have stuff set up for Python its something like:

    # save the attached files into some folder - stopwords.txt has to be in the same directory as the script.
    mkdir getbooks && cd getbooks

    # install PIP if you don't have it
    curl https://bootstrap.pypa.io/get-pip.py > get-pip.py
    sudo get-pip.py

    # use a virtualenv for packages
    virtualenv venv
    source venv/bin/activate

    # install needed stuff
    pip install gutenberg
    pip install text blob
    pip install progressbar

    # run script
    python getbooks.py


