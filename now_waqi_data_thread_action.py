# coding: utf-8
"""
    To download air quality from World Air Quality Index Project
"""
import os
from datetime import datetime, timezone, timedelta
import numpy as np
import pandas as pd
import argparse
from multiprocessing import Pool, Lock
from waqip import WAQIP

your_token = "5e7d868fc7b5b904512980181cf0413364895121"


def get_waqip(token, cities=None, latlng=None):
    """
    :param token (str):
    :param cities (list):
    :param latlng (list):
    :return:
    """
    # csv format
    columns = ['date', 'tz', 'city', 'idx', 'lat', 'lon', 'aqi', 'pm25', 'pm10', 'so2', 'no2', 'o3', 'co',
               'h', 't', 'r', 'w']
    dfs_waqi = pd.DataFrame(columns=columns)

    # waqip info
    waqip = WAQIP(token)
    if cities is not None:
        for i, city_idx in enumerate(cities):
            city_data = waqip.get_city(city_idx)
            if city_data is not None:
                dfs_waqi = dfs_waqi.append(city_data, ignore_index=True)
        # for
    elif latlng is not None:
        for lat, lon in latlng:
            city_data = waqip.get_latlon(lat, lon)
            if city_data is not None:
                dfs_waqi = dfs_waqi.append(city_data, ignore_index=True)
        # for
    else:
        raise ValueError('Please ensure cities or latlng must be is not None at least!')

    return dfs_waqi


def thread_task(cities):
    return get_waqip(token=your_token, cities=cities)


def main():
    now = datetime.now(timezone(timedelta(hours=8)))
    print("###########################################################")
    print("### WAQIP in China (using multiprocessing) ################")
    print("###", now, "######################")
    print("###########################################################")
    yr_mth = now.strftime("%Y-%m")
    date_time = now.strftime('%Y_%m_%d_%H_%M_%S')

    # csv format
    columns = ['date', 'tz', 'city', 'idx', 'lat', 'lon', 'aqi', 'pm25', 'pm10', 'so2', 'no2', 'o3', 'co',
               'h', 't', 'r', 'w']
    dfs_main = pd.DataFrame(columns=columns)

    # reading city meta for further fetching
    city_meta = "./data/city_metainfo_00000000.csv"
    city_csv = pd.read_csv(city_meta, index_col=0, encoding="gbk")
    cities = city_csv.idx.values

    # setup multi-processor tasks
    num_processor = 8
    async_results = []
    pool = Pool(processes=num_processor)
    for i in np.arange(0, len(cities), num_processor):
        async_results.append(pool.apply_async(thread_task, args=(cities[i:i+num_processor], )).get())

    # wait and gather results
    pool.close()
    pool.join()
    for result in async_results:
        dfs_main = dfs_main.append(result, ignore_index=True)

    # folder and file to store results
    store_data_folder = os.path.join("./data/", yr_mth)
    if not os.path.exists(store_data_folder):
        os.makedirs(store_data_folder)
    store_data_file = os.path.join(store_data_folder, (date_time + "_WAQIP_China.csv"))
    dfs_main.to_csv(store_data_file, index=True, encoding="gbk")

    print("### Task over @ {}".format(date_time))


if __name__ == '__main__':
    main()
