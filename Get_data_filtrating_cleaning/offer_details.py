from bs4 import BeautifulSoup as bs
import requests
import pandas as pd

pd.set_option("display.max_rows", 20, "display.max_columns", 10)

base_link = "https://hubblehq.com/office-space/7629/boutique-workplace-theobalds-road?option=34605"
r = requests.get(base_link, "html.parser")
soup = bs(r.content, 'html.parser')

df = pd.DataFrame(columns = ['Link', 'Title', 'Option', 'Office price', 'People', 'Min. Term', 'Building Floor'])

map_link = soup.findAll('img', attrs = {'srcset' : True})
coordinates = map_link[-1]['srcset'].split('center=')[1].split('&zoom')[0]

Lat = coordinates.split(',')[0]
Long = coordinates.split(',')[1]

print('latitude = {}, longitude = {}'.format(Lat, Long))



