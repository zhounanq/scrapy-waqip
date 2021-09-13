# -- coding:utf-8 --

import os
import datetime
import re
import requests
import json
import pandas as pd
from bs4 import BeautifulSoup


def city_meta_re():
    city_df = pd.DataFrame(columns=['name', 'idx', 'url'])

    html = requests.get(url='http://aqicn.org/city/all')
    if html.ok:
        # get city lists
        infos = BeautifulSoup(re.findall('CHINA.*MACAO', html.text)[0], 'lxml')
        cities = infos.find_all('a', href=True)
        print("### {} cities in China found...".format(len(cities)))

        re_name = re.compile('"name":.(\w*\s*\w*)')
        re_idx = re.compile('"idx":(\d+)')

        for i, city in enumerate(cities):
            city_url = city['href']
            try:
                city_html = BeautifulSoup(requests.get(city_url).text, features="lxml")
                city_str = city_html(text=re_idx)

                city_df.loc[i, 'name'] = re.findall(re_name, city_str[0])[0]
                city_df.loc[i, 'idx'] = re.findall(re_idx, city_str[0])[0]
                city_df.loc[i, 'url'] = city_url
            except:
                print(city_url)

        # save data
        date_str = datetime.datetime.now().strftime('%Y_%m_%d')
        target_file = os.path.join("./data/", ("{}_city_metainfo.csv".format(date_str)))
        city_df.to_csv(target_file, encoding="gbk")
    print("### Task over!!!")


def city_meta_json():
    city_df = pd.DataFrame(columns=['name', 'idx', 'lat', 'lon', 'url'])

    html = requests.get(url='http://aqicn.org/city/all')
    if html.ok:
        # get city lists
        infos = BeautifulSoup(re.findall('CHINA.*MACAO', html.text)[0], 'lxml')
        cities = infos.find_all('a', href=True)
        print("### {} cities in China found...".format(len(cities)))

        for i, city in enumerate(cities):
            city_url = city['href']
            try:
                city_html = requests.get(city_url).text

                from_str = "\"city\":{"
                from_idx = city_html.find(from_str)
                assert from_idx > 0
                temp_str = city_html[from_idx+len(from_str)-1:]

                to_str = "}"
                end_idx = temp_str.find(to_str)
                assert end_idx > 0
                city_str = temp_str[:end_idx+len(to_str)]

                city_json = json.loads(city_str)
                city_df.loc[i, 'name'] = city_json['name']
                city_df.loc[i, 'idx'] = city_json['idx']
                city_df.loc[i, 'lat'] = city_json['geo'][0]
                city_df.loc[i, 'lon'] = city_json['geo'][1]
                city_df.loc[i, 'url'] = city_json['url']
            except:
                print(city_url)

        # save data
        date_str = datetime.datetime.now().strftime('%Y_%m_%d')
        target_file = os.path.join("./data/", ("{}_city_metainfo.csv".format(date_str)))
        city_df.to_csv(target_file, encoding="GB18030")
    print("### Task over!!!")


def main():
    city_meta_json()


if __name__ == '__main__':
    main()
