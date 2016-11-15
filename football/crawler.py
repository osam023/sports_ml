# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import urllib
import re
import pandas as pd
import time
import requests

WAIT_TIME = 0.3

def get_archives():
    '''
    過去2006年〜2016年までのデータを取得する
    '''
    result = []
    data_uri = 'http://www.xleague.com/kiroku/'
    html_doc = urllib.request.urlopen(data_uri)
    year_pattern = '^.+(20\d{2}).+$'

    soup = BeautifulSoup(html_doc.read(), 'html.parser')
    for link in  soup.find_all('a'):
        href = link.get('href')
        if link.text.startswith('X') and href.find(u'kiroku') > 0 and href.find(u'diagram') < 0:
            matcher = re.match(year_pattern, link.get('href'))
            tmp = {}
            tmp['year'] = matcher.group(1)
            tmp['link'] = link.get('href')
            tmp['category'] = get_category(link)
            tmp['link_text'] = link.text
            result.append(tmp)
    return result


def get_category(url):
    '''
    categoryを取得する@utility
    '''
    if url.get('href').find(u'ranking') > 0:
        return 'ranking'
    elif url.get('href').find(u'result_list') > 0:
        return 'result_list'
    else:
        return None


def get_src(uri):
    '''
    iframeに埋込されているリンク先URLを取得する
    '''
    html_doc = urllib.request.urlopen(uri)
    soup = BeautifulSoup(html_doc.read(), 'html.parser')
    iframe_tag = soup.find('iframe')
    return iframe_tag.get('src')


def get_results(links):
    '''
    各試合の結果を取得する
    '''
    for link in links:
        if link['category'] == 'result_list':
            source_uri = get_src(link['link'])
            print(source_uri)

            play_info_doc = urllib.request.urlopen(source_uri)
            play_info_soup = BeautifulSoup(play_info_doc.read(), 'html.parser')
            all_play_info_link = play_info_soup.find_all('a')
            for info in all_play_info_link:
                href_object = info.get('href')
                if href_object is not None and href_object.find(u'kiroku') > 0:
                    get_play_info(info)
                    time.sleep(WAIT_TIME)
            time.sleep(WAIT_TIME)


def get_play_info(info):
    '''
    各試合の詳細情報を取得する
    '''
    source_uri = get_src(info.get('href'))
    print(source_uri)
    get_play_result(source_uri)
    get_play_personal_result(source_uri)

    
def get_charset(encodings):
    '''
    Webページの文字コードを取得する
    '''
    codings = [encoding for encoding in set(encodings)]
    coding = codings[0].lower()
    if coding == 'shift-jis':
        return 'CP932'
    else:
        return coding

def get_play_result(source_uri):
    '''
    試合結果のデータ
    '''
    response = requests.get(source_uri)
    html_body = response.text if response.text is not None else None
    html_encodings = requests.utils.get_encodings_from_content(html_body) # FIXME encoding指定のmetaタグが複数取れた場合の処理が必要
    html_encode = get_charset(html_encodings)
    result_df = pd.read_html(source_uri, encoding=html_encode) 
    print(result_df)
    result_info = {}
    result_info['condition'] = result_df[0]
    result_info['results'] = result_df[1]
    result_info['passed_result'] = result_df[2]
    result_info['stats'] = result_df[3]
    

def get_play_personal_result(source_uri):
    ## 個人記録のデータ
    player_info = []
    doc = urllib.request.urlopen(source_uri)
    soup = BeautifulSoup(doc.read(), 'html.parser')
    for ancher in soup.find_all('a'):
        if ancher.get('href').find('player') > 0:
            player_page = urllib.request.urlopen(ancher.get('href'))
            player_soup = BeautifulSoup(player_page.read(), 'html.parser')
            player_uri = player_soup.find('iframe').get('src')
            player_df = pd.read_html(player_uri, header=0)
            team_names = player_df[1]['TEAM']

            for team in team_names:
                tmp = {}
                tmp['team'] = team
                player_info.append(tmp)
#            print(len(player_df))
            
            # RUSHING
            # add_score(player_df, 'rushing', 2, player_info)
            # add_score(player_df, 'rushing', 3, player_info)

            # #PASSING
            # add_score(player_df, 'passing', 4, player_info)
            # add_score(player_df, 'passing', 5, player_info)

            # #RECIEVING
            # add_score(player_df, 'recieving', 6, player_info)
            # add_score(player_df, 'recieving', 7, player_info)

            # #TACKLE
            # add_score(player_df, 'tackle', 8, player_info)
            # add_score(player_df, 'tackle', 9, player_info)

            # #INTERCEPTION
            # add_score(player_df, 'interception', 10, player_info)
            # add_score(player_df, 'interception', 11, player_info)

            # #PASS CUT
            # add_score(player_df, 'pass_cut', 12, player_info)
            # add_score(player_df, 'pass_cut', 13, player_info)
            break


def add_score(df, target, data_num, info_object):
    '''
    target属性にdfのデータをinfo_object毎に格納する
    '''
    team_name = df[data_num].columns[0]
    for cnt, team in enumerate(info_object):
        if team_name == team['team']:
            info_object[cnt][target] = df[data_num][1:]
            break
    
def get_ranking(links):
    pass

    
def main():
    links = get_archives()
    get_results(links)
    get_ranking(links)

def test():
    # チーム成績情報 がない
    ng_uri = 'http://www.xleague.com/kiroku/archive/game/Y2010/I5062.htm'
    get_play_result(ok_uri)
    
    
if __name__ == '__main__':
#    test()
    main()
