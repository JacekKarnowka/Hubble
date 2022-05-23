### Hubble data analysis

#### Project describtion
[Hubble- Locals to rent in London](https://locals-to-rent-london.herokuapp.com).


Hubble project is a HubbleHQ webscraping interactive dashboard.
Data for analysis was scrapped using Beautiful Soup from [HubbleHQ](www.hubbleHQ.com) for apartments to rent in London.
Scrapped data was cleaned and filtrated using pandas python library, and visualized using dash with plotly and mapbox.

Created simple search box for apartment estimated price value, based on the price of ten closest apartments to rent.
Entered adress is translated to coordinates using [positionstack](www.positionstack.com) API request.

Finally, project app was to deployed on [Heroku](www.herokuapp.com).

#### Project elements

1. Apartments locations on map. Color indicates average price per person. Slider below plots allows to change price range and live update plot data.

![hubble_1_Easy-Resize com (2)](https://user-images.githubusercontent.com/95350394/167929043-49a0b68a-1855-4d0f-a16c-77859bee5493.jpg)


2. Next plot shows office price depending on available workplaces and distance from the geografical center of London. Slider below allows to change number of workplaces.

![hubble2_Easy-Resize com](https://user-images.githubusercontent.com/95350394/167929284-6cf80c63-6ac1-435c-b7c0-38a18099ff49.jpg)


3. Two plots on the bottom:
  - Left one shows density map, based on number of available apartments
  - Right one shows average price per person.
  
![hubble3_Easy-Resize com](https://user-images.githubusercontent.com/95350394/167929314-4b2a55fe-2356-4016-8d01-8198eaad7c32.jpg)

4. Search box allows to enter address and search for estimated value, based on the price of ten closest available apartments.

After entering London address graph is updated and the predicted value is calculated based on ten closest apartments to rent.

![hubble4_Easy-Resize com](https://user-images.githubusercontent.com/95350394/167929357-2a6437f2-d799-4cba-be0c-21032755bbe8.jpg)

#### Used tools and technology:
- Plotly,
- Dash,
- BeautifulSoup4,
- Pandas.

### Installation

1. Clone this repository: `git clone https://github.com/JacekKarnowka/Hubble.git`.
2. Create a new virtualenv called venvHubble: `python -m venv venvHubble`.
3. Activate venvHubble virtual enviroment, if all went well then your command line prompt should now start with (venvHubble).
4. Install packages: `pip install -r requirements.txt`.
5. Run app.py file: `python app.py`
