import abc
import ebooklib
import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import regex as re


def log(txt):
    file = open("log_epubMaker.txt", 'a')
    file.write(txt)
    file.close()


def delete_spaces(txt):
    # Also prevents the issues with "/" when creating a file (not to make it a folder), also with "\""
    tmp = ""
    for k in range(len(txt)):
        if txt[k] == ' ':
            tmp += '_'
        elif txt[k] == '"':
            tmp += '\''
        elif txt[k] == "/":
            tmp += ":"
        else:
            tmp += txt[k]
    return tmp


class AbstractBook(metaclass=abc.ABCMeta):

    def __init__(self, url0, path):
        self.title = None
        self.author = None
        self.url0 = url0
        self.url_list = []
        if path == "":
            self.book = epub.EpubBook()
            self.book.toc = list(self.book.toc)  # Test
        else:
            self.book = epub.read_epub(path)
        self.style = ""
        self.soup0 = BeautifulSoup(requests.get(url0, headers={'User-Agent': 'Mozilla/5.0'}).content, 'html.parser')
        self.get_author()
        self.get_title()

    #
    # ######################################## Methods that  need overloading ######################################## #

    @abc.abstractmethod
    def get_author(self):
        pass

    @abc.abstractmethod
    def get_title(self):
        pass

    @abc.abstractmethod
    def get_cover(self):
        pass

    @abc.abstractmethod
    def import_chapter_to_book_with_url(self, _uid="0"):
        pass

    @abc.abstractmethod
    def get_chapter_link(self):
        pass

    # ################################################################################################################ #
    #

    #
    # #################################### Methods that does not need overloading #################################### #

    def set_title_author(self):
        self.book.set_title(self.title)
        self.book.add_author(self.author)

    def set_lang_isbn(self, lang="en", isbn="No ISBN"):
        self.book.set_language(lang)
        self.book.set_identifier(isbn)

    def set_cover(self, path="cover.jpg"):
        try:
            self.book.set_cover("cover.jpg", open('cover.jpg', 'rb').read())
        except FileNotFoundError:
            try:
                self.book.set_cover("cover.png", open('cover.png', 'rb').read())
            except FileNotFoundError:
                log("The cover file was not found.")
                print("The cover file was not found.")

    def get_css_style(self):
        # @TODO Try to find a way to add a path as a parameter, if none entered, use the basic value
        self.style = '''
            BODY {color: white;}
            nav[epub|type~='toc'] > ol > li > ol  {
                list-style-type:square;
            }
            nav[epub|type~='toc'] > ol > li > ol > li {
                    margin-top: 0.3em;
            }
        '''

    def set_css_style(self):
        self.book.add_item(
            epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=self.style))

    def add_chapter(self, chapter):
        self.book.add_item(chapter)

    def add_ncx_nav(self):
        # Need to be added at the end, right before closing the ebook
        self.book.toc = tuple(self.book.toc)
        self.book.add_item(epub.EpubNav())
        self.book.add_item(epub.EpubNcx())


    def write(self):
        epub.write_epub(delete_spaces(str(self.title)) + '.epub', self.book, {})


    # ############### Methods for updating books ############### #

    def get_last_chapter(self):
        lst = []
        for item in self.book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
            lst.append(item)
        last = str(lst[-2])
        nbr = []
        for item in map(int, re.findall(r'\d+', last)):
            nbr.append(int(item))
        return max(nbr)  # Not sure that it will work in all cases
        # (for example if there is a high number in the name of the last chapter)

    def select_needed_chapters(self, last_chapter):
        self.get_chapter_link()
        self.url_list = self.url_list[last_chapter:]

    # ########################################################## #


    # ################################################################################################################ #
    #
