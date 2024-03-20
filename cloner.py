import requests
import shutil
import codecs
import os
import sys
import time
import platform

from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
def start():
    
    R = '\033[91m'
    Y = '\033[93m'
    G = '\033[92m'
    W = '\033[97m'
    print(R + """Enter Site Url Like example.ir""")
    DD = '\x1b[38;5;136m'
    print(DD+"""""")
    url = input("")
    url = "https://"+str(url)
    def check_url(url):
        try:
            response = requests.head(url)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    if check_url(url):
        print(Y +"""URL is valid""")
    else:
        print(Y +"""URL is not valid""")
        exit()


    if len(sys.argv) > 1: url = sys.argv[1]
    output_folder = urlparse(url).netloc

    session = requests.session()
    workspace = os.path.dirname(os.path.realpath(__file__))

    class Extractor:
        def __init__(self, url):
            self.url = url
            self.soup = BeautifulSoup(self.get_page_content(url), "html.parser")

            self.scraped_urls = self.scrap_all_urls()

        def run(self):
            self.save_files(self.scraped_urls)
            self.save_html()

        def get_page_content(self, url):
            try: 
                content = session.get(url)
                content.encoding = 'utf-8'
                return content.text
            except: return None
    
        def scrap_scripts(self):
            script_urls = []
            for script_tag in self.soup.find_all("script"):
                script_url = script_tag.attrs.get("src")
                if script_url:
                    if not script_url.startswith('http'): script_url = urljoin(self.url, script_url)
                    else: continue

                    new_url = self.url_to_local_path(script_url, keepQuery=True)

                    if new_url:
                        script_tag['src'] = new_url
                        script_urls.append(script_url.split('?')[0])

            return list(dict.fromkeys(script_urls))

        def scrap_form_attr(self):
            urls = []
            for form_tag in self.soup.find_all("form"):
                # if the tag has the attribute 'action'
                form_url = form_tag.attrs.get("action")
                if form_url:
                    if not form_url.startswith('http'): form_url = urljoin(self.url, form_tag.attrs.get("action"))

                    new_url = self.url_to_local_path(form_url, keepQuery=True)

                    if new_url:
                        form_tag['action'] = new_url

                        urls.append(form_url.split('?')[0])

            return list(dict.fromkeys(urls))

        def scrap_a_attr(self):
            urls = []
            for link_tag in self.soup.find_all('a'):
                link_url = link_tag.attrs.get('href')
                if link_url:
                    if not link_url.startswith('http'): link_url = urljoin(self.url, link_tag.attrs.get('href'))

                    new_url = self.url_to_local_path(link_url, keepQuery=True)
                    if new_url:
                        link_tag['href'] = new_url
                        urls.append(link_url.split('?')[0])

            return list(dict.fromkeys(urls))          


        def scrap_img_attr(self):
            urls = []
            for img_tag in self.soup.find_all('img'):
                img_url = img_tag.attrs.get('src')
                if img_url:
                    if not img_url.startswith('http'): img_url = urljoin(self.url, img_tag.attrs.get('src'))

                    new_url = self.url_to_local_path(img_url, keepQuery=True)
                    if new_url:
                        img_tag['src'] = new_url
                        urls.append(img_url.split('?')[0])

            return list(dict.fromkeys(urls))

        def scrap_link_attr(self):
            urls = []
            for link_tag in self.soup.find_all('link'):
                link_url = link_tag.attrs.get('href')
                if link_url:
                    if not link_url.startswith('http'): link_url = urljoin(self.url, link_tag.attrs.get('href'))

                    new_url = self.url_to_local_path(link_url, keepQuery=True)
                    if new_url:
                        link_tag['href'] = new_url
                        urls.append(link_url.split('?')[0])

            return list(dict.fromkeys(urls))

        def scrap_btn_attr(self):
            urls = []
            for buttons in self.soup.find_all('button'):
                button_url = buttons.attrs.get('onclick')
                if not button_url: return None

                button_url = button_url.replace(' ','')
                button_url = button_url[button_url.find('location.href='):].replace('location.href=','')
                button_url = button_url.replace('\'', '')
                button_url = button_url.replace('\"', '')
                button_url = button_url.replace('`', '')

                if button_url and button_url.startswith('/'):
                    if not button_url.startswith('http'): button_url = urljoin(self.url, buttons.get('onclick'))

                    new_url = self.url_to_local_path(button_url, keepQuery=True)
                    if new_url:
                        buttons['onclick'] = new_url
                        urls.append(button_url.split('?')[0])

            return list(dict.fromkeys(urls))


        def scrap_assets(self):
            assets_urls = []

            form_attr = self.scrap_form_attr()
            a_attr = self.scrap_a_attr()
            img_attr = self.scrap_img_attr()
            link_attr = self.scrap_link_attr()
            btn_attr = self.scrap_btn_attr()
                                                                                                                                                                                                                                                           # @slu000uls
            if form_attr: assets_urls = list(set(assets_urls + form_attr))
            if a_attr: assets_urls = list(set(assets_urls + a_attr))
            if img_attr: assets_urls = list(set(assets_urls + img_attr))
            if link_attr: assets_urls = list(set(assets_urls + link_attr))
            if btn_attr: assets_urls = list(set(assets_urls + btn_attr))

            return assets_urls

        def scrap_all_urls(self):
            urls = []
            urls.extend(self.scrap_scripts())
            urls.extend(self.scrap_assets())
            return list(dict.fromkeys(urls))

        def url_to_local_path(self, url, keepQuery=False):
            try:
                new_url = urlparse(url).path
                query = urlparse(url).query
                if keepQuery and query: new_url += '?' + urlparse(url).query
                if (new_url[0] == '/') or (new_url[0] == '\\'): new_url = new_url[1:]
            except:
                return None

            return new_url

        def download_file(self, url, output_path):

            url = url.split('?')[0]
            file_name = url.split('/')[-1]

            if len(file_name) == 0: return False
                                                                                                                                                                                                                                                                               # @slu000uls
            if not os.path.exists(os.path.dirname(output_path)):
                os.makedirs(os.path.dirname(output_path))

            response = session.get(url)
            with open(output_path, "wb") as file:
                file.write(response.content)
                GG = '\033[95m'
                print(GG+"""""")
                print(f"Downloaded {file_name} to {os.path.relpath(output_path)}")

            return True

        def save_files(self, urls):
            shutil.rmtree(os.path.join(workspace, output_folder), ignore_errors=True)
            for url in urls:
                output_path = self.url_to_local_path(url, keepQuery=False)
                output_path = os.path.join(workspace, output_folder, output_path)

                self.download_file(url, output_path)

            return True

        def save_html(self):
            output_path = os.path.join(workspace, output_folder,'index.html')
            prettyHTML = self.soup.prettify()
            with codecs.open(output_path, 'w', 'utf-8') as file:
                file.write(prettyHTML)
                file.close()
                print(f"Saved {os.path.relpath(output_path)}")

            return True

    extractor = Extractor(url)

    print(f"Downloading files{url}\n")
    extractor.run()
    SS = '\033[94m'
    AA = '\x1b[38;5;231m'
    print(SS+"""""")
    print(f"\nTotal Downloaded files: {len(extractor.scraped_urls)}\n@slu000uls")                                                                                                                                                                      # @slu000uls
    print(AA+"""""")


