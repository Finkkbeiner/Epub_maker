#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
from ebooklib import epub
import regex as re
import shutil
import platform
import os


def test_internet_connection():
    timeout = 1
    try:
        requests.head("http://www.google.com/", timeout=timeout)
        log('The internet connection is active.\n')
    except requests.ConnectionError:
        log("The internet connection is down.\n")
        quit()          # Exits the programm


def log(txt):
    file = open("log_epubMaker.txt", 'a')
    file.write(txt)
    file.close()

def display_header():
    print("\n")
    print("\t\t   フィンクバイヌ")
    print("\t\t⎡⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎤")
    print("\t\t⎢    Epub Maker    ⎥")
    print("\t\t⎣__________________⎦")
    print("\n\tIt only works with lightnovelpub.com.\n")

def input_url0():
    url0 = input("Enter the book URL: ")
    return url0



def get_cover(soup0):
    s = soup0.find('div', class_='fixed-img')
    urls = re.findall(r'(https?://[^\s]+)', str(s))
    cover_url = urls[0][:-1]                            # There is a " at the end, who knows why

    res = requests.get(cover_url, headers={'User-Agent': 'Mozilla/5.0'}, stream = True)
    if res.status_code == 200:
        current_os = platform.system()
        match current_os:
            case 'Linux':
                with open('./cover.jpg', 'wb') as f:
                    shutil.copyfileobj(res.raw, f)
                log("You're on Linux.")
            case 'Windows':                             # idk if it works, I'm on linux
                with open(f'{os.getcwd()}\\cover.jpg', 'wb') as f:
                    shutil.copyfileobj(res.raw, f)
                log("You're on Windows. :/")
    else:
        log("The cover couldn't be downloaded.")


def get_chapter_content(url):
    r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    soup = BeautifulSoup(r.content, 'html.parser')
    s = soup.find('div', class_='titles')
    
    chap_title = str(s.find('span', class_='chapter-title').text)

    s2 = soup.find('div', id='chapter-container')

    chap_content_raw = s2.find_all('p')
    chap_content = ""

    for k in range(len(chap_content_raw)):      # watermarks remover
        reg_res = re.findall(r'<sub>', str(chap_content_raw[k]))
        if (len(reg_res) == 0):
            chap_content += str(chap_content_raw[k])
        else:
            continue
            #print('Watermark deleted.')

    return chap_title, chap_content


def get_soup0(url0):
    r = requests.get(url0, headers={'User-Agent': 'Mozilla/5.0'})
    return BeautifulSoup(r.content, 'html.parser')

def get_author(soup0):
    s = soup0.find('div', class_='author')
    author = str(s.find_all('span')[1].text)
    return author

def get_title(soup0):
    s = soup0.find('div', class_='main-head')
    title = str(s.find_all('h1')[0].text[1:-1])         # [1:-1] because there is a \n a the beginning and at the end it seems
    return title

def get_nbrChap(soup0):
    s = soup0.find('div', class_='header-stats')
    nbrChap = int(s.find_all('strong')[0].text)
    return nbrChap


def get_urlTemplates(soup0):
    s = soup0.find('nav', class_='links')
    urlTemplate = [];
    for link in s.find_all('a'):
        if link.has_attr('href'):
            urlTemplate.append(link.attrs['href'])
    
    fstChapter = 0  # default value
    urlTemplate = urlTemplate[0]
    try:
        i = urlTemplate.index('chapter-1')
        fstChapter = 1
    except:
        i = urlTemplate.index('chapter-0')     # Some books start at chapter 0!
        
    
    urlTemplateEnd = urlTemplate[i+9:]
    urlTemplate = 'https://www.lightnovelpub.com' + urlTemplate[:i+8]

    return fstChapter, urlTemplate, urlTemplateEnd



def init_book(title, author):
    book = epub.EpubBook()
    book.set_identifier('No ISBN')
    book.set_title(title)
    book.set_language('en')
    book.add_author(author)
    return book

def set_CSS_style():
    style = '''
        BODY {color: white;}
        nav[epub|type~='toc'] > ol > li > ol  {
            list-style-type:square;
        }
        nav[epub|type~='toc'] > ol > li > ol > li {
                margin-top: 0.3em;
        }
    '''
    return style

