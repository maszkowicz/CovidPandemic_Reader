COVID-19 Pandemic reader
========================

This programme gets COVID-19 pandemic data, country by country, draws trend plots, and sends OSC messages to a sound related software in a given pace.

Data referred to repository for the 2019 Novel Coronavirus Visual Dashboard operated by the Johns Hopkins University Center for Systems Science and Engineering (JHU CSSE). Also, Supported by ESRI Living Atlas Team and the Johns Hopkins University Applied Physics Lab (JHU APL).

Running this program
--------------------

typing “python get_data.py” alone will not work. Usage wants at least one country related argument such as:

“python get_data.py Switzerland”

For more countries type:

“python get_data.py Switzerland Greenland Macau Hubei ‘Hong Kong’”

please note that one can type all country states, but not US States which are in another data set.

For listing all countries type

“python get_data.py -c”

If you want to get plots, add “-p”

If you want to send OSC messages at a given adress and a given pace, add “-m”