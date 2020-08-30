# -*- coding: utf-8 -*-

# Author/Copyright: fr33p0rt (based on code by Roman V. M.)
# License: GPLv3 https://www.gnu.org/copyleft/gpl.html

import os
import sys
import re
import urllib
import requests

from urllib import urlencode
from urlparse import parse_qsl
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from resources.lib.pornky.pornky import Pornky

from resources.lib.cfg.filter import Filter
from resources.lib.cfg.res import Res
from resources.lib.cfg.cfg import Cfg

from contextlib import contextmanager


@contextmanager
def busy_dialog():
    # Get Kodi version
    kodi_version = re.findall(r'[0-9.]+|$', xbmc.getInfoLabel('System.BuildVersion'))[0]

    xbmc.log('Kodi version: %s' % kodi_version, xbmc.LOGERROR)

    if int(kodi_version.split('.')[0]) >= 18:
        dialog = 'busydialognocancel'
    else:
        dialog = 'busydialog'

    xbmc.executebuiltin('ActivateWindow({})'.format(dialog))
    try:
        yield
    finally:
        xbmc.executebuiltin('Dialog.Close({})'.format(dialog))


def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :type kwargs: dict
    :return: plugin call URL
    :rtype: str
    """
    return '{0}?{1}'.format(_url, urlencode(kwargs))


def get_categories():
    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or server.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: types.GeneratorType
    """
    return pornky.get_categories()


def get_videos(url):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given url from some site or server.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param url: url
    :type url: str
    :return: the list of videos in the url (and next page if exists)
    :rtype: list
    """
    return pornky.get_videos_and_next_page(url)


def list_end():
    # Add a sort method for the virtual folder items
    xbmcplugin.addSortMethod(_handle, xbmcplugin.SORT_METHOD_NONE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(_handle)


def donate_menu():
    xbmcplugin.setPluginCategory(_handle, 'Donate')
    xbmcplugin.setContent(_handle, 'videos')

    for i in [('Bitcoin (BTC)', 'Bitcoin_QR.png'),
              ('Ethereum (ETH)', 'Ethereum_QR.png'),
              ('Ripple (XRP)', 'XRP_QR.png')]:
        picture_path = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'donate', i[1])
        list_item = xbmcgui.ListItem('Donate %s' % i[0])
        list_item.setInfo('video', {'title': 'Donate %s' % i[0],
                                    'genre': 'Donate %s' % i[0],
                                    'mediatype': 'video'})
        list_item.setArt({'icon': picture_path,
                          'thumb': picture_path})

        url = get_url(action='show', category=picture_path)

        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_end()


def list_root():
    xbmcplugin.setPluginCategory(_handle, 'pornky.com')
    xbmcplugin.setContent(_handle, 'videos')
    main_menu = pornky.get_main_menu()
    log_menu = pornky.get_log_menu()
    list_item = xbmcgui.ListItem('Donate ...')
    list_item.setInfo('video', {'title': 'Donate ...',
                                'genre': 'Donate ...',
                                'mediatype': 'video'})
    url = get_url(action='donatemenu', category='')
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    for menu_item in log_menu:
        list_item = xbmcgui.ListItem(label=menu_item['name'])
        list_item.setInfo('video', {'title': menu_item['name'],
                                    'genre': menu_item['name'],
                                    'mediatype': 'video'})

        url = get_url(action='listing', category=menu_item['url'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)

    list_item = xbmcgui.ListItem('Search menu ...')
    list_item.setInfo('video', {'title': 'Search menu ...',
                                'genre': 'Search menu ...',
                                'mediatype': 'video'})
    url = get_url(action='searchmenu', category='')
    xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    for menu_item in main_menu:
        list_item = xbmcgui.ListItem(label=menu_item['name'])
        list_item.setInfo('video', {'title': menu_item['name'],
                                    'genre': menu_item['name'],
                                    'mediatype': 'video'})

        if menu_item['name'][0:7] == 'Categor':
            url = get_url(action='categories', category='')
        else:
            url = get_url(action='listing', category=menu_item['url'])
        xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_videos('')


def list_categories():
    """
    Create the list of video categories in the Kodi interface.
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, 'Categories')
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get video categories
    categories = get_categories()
    # Iterate through categories
    for category in categories:
        if (cfg.filter == Filter.SUPPRESS and category['name'] not in cfg.filter_items) or\
                (cfg.filter == Filter.ONLY and category['name'] in cfg.filter_items) or\
                 cfg.filter == Filter.OFF:
            # Create a list item with a text label and a thumbnail image.
            list_item = xbmcgui.ListItem(label=category['name'])
            # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
            # Here we use the same image for all items for simplicity's sake.
            # In a real-life plugin you need to set each image accordingly.
            list_item.setArt({'thumb': category['thumb'],
                              'icon': category['thumb']})
            # Set additional info for the list item.
            # Here we use a category name for both properties for for simplicity's sake.
            # setInfo allows to set various information for an item.
            # For available properties see the following link:
            # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
            # 'mediatype' is needed for a skin to display info for this ListItem correctly.
            list_item.setInfo('video', {'title': category['name'],
                                        'genre': category['name'],
                                        'mediatype': 'video'})
            list_item.setProperty('IsPlayable', 'true')
            # Create a URL for a plugin recursive call.
            # Example: plugin://plugin.video.example/?action=listing&category=Animals
            url = get_url(action='listing', category=category['url'])
            # Add our item to the Kodi virtual folder listing.
            xbmcplugin.addDirectoryItem(_handle, url, list_item, True)
    list_end()