R = '\033[91m'
Y = '\033[93m'
G = '\033[92m'
W = '\033[97m'
path = os.path.isfile('/data/data/com.termux/files/usr/bin/bash')

if platform.system() == "Windows":
    os.system('cls')
else :
    os.system('clear')
print(G + """

       __      __     _       ___  _                      
       \ \    / /___ | |__   / __|| | ___  _ _   ___  _ _ 
        \ \/\/ // -_)| '_ \ | (__ | |/ _ \| ' \ / -_)| '_|
         \_/\_/ \___||_.__/  \___||_|\___/|_||_|\___||_|  
                                        
      Web Clonner
    
    """ + R + """>>""" + Y + """---""" + G + """ Author - slu000uls """ + Y + """---""" + R + """<<""")

try:
    print(R + """\n
#""" + Y + """ Select option""" + G + """ >>""" + Y + """

1)""" + G + """ Clone A Web Site """ + Y + """
2)""" + G + """ Exit""" + Y + """

""")
    ch = int(input(G + "Enter Your choice: " + W))
    if ch == 1:
        print(Y + "Loading ...." + W)
        time.sleep(1)
        if platform.system() == "Windows":
            os.system('cls')
        else :
            os.system('clear')
        start()
        

    elif ch == 2:
        print(Y + "Exit................" + W)
        sys.exit(0)

    else:
        print(R + "\nInvalid choice! Please try again")
except ValueError:
    print(R + "\nInvalid choice! Please try again")

    # @slu000uls