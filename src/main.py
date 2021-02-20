import requests
from bs4 import BeautifulSoup
import subprocess
import youtube_dl
import os
import sys
from selenium import webdriver
import json

YOUTUBE_LINK = "https://www.youtube.com"

def find_values(id, json_file):
    results = []
    def _decode_dict(a_dict):
        try:
            results.append(a_dict[id])
        except KeyError:
            pass
        return a_dict
    json.load(json_file, object_hook=_decode_dict)  # Return value ignored.
    return bool(results)

def get_source_code_with_selenium(url):
    """
        Getting Source Code on Website with Selenium, because javascript
    """
    print("Channel url: " + url)
    driver = webdriver.Firefox()
    driver.get(url)
    button = driver.find_element_by_css_selector('.yt-uix-load-more')
    print(button)
    button.click();
    source_code = driver.page_source
    print("[+] Getting Source Code is Done, in Selenium")
    return source_code

def get_source_code(url):
    """ - Getting Source Code on Website
        http://stackoverflow.com/questions/17011357/what-is-the-difference-between-content-and-text#17011420
        r.text is the content of the response in unicode
        r.content is the content of the response in bytes.
    """
    print("Channel url: " + url)
    sourceCode = requests.get(url).content
    print("[+] Getting Source Code is Done")
    # print("sourceCode: ", sourceCode)
    sourceCode_str = sourceCode.decode('utf-8')
    strat_idx = sourceCode_str.index('{"responseContext"')
    end_idx = sourceCode_str.index(';</script><link rel="canonical')
    ext_str = sourceCode_str[strat_idx:end_idx]
    y = json.loads(ext_str)
    y_list = y['contents']['twoColumnBrowseResultsRenderer']['tabs']
    content_title_url_dic = {}
    for data in y_list:
        try:
            if data['tabRenderer']['title'] == '재생목록':
                for itemSectionRenderer in data['tabRenderer']['content']['sectionListRenderer']['contents']:
                    for item in itemSectionRenderer['itemSectionRenderer']['contents'][0]['shelfRenderer']['content']['horizontalListRenderer']['items']:
                        content_title_url_dic[item['gridPlaylistRenderer']['title']['runs'][0]['text']] = item['gridPlaylistRenderer']['title']['runs'][0]['navigationEndpoint']['commandMetadata']['webCommandMetadata']['url']

        except:
            pass
    return content_title_url_dic

def get_playlist_data(url):
    """ - Getting Data like Playlist Name and Link """
    sourceCode = requests.get(url).content
    sourceCode = sourceCode.decode('utf-8')
    print("url: ", url)
    strat_idx = sourceCode.index('{"responseContext"')
    # end_idx = sourceCode.index(';</script><link rel="canonical')
    ori_texts = sourceCode[strat_idx:]
    playlist = []
    while True:
        if ori_texts.find('playlistPanelVideoRenderer') == -1:
            break
        texts = ori_texts[ori_texts.index('playlistPanelVideoRenderer'):]
        texts.index('webPageType')
        texts = texts[texts.index('{"webCommandMetadata":{"url":"/watch'):]
        texts = texts[texts.index('/watch?'):texts.index('","webPageType')]
        playlist.append(texts)
        ori_texts = ori_texts[ori_texts.index('playlistPanelVideoRenderer')+10:]
    return playlist

def display_playlist(playlist):
    for name in playlist:
        print("Name : {} , Link :{} ".format(name, playlist[name]))

def create_directory_then_download(playlist, setuppath):
    """ First creating directory, then dowloading playlist each directory """
    for name in playlist:
        try:
            # Creating directory
            directory_path = "{0}".format(setuppath.replace('/', '_'))
            try:
                subprocess.check_call("mkdir -p " + directory_path, shell=True)
            except subprocess.CalledProcessError as e:
                print(e.output)
                continue
            # Downloading Playlist
            link = YOUTUBE_LINK + name
            options = {
                'outtmpl' : directory_path + '/%(title)s-%(id)s.%(ext)s'
            }
            if options['outtmpl'] in os.listdir(setuppath):
                continue
            with youtube_dl.YoutubeDL(options) as ydl:
                ydl.download([link])
        except Exception as e:
             with open(setuppath + name[-3:] + '.txt' , 'w') as f:    
                f.write(link + str(e))
                               
def main():
    # Downloading all playlists each directory from TheNewBoston channel
    url, option, setuppath = sys.argv[1:]
    
    if option == "selenium":
        sourceCode  = get_source_code_with_selenium(url)
    elif option == "request":
        sourceCode  = get_source_code(url)
    else:
        print("[-] Please entry option! ")
        print("$ python main.py url [selenium | request]")
        sys.exit(1)
    exist_list = os.listdir()

    for title, url in sourceCode.items():
        setuppath = title.replace(' ', '_')
        setuppath = setuppath.split('/')[0]
        setuppath = setuppath.replace('(', '_')
        setuppath = setuppath.replace(')', '_')

        if setuppath in exist_list:
            continue
        print("setuppath: ", setuppath)
        playlist = get_playlist_data('https://www.youtube.com' + url)
        try:
            create_directory_then_download(playlist, setuppath)
        except:
            with open(setuppath + '.txt' , 'w') as f:
                for i in playlist:
                    f.write(i)

if __name__ == "__main__":
    main()


