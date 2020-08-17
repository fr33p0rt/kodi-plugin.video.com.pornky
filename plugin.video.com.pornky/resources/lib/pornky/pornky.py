# -*- coding: utf-8 -*-

# Author/Copyright: fr33p0rt
# License: GPLv3 https://www.gnu.org/copyleft/gpl.html

import requests
from bs4 import BeautifulSoup

class Pornky:
    URL = 'https://www.pornky.com/'
    URLCAT = '%s%s' % (URL, 'categories/')
    URLSEARCH = '%s%s' % (URL, 'search/?q=%s')
    cookies = None
    categories = []
    main_menu = []
    videos = []
    root_page = ''
    categories_page = ''

    def set_resolution(self, resolution_limit):
        pass

    def filter_category(self, categories, type):
        """
        Set category filter

        :param categories: list of categories (str)
        :type categories: str
        :param type: type of filter ('remove' 'only' 'ignore')
        :type type str
        """
        pass

    def get_cookies(self):
        """
        Initializes cookies
        """
        if not self.cookies:
            self.cookies = requests.head(self.URL, verify=False).cookies
        return self.cookies

    def get_root_page(self):
        """
        Returns root page
        """
        if not self.root_page:
            self.root_page = requests.get(self.URL, cookies=self.get_cookies(), verify=False).text
        return self.root_page

    def get_categories_page(self):
        """
        Returns page with categories
        """
        if not self.categories_page:
            self.categories_page = requests.get(self.URLCAT, cookies=self.get_cookies(), verify=False).text
        return self.categories_page

    def get_main_menu(self):
        """
        Returns main menu items from root page
        """
        if not self.main_menu:
            soup = BeautifulSoup(self.get_root_page(), 'html.parser')
            for i in soup.find('div', class_="main_menu").find_all('a'):
                if i.get('id')[0:4] == 'item' and i.get('id') != 'item1':
                    self.main_menu.append({'name': i.get('title'), 'url': i.get('href')})
        return self.main_menu

    def get_categories(self):
        """
        Returns categories items from categories page
        """
        if not self.categories:
            soup = BeautifulSoup(self.get_categories_page(), 'html.parser')
            for i in soup.find('div', class_='block_content').find_all('div', class_='item'):
                self.categories.append({'name': i.find('img').get('alt'),
                                        'url': i.find('a').get('href'),
                                        'thumb': i.find('img').get('src')+'|verifypeer=false'})
        return self.categories

    def get_video_links(self, url):
        """
        Returns video links from video page
        """
        soup = BeautifulSoup(self.get_page(url), 'html.parser')
        soup_links = soup.find(id="plinks")
        data_c_list = []
        for i in soup_links.find_all('div'):
            if i.get('data-c'):
                data_c_list.append(i.get('data-c').split(';'))

        default = '720p'

        video_links = []
        for data_c in data_c_list:

            res_suffix = '_' + data_c[1] if default != data_c[1] else ''
            url = 'http://s{}.fapmedia.com/cqlvid/{}/{}/{}000/{}/{}{}.mp4/{}{}.mp4'.format(
                data_c[7], data_c[5], data_c[6],
                str((int(data_c[4]) // 1000)), data_c[4],
                data_c[4], res_suffix, data_c[4], res_suffix)

            video_links.append((int(''.join(x for x in data_c[1] if x.isdigit())), url))

        return video_links

    def get_page(self, url):
        """
        Returns page
        """
        return requests.get(url, cookies=self.get_cookies(), verify=False).text

    def get_next_page(self, soup):
        """
        Returns link to next page from soup
        """
        page = soup.find('div', class_="pages")
        if not page:
            return None
        page = page.find('span')
        if not page:
            return None
        page = page.find_next_sibling()
        if page:
            return {'name': page.get('title'), 'url': page.get('href')}
        else:
            return None

    def get_video_categories(self, url):
        soup = BeautifulSoup(self.get_page(url), 'html.parser')
        categories = ''
        try:
            list_cat = []
            for i in soup.find('div', class_='videocats').find_all('a'):
                if i.string[0:3] == 'HD ':
                    list_cat.append(i.string[3:].replace(' Porno Videos', ''))
                else:
                    list_cat.append(i.string.replace(' Porno Videos', ''))
            categories = ', '.join(list_cat)
        except:
            pass
        return categories

    def get_videos(self, soup):
        """
        Returns all videos from soup tree
        """
        video_page_list = []
        for i in soup.find_all('div', class_="video"):
            name = i.find('h2').find('a').get('title')
            page = i.find('h2').find('a').get('href')
            thumb = i.find('img').get('src')
            #takes too long
            #categories = self.get_video_categories(page)
            duration = i.find('div', class_="duration").string
            video_page_list.append({'name': name, 'thumb': thumb, 'page': page, 'duration': duration, 'categories': 'Porn'})
        return video_page_list

    def get_videos_and_next_page(self, url):
        """
        Returns all videos and link to next page
        """
        soup = BeautifulSoup(self.get_page(url) if url[:4]=='http' else self.get_page(self.URL+url), 'html.parser')
        return (self.get_videos(soup), self.get_next_page(soup))
