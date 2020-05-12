#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May  8 20:53:29 2020

@author: Daniel Maszkowicz
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sys
import requests
from pythonosc.udp_client import SimpleUDPClient
import time

### Constants and Global Variables
# OSC communication for SuperCollider use
ip_osc = "127.0.0.1"
port_osc = 9002
client_osc = SimpleUDPClient(ip_osc, port_osc)

# path for CSV data
path_confirmed = "./Data/time_series_covid19_confirmed_global.csv"
path_healed = "./Data/time_series_covid19_recovered_global.csv"
path_deaths = "./Data/time_series_covid19_deaths_global.csv"

# data held in Panda format
df_confirmed = pd.read_csv(path_confirmed)
df_healed = pd.read_csv(path_healed)
df_deaths = pd.read_csv(path_deaths)

### OSC data files update from their web location
def update_data():
    url_confirmed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv'
    url_healed = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_recovered_global.csv'
    url_deaths = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv'

    r = requests.get(url_confirmed, allow_redirects=True)
    with open(path_confirmed, "wb") as file:
        file.write(r.content)

    r = requests.get(url_healed, allow_redirects=True)
    with open(path_healed, "wb") as file:
        file.write(r.content)

    r = requests.get(url_deaths, allow_redirects=True)
    with open(path_deaths, "wb") as file:
        file.write(r.content)

### Checking Data, Country by Country
def select_country(country):
    region_label = "Country/Region"
    # in case of inconsistency, use minimal array length out of the three data sets
    length = min(len(df_deaths.columns),len(df_confirmed.columns),len(df_healed.columns))
    # Special country World, take the sum of all datasets
    if country == "World":
        item_array = df_deaths.sum(axis = 0,skipna = True).to_numpy()
        item_deaths = item_array[2:length:1]
        item_deaths = item_deaths.astype('float32')

        item_array = df_confirmed.sum(axis = 0,skipna = True).to_numpy()
        item_confirmed = item_array[2:length:1]
        item_confirmed = item_confirmed.astype('float32')

        item_array = df_healed.sum(axis = 0,skipna = True).to_numpy()
        item_healed = item_array[2:length:1]
        item_healed = item_healed.astype('float32')
    else:
        # check if variable country is actually a Country or a State
        item = df_confirmed.loc[(df_confirmed[region_label] == country)]
        if item.shape[0] == 0:
            region_label = "Province/State"
            item = df_confirmed.loc[(df_confirmed[region_label] == country)]
            if item.shape[0] == 0:
                print("Couldn't find such Country or State")
                sys.exit(1)
        # Get an array for the given country
        # some countries have several rows and need to be summed
        item = df_confirmed.loc[(df_confirmed[region_label] == country)]
        item_array = item.groupby([region_label]).sum().to_numpy()
        item_confirmed = item_array[0,2:length:1]
        item_confirmed = item_confirmed.astype('float32')

        item = df_healed.loc[(df_healed[region_label] == country)]
        item_array = item.groupby([region_label]).sum().to_numpy()
        item_healed = item_array[0,2:length:1]
        item_healed = item_healed.astype('float32')

        item = df_deaths.loc[(df_deaths[region_label] == country)]
        item_array = item.groupby([region_label]).sum().to_numpy()
        item_deaths = item_array[0,2:length:1]
        item_deaths = item_deaths.astype('float32')

    # Generate a new array for Active cases, and normalize them
    max_value = np.max(item_confirmed)
    item_confirmed_norm = item_confirmed / max_value
    item_deaths_norm = item_deaths / max_value
    item_healed_norm = item_healed / max_value
    item_active = item_confirmed_norm - item_deaths_norm - item_healed_norm

    # Very simple analysis that will be printed later on
    if item_active[-1] > 0.9*peak_active:
        tendency = "Sitation is out of control"
    elif item_active[-1] > 0.5*peak_active:
        tendency = "Sitation is bad, but stable"
    elif item_active[-1] > 0.1*peak_active:
        tendency = "Sitation is good, but watch out the second wave"
    elif item_active[-1] > 0:
        tendency = "Almost recovered"
    else:
        tendency = "Free of Covid"

    return item_confirmed_norm, item_healed_norm, item_deaths_norm, item_active, np.array2string(max_value.astype(int)), tendency

### Get list of considered countries
def list_countries(args):
    list_countries = set()
    # list all countries in a set, if asked so
    if args.countries:
        for item in range(df_confirmed.shape[0]):
            list_countries.add(str(df_confirmed.iloc[(item,1)]))
        list_countries=sorted(list_countries)
        list_countries.append('World')
        return list_countries
    # use list of countries given as argument, if asked so
    # return a list if argument is a single string
    if isinstance(args.country, str):
        return [args.country]
    else:
        return args.country

### arguments
def parse_args():
    from argparse import ArgumentParser
    p = ArgumentParser()
    #type a single country or more
    p.add_argument("country", nargs="*", default=None)
    #refresh data from the web
    p.add_argument("--refresh_data", "-r", action="store_true", default=False)
    #list ALL countries
    p.add_argument("--countries", "-c", action="store_true", default=False)
    #plot figures after analysis
    p.add_argument("--plot", "-p", action="store_true", default=False)
    #send OSC after analysis
    p.add_argument("--osc", "-m", action="store_true", default=False)
    args = p.parse_args()
    if args.countries:
        print("listing countries/states")
    elif args.country is None:
        print("type a country")
        p.print_usage()
        sys.exit(1)
    if args.osc:
        print("Sending OSC")
    return args

### Main Programme
if __name__ == "__main__":
    # get arguments
    args = parse_args()
    # update data if needed
    if args.refresh_data:
        update_data()
    # list countries to be considered
    country_list = list_countries(args)
    i = 0
    # Perform analysis for each country
    for country in country_list:
        # if ALL countries are considered, all are ploted on the same figure
        # use separate figures otherwise
        if args.countries:
            i=1
        else:
            i+=1
        # get specific Data for each country
        item_confirmed_norm, item_healed_norm, item_deaths_norm, item_active, max_value, tendency  = select_country(country)
        print(country+" : "+max_value + " cases -> "+tendency)
        # If needed, print the curves corresponding to the given country
        if args.plot:
            plt.figure(num=i,figsize=(3,3), dpi=100)
            plt.clf()
            plt.plot(item_confirmed_norm, 'k', label='confirmed')
            plt.plot(item_healed_norm, 'g', label='healed')
            plt.plot(item_deaths_norm, 'r', label='deaths')
            plt.plot(item_active, 'y', label='active')
            plt.title(country+"\n"+max_value + " cases")
            plt.xlabel('days from 22nd January')
            plt.ylabel('relative number of cases')
            plt.yticks([0,1])
            plt.tight_layout()
            plt.pause(0.01)
        # If needed, send OSC messages related to active cases and total cases
        if args.osc:
            client_osc.send_message("/pandemic/cases", float(max_value))
            # send each elements of active cases array, one by one, at a given pace
            for item in item_active:
                client_osc.send_message("/pandemic/curve", item.item())
                time.sleep(1/1000)
            client_osc.send_message("/pandemic/country", country)
            #time.sleep(0.01)
    # after a full round, send 0 for cutting the sound
    if args.osc:
        client_osc.send_message("/pandemic/curve", 0)
    plt.show()
