# COVID-19 Pandemic reader

This programme gets COVID-19 pandemic data, country by country, draws trend plots, and sends OSC messages to a sound related software at a given pace.

Data referred to repository for the 2019 Novel Coronavirus Visual Dashboard operated by the Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE). Also, Supported by ESRI Living Atlas Team and the Johns Hopkins University Applied Physics Lab (JHU APL).

# Running this program

## First time Use

type <b>python get_data.py -r</b> This will get the data from the web and put it in the right folder

## Full Listing

type <b>python get_data.py -c -m -p</b> for full programme potential! It lists all countries, plots all trends, and sends everything throuhg OSC link.

## Specific Use

typing <b>python get_data.py</b> alone will not work. Usage wants at least one country related argument such as:

<b>python get_data.py Switzerland</b>

For more countries simply type:

<b>python get_data.py Switzerland Greenland Macau Hubei ‘Hong Kong’</b>

please note that one can type all country states, but not US States which are in another data set.

## Arguments

For listing all countries add <b>-c</b>

If you want to get plots, add <b>-p</b>

If you want to send OSC messages at a given address and a given pace (hardcoded in software), add <b>-m</b>

For updating data, add <b>-r</b>, otherwise the programme will get it from local folder

# Getting OSC message with SuperCollider

Run file covid_sonification.scd in SuperCollider for getting OSC message sent from Python programme