def create_chapter(chap_name, xhtml_file):
    return epub.EpubHtml(title=chap_name, file_name=xhtml_file, lang='en')

def add_chapter(book, chapter):
    book.add_item(chapter)

def add_cover(book, path):
    book.add_item(epub.EpubCover(path))

def remove_cover():
    os.remove("cover.jpg")

def remove_log_file():
    try:
        os.remove("log_epubMaker.txt")
    except FileNotFoundError:
        pass

def add_NCX_Nav(book):
    # Need to be added at the end, right before closing the ebook
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())


def delete_spaces(txt):         
    # Also prevents the issues with "/" when creating a file (not to make it a folder), also with "\""
    tmp = ""
    for k in range(len(txt)):
        if(txt[k] == ' '):
            tmp += '_'
        elif (txt[k] == '"'):
            tmp += '\''
        elif (txt[k] == "/"):
            tmp += ":"
        else:
            tmp += txt[k]
    return tmp

def import_chapter_to_book(book, nbrChap, fstChapter, urlTemplate, urlTemplateEnd):
    for k in range(fstChapter, nbrChap + 1):
        try:
            curr_url = urlTemplate + f'{k}' + urlTemplateEnd
            chap_title, chap_content = get_chapter_content(curr_url)
        except AttributeError:
            try:
                curr_url = urlTemplate + f'{k}'
                chap_title, chap_content = get_chapter_content(curr_url)
            except:
                print(f">- Chapter {k} failed -<")
                log(f">- Chapter {k} failed -<\n\tIt may not exist.\n")
                continue

        print(f"{chap_title}")
        chap = epub.EpubHtml(title=chap_title, file_name=(delete_spaces(chap_title) + '.xhtml'), lang='en')
        chap.set_content('<html><body><h1>' + chap_title + '</h1>' + chap_content + '</body></html>')
        add_chapter(book, chap)
        book.spine.append(chap)

        book.toc = book.toc + (chap,)
    


###################################################################################

def create_epub():
    remove_log_file()
    test_internet_connection()
    url0 = input_url0()
    soup0 = get_soup0(url0)
    get_cover(soup0)
    author = get_author(soup0)
    title = get_title(soup0)
    nbrChap = get_nbrChap(soup0)
    fstChapter, urlTemplate, urlTemplateEnd = get_urlTemplates(soup0)
    book = init_book(title + '.epub', author)
    book.spine = ['nav']
    book.toc = ()
    try:
        book.set_cover("cover.jpg", open('cover.jpg', 'rb').read())
    except FileNotFoundError:
        print("The cover file was not found.")
    import_chapter_to_book(book, nbrChap, fstChapter, urlTemplate, urlTemplateEnd)
    add_NCX_Nav(book)
    style = set_CSS_style()
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)
    book.add_item(nav_css)
    epub.write_epub(delete_spaces(str(title)) + '.epub', book, {})
    remove_cover()



if __name__ == "__main__":
    remove_log_file()
    test_internet_connection()

    display_header()
    url0 = input_url0()
    #url = 'https://www.lightnovelpub.com/novel/the-beginning-after-the-end-web-novel-09092253'
    #print(url)

    # Get important stuff from the first URL
    soup0 = get_soup0(url0)
    get_cover(soup0)
    author = get_author(soup0)
    title = get_title(soup0)
    nbrChap = get_nbrChap(soup0)
    fstChapter, urlTemplate, urlTemplateEnd = get_urlTemplates(soup0)


    book = init_book(title + '.epub', author)
    book.spine = ['nav']
    book.toc = ()   # Initializing the Table of Content


    # add cover image
    try:
        book.set_cover("cover.jpg", open('cover.jpg', 'rb').read())
    except FileNotFoundError:
        print("The cover file was not found.")
    
    
    #add all the chapters
    import_chapter_to_book(book, nbrChap, fstChapter, urlTemplate, urlTemplateEnd)
    
    add_NCX_Nav(book)

    # define CSS style
    style = set_CSS_style()
    nav_css = epub.EpubItem(uid="style_nav", file_name="style/nav.css", media_type="text/css", content=style)


    # add CSS file
    book.add_item(nav_css)

    epub.write_epub(delete_spaces(str(title)) + '.epub', book, {})

    remove_cover()