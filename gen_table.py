import os
import sys
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from bs4.element import Tag
import pandas as pd

from utils import load_config

BASE_URL = "https://www.jleague.jp"

CONFIG_FILENAME = "config.yml"

config = load_config(CONFIG_FILENAME)


def get_soup(resource_url) -> BeautifulSoup:
    html = requests.get(resource_url)
    print("get: " + resource_url)
    return BeautifulSoup(html.text, 'lxml')


def get_soup_by_selenium(resource_url) -> BeautifulSoup:
    with webdriver.Chrome(config["driver_path"]) as driver:
        driver.get(resource_url)
        print("get: " + resource_url)
        html = driver.page_source.encode('utf-8')
        return BeautifulSoup(html, 'lxml')


def gen_players_table(team_soup: BeautifulSoup, out_dir_path):
    players_data_table = team_soup.find("table", class_="playerDataTable")
    out_path = out_dir_path + "/players.csv"
    pd.read_html(str(players_data_table))[0].to_csv(
        out_path, index=False)
    print("out: " + out_path)


def gen_player_season_score_table(team_soup: BeautifulSoup, out_dir_path):
    table_body = team_soup.find("tbody")
    for r in table_body:
        if(type(r) is Tag):
            data_href = r.get("data-href")
            soup = get_soup(BASE_URL + data_href)
            season_score_table = soup.find(
                "table", {'id': 'season-score-table'})  # 今シーズンの成績
            player_records = [elm.text for elm in r.find_all("td")]
            # 背番号と名前
            player_number, player_name = player_records[0], player_records[3]
            out_path = out_dir_path+"/"+player_name+"_"+player_number+".csv"
            pd.read_html(str(season_score_table))[
                0].to_csv(out_path, index=False)
            print("out: " + out_path)


def main():
    args = sys.argv
    out_dir_path = args[1]
    if not os.path.isdir(out_dir_path):
        os.makedirs(out_dir_path)
    team_url = args[2]
    players_soup = get_soup_by_selenium(team_url + "/player")
    gen_players_table(players_soup, out_dir_path)
    gen_player_season_score_table(players_soup, out_dir_path)


if __name__ == '__main__':
    main()