def list_videos(url):
    """
    Create the list of playable videos in the Kodi interface.

    :param url: url
    :type url: str
    """
    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    xbmcplugin.setPluginCategory(_handle, url if url[:4] != 'http' else '/'.join(url.split('/')[3:]))
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(_handle, 'videos')
    # Get the list of videos in the page.
    videos, next_page = get_videos(url)

    downloader_path = os.path.join(xbmcaddon.Addon().getAddonInfo('path'), 'resources', 'lib', 'pornky', 'downloader.py')
    # Iterate through videos.
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': '%s (%s)' % (video['name'], video['duration']),
                                    'genre': video['categories'],
                                    'mediatype': 'video'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})

        url = get_url(action='download', video_page=video['page'], video_name=video['name'])
        context_menu = [('Download video',
                         'RunPlugin({})'.format(url))]
#                         'ActivateWindow(busydialog)')]
#                         'ActivateWindow(yesnodialog,{},return'.format(url))]
        list_item.addContextMenuItems(context_menu)

        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='play', video=video['page'])
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    if next_page:
        list_item = xbmcgui.ListItem(label=next_page['name'])
        list_item.setInfo('video', {'title': next_page['name'],
                                    'genre': next_page['name'],
                                    'mediatype': 'video'})
        url = get_url(action='listing', category=next_page['url'])
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    list_end()


def search_dialog():
    keyboard = xbmc.Keyboard('', "Search")
    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return
    search_string = keyboard.getText()
    if len(search_string) == 0:
        return
    query = urllib.quote('%s' % search_string)
    search_url = pornky.URL_SEARCH % query
    list_videos(search_url)


def search_menu():
    xbmcplugin.setPluginCategory(_handle, 'Search')
    xbmcplugin.setContent(_handle, 'videos')

    list_item = xbmcgui.ListItem('Search form ...')
    list_item.setInfo('video', {'title': 'Search',
                                'genre': 'Search form ...',
                                'mediatype': 'video'})
    url = get_url(action='search', category='')
    is_folder = True
    xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)

    for i in cfg.search_items:
        list_item = xbmcgui.ListItem(label=i)
        list_item.setInfo('video', {'title': i,
                                    'genre': i,
                                    'mediatype': 'video'})
        #list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        #list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        url = get_url(action='listing', category='search/?q='+i)
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(_handle, url, list_item, is_folder)
    list_end()

def show_image(path):
    # Create a playable item with a path to play.
    #play_item = xbmcgui.ListItem(path=path)
    # Pass the item to the Kodi player.
    #xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)
    xbmc.executebuiltin("ShowPicture(%s)" % path)


def play_video(path):
    """
    Play a video by the provided path and the resolution from config.

    :param path: Fully-qualified video page URL
    :type path: str
    """
    video = pornky.get_video_link(path, cfg.res.res())
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=video[1])
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_handle, True, listitem=play_item)


