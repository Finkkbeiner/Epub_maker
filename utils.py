import os
import shutil
import platform
import requests

ERROR = -1
CREATE = 1
UPDATE = 2

LIGHTNOVELPUB = 1
ISEKAISCAN = 2


def choose_create_update():
	print("You want to:")
	print('\t[1] Create an ebook')
	print('\t[2] Update an ebook')
	print('\t[_] Quit')
	choice = input("Your choice: ")
	try:
		if int(choice) == 1:
			return CREATE
		elif int(choice) == 2:
			return UPDATE
		else:
			return ERROR
	except ValueError:
		return ERROR


def choose_source():
	book_types = ["Light Novel", "Manga", "Manhua", "Manhwa"]
	print("Sources:")
	print("\t[1] {} ({})".format("LightNovelPub", book_types[0]))
	#print("\t[2] {} ({})".format("IsekaiScan", book_types[1]))
	#
	source = input("Your choice: ")
	try:
		if int(source) == 1:
			return LIGHTNOVELPUB
		#elif int(source) == 2:
		#	return ISEKAISCAN
		else:
			return ERROR
	except ValueError:
		return ERROR


# Basic CSS style
STYLE = '''
BODY {color: white;}

nav[epub|type~='toc'] > ol > li > ol  {
	list-style-type:square;
}

nav[epub|type~='toc'] > ol > li > ol > li {
	margin-top: 0.3em;
}

.container {
	display: flex;
	align-items: center;
	height: 100%;
}

img	{
	width: 100%;
	object-fit: contain;
}
'''


def log(txt):
	file = open("log_epubMaker.txt", 'a')
	file.write(txt + '\n')
	file.close()


def remove_log_file():
	try:
		os.remove("log_epubMaker.txt")
	except FileNotFoundError:
		pass


def remove_cover():
	try:
		os.remove("cover.jpg")
	except FileNotFoundError:
		try:
			os.remove("cover.png")
		except FileNotFoundError:
			log("No cover to remove.")


def input_url0():
	return input("Enter the book URL: ")


def get_path_of_existing_book():
	is_file = False
	while not is_file:
		path = input("Enter existing book path: ")
		if os.path.isfile(path) and os.path.splitext(path)[1] == '.epub':
			break
		print("Please enter a valid path.")
	return path


def display_header():
	print("\n")
	print("\t\t   フィンクバイナ")
	print("\t\t⎡⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎴⎤")
	print("\t\t⎢    Epub Maker    ⎥")
	print("\t\t⎣__________________⎦")
	print("\n\tIt only works with lightnovelpub.com.\n")


def download_image(image_url, filename):
	res = requests.get(image_url, headers={'User-Agent': 'Mozilla/5.0'}, stream=True)
	if res.status_code == 200:
		current_os = platform.system()
		match current_os:
			case 'Linux':
				with open(filename, 'wb') as f:
					shutil.copyfileobj(res.raw, f)
				log("You're on Linux.")
			case 'Windows':  # IDK if it works, I'm on linux
				with open(f'{os.getcwd()}\\' + filename, 'wb') as f:
					shutil.copyfileobj(res.raw, f)
				log("You're on Windows. :/")
	else:
		log(f"The cover couldn't be downloaded (error: {res.status_code}).")


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
