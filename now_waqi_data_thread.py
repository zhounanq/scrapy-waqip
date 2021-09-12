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


def parse_args():
    parser = argparse.ArgumentParser(description='Scrapy waqip info of China')
    parser.add_argument('--city-meta', required=False, type=str, default="./data/city_metainfo_00000000.csv",
                        help='city urls')
    parser.add_argument('--target-dir', required=False, type=str, default="./data/",
                        help='target dir for writing results')
    parser.add_argument('--num-process', required=False, type=int, default=4,
                        help='number of process for multiprocessing')
    opts = parser.parse_args()
    return opts


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
    print("### WAQIP in China (using multiprocessing)#################")
    print("###", now, "######################")
    print("###########################################################")
    opts = parse_args()

    # csv format
    columns = ['date', 'tz', 'city', 'idx', 'lat', 'lon', 'aqi', 'pm25', 'pm10', 'so2', 'no2', 'o3', 'co',
               'h', 't', 'r', 'w']
    dfs_main = pd.DataFrame(columns=columns)

    # reading city meta for further fetching
    city_csv = pd.read_csv(opts.city_meta, index_col=0, encoding="gbk")
    cities = city_csv.idx.values

    # setup multi-processor tasks
    async_results = []
    pool = Pool(processes=opts.num_process)
    for i in np.arange(0, len(cities), 4):
        async_results.append(pool.apply_async(thread_task, args=(cities[i:i+4], )).get())

    # wait and gather results
    pool.close()
    pool.join()
    for result in async_results:
        dfs_main = dfs_main.append(result, ignore_index=True)

    # writing results into file.
    date_str = datetime.now().strftime('%Y_%m_%d_%H_%M_%S')
    target_file = os.path.join(opts.target_dir, date_str+"_WAQIP_China.csv")
    dfs_main.to_csv(target_file, index=True, encoding="gbk")

    print("### Task over @ {}".format(date_str))


if __name__ == '__main__':
    main()
