# coub_bookmarks_likes_downloader

This is a simple script that allows you to download your favorite coubs from the <https://coub.com/bookmarks> and <https://coub.com/likes> tabs, where log in is necessery.

## How to use

### Install necessary libraries

    pip install -r requirements.txt

### Run script

    usage: python coub.py [-h] [-p PASSWORD] [-e EMAIL] [-t TYPE]

    mandatory arguments:
        -p PASSWORD, --password PASSWORD
        -e EMAIL, --email EMAIL
        -t TYPE, --type TYPE  Type [likes] to download coubs form My likes page and [bookmarks] for Bookmarks.
    
    optional arguments:
        -h, --help            show this help message and exit
    
    example: python coub.py -p mypassword -e myemail@gmail.com -t likes
