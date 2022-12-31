# epub_maker
*epub_maker* can help you create ebook from an internet source.\
You can **create new ebooks** or **update** them (created with this program though, it won't work with other ebooks).

#### Lightnovels
For now, only [LightNovelPub](https://www.lightnovelpub.com) is available.

#### Mangas
For now, only [IsekaiScan](https://isekaiscan.com) is available.\
But the creation isn't perfect, the images are still too small and not centered in height.


## Set-up
### Linux
You can run the bash script `set_up.sh` to install the different python libraries as well as python3. (You must run it as root if you don't have python)
(I'm not too sure about my bash skills, so it may not work properly)\
You can also install all the libraries by hand : `pip install requests beautifulsoup4 EbookLib regex pytest-shutil tqdm`.

### Windows
Visit [Python website](https://www.python.org/downloads/) and download python 3.10 or higher (libraries may not be compatible with higher versions)
Install it following the wizard steps.\
Then open a Terminal (⊞ Win + R), and enter the following command:\
`pip install requests beautifulsoup4 EbookLib regex pytest-shutil tqdm`\
And wait for installation to finish.

## Run the program
To run in on Windows, use: `C:\Users\*User*\AppData\Local\Programs\Python\Pyhton310\python.exe .\main.py` \
To run in on Linux, use: `python3 ./lightNovalPub_Classes.py`


Juste paste the URL of the book when asked and wait.

---

#### Note
You can only update ebook created by this program.\
You need **Python 3.10** (or higher, if libraries are compatibles) to run the program.