def router(paramstring):
    """
    Router function that calls other functions
    depending on the provided paramstring

    :param paramstring: URL encoded plugin paramstring
    :type paramstring: str
    """
    # Parse a URL-encoded paramstring to the dictionary of
    # {<parameter>: <value>} elements
    params = dict(parse_qsl(paramstring))
    # Check the parameters passed to the plugin
    if params:
        if params['action'] == 'listing':
            # Display the list of videos in a provided category.
            list_videos(params['category'])
        elif params['action'] == 'play':
            # Play a video from a provided URL.
            play_video(params['video'])
        elif params['action'] == 'categories':
            list_categories()
        elif params['action'] == 'searchmenu':
            # Search menu.
            search_menu()
        elif params['action'] == 'search':
            # Show search dialog
            search_dialog()
        elif params['action'] == 'donatemenu':
            # Show search dialog
            donate_menu()
        elif params['action'] == 'show':
            # Show image
            show_image(params['category'])
        else:
            # If the provided paramstring does not contain a supported action
            # we raise an exception. This helps to catch coding errors,
            # e.g. typos in action names.
            raise ValueError('Invalid paramstring: {0}!'.format(paramstring))
    else:
        # If the plugin is called from Kodi UI without any parameters,
        # display the list of video categories
        list_root()


def router_special(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        xbmc.log(params['action'], xbmc.LOGERROR)
        if params['action'] == 'download':
            # Download
            xbmc.log('Download routine started', xbmc.LOGERROR)
            xbmc.log('for video {}'.format(params['video_name']), xbmc.LOGERROR)
            res = Res(int(xbmcaddon.Addon(id=_id).getSetting('res')))
            download_path = xbmcaddon.Addon(id=_id).getSetting('download_path')
            if not download_path:
                xbmcgui.Dialog().ok('Download Error!', 'Download path is not set!')
                return

            video_url = pornky.get_video_link(params['video_page'], res.res())[1]
            xbmc.log('Downloading: {}'.format(video_url), xbmc.LOGERROR)
            video_name = re.sub('[^0-9A-Za-z _-]+', '', params['video_name']).replace(' ', '_')

            xbmc.log('as: {}'.format(video_name), xbmc.LOGERROR)
            size = int(requests.head(video_url, allow_redirects=True).headers.get('content-length', 0))
            xbmc.log('Size: {} MB'.format(str(size >> 20)), xbmc.LOGERROR)

            result = 'Download Error!'
            with busy_dialog():
                try:
                    r = requests.get(video_url)
                    with open(os.path.join(download_path, video_name + '.mp4'), "wb") as video_file:
                        video_file.write(r.content)
                    result = 'Download Complete!'
                except:
                    pass
            xbmc.log(result, xbmc.LOGERROR)
            xbmcgui.Dialog().ok(result, result)


# Get the plugin url in plugin:// notation.
_url = sys.argv[0]
_id = _url.replace('plugin://', '').replace('/', '')
# Get the plugin handle as an integer number.
_handle = int(sys.argv[1])
_version = '0.9.2'

if __name__ == '__main__':
    pornky = Pornky()

    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring

    xbmc.log(str(sys.argv), xbmc.LOGERROR)

    # xbmc.log('Kodi version: %s' % xbmc.getInfoLabel('System.BuildVersion'), xbmc.LOGERROR)

    if _handle == -1:
        router_special(sys.argv[2][1:])
    else:
        cfg = Cfg()

        cfg.res = Res(int(xbmcplugin.getSetting(_handle, 'res')))
        cfg.search_items = xbmcplugin.getSetting(_handle, 'search_items').split(',')

        cfg.filter = Filter(int(xbmcplugin.getSetting(_handle, 'filter')))
        cfg.filter_items = xbmcplugin.getSetting(_handle, 'filter_items').split(',')

        cfg.username = xbmcplugin.getSetting(_handle, 'username')
        cfg.password = xbmcplugin.getSetting(_handle, 'password')

        cfg.cookie_PHPSESSID = xbmcplugin.getSetting(_handle, 'cookie_PHPSESSID')
        cfg.cookie_XSAE = xbmcplugin.getSetting(_handle, 'cookie_XSAE')

        cfg.disable_login = xbmcplugin.getSetting(_handle, 'disable_login') == 'true'

        logged_in, cookies = pornky.set_cookies(cfg)
        if logged_in and cookies:
            xbmcaddon.Addon(_id).setSetting(id='cookie_XSAE', value=cookies['XSAE'])
            xbmcaddon.Addon(_id).setSetting(id='cookie_PHPSESSID', value=cookies['PHPSESSID'])
        if not logged_in and cfg.username and cfg.password and not cfg.disable_login:
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('pornky.com', 'Login error.\nCheck username/password or disable login.')
        router(sys.argv[2][1:])
