from bs4 import BeautifulSoup as bs
import requests
import  pandas as pd
pd.set_option("display.max_rows", 50, "display.max_columns", 10)

df_links = pd.DataFrame(columns= ['Link'])

base_link = "https://hubblehq.com/office-space-london?peopleMax=25&peopleMin=10&page=1"
r = requests.get(base_link, "html.parser")
soup = bs(r.content, 'html.parser')

# find html responsible for page chooser
# find number of max pages
max_number_info = soup.find(class_ = "css-zk8w31-paginationStyle")
max_pages_number = int(str(max_number_info.find_all('li')).split('<!-- -->')[2][:2])

base_path = "https://hubblehq.com/office-space-london?peopleMax=25&peopleMin=10&"

all_links = []

for i in range(1, max_pages_number):
    page = "page={}".format(i)
    current_page = base_path + page

    print('page number: {}, link: {}'.format(i, current_page))

    r = requests.get(current_page, "html.parser")
    soup = bs(r.content, "html.parser")

    # look for specific html class containing links
    page_links_info = soup.findAll(class_ = 'css-6rnjt4-wrapperStyle')

    # get all links from page_links_info
    for link in page_links_info:
        all_links.append(link.find(class_ = 'css-v7ho7-linkStyle', href = True).get('href'))

# print(all_links)

df_main = pd.DataFrame()

for link in all_links:
    first = 'https://hubblehq.com'
    good_link = first + link
    print(good_link)
    r = requests.get(good_link, "html.parser")
    soup = bs(r.content, "html.parser")

    map_link = soup.findAll('img', attrs={'srcset': True})
    coordinates = map_link[-1]['srcset'].split('center=')[1].split('&zoom')[0]
    Lat = coordinates.split(',')[0]
    Long = coordinates.split(',')[1]

    details = soup.findAll(class_ = "css-5i54kf-officeDetailStyle")

    lst_dict = []

    for i in range(0, len(details)):

        office_price = details[i].find(
            class_="css-ubngax-wrapperStyle-marginlessStyle-contentText1-baseOverridesStyle").get_text()

        local_information = details[i].findAll(class_="css-jqw1nl-textStyle-contentText2")

        title = soup.find(class_="css-1ky4310-headingStyle-titleText1-colorStyle").get_text()

        if len(local_information) == 3:

            people = local_information[0].get_text()
            min_term = local_information[1].get_text()
            building_floor = local_information[2].get_text()

        elif len(local_information) == 2:

            people = local_information[0].get_text()
            min_term = local_information[1].get_text()
            building_floor = "No information"

        elif len(local_information) == 1:

            people = local_information[0].get_text()
            min_term = "No information"
            building_floor = "No information"

        else:
            people = "No information"
            min_term = "No information"
            building_floor = "No information"

        lst_dict.append({'Link': good_link, 'Title': title,
                         'Option': i, 'Office price': office_price,
                         'People': people, 'Min. Term': min_term,
                         'Building Floor': building_floor, 'Latitude' : Lat,
                         'Longitude': Long})

        df_dict = pd.DataFrame(lst_dict)

    df_main = pd.concat([df_main, df_dict])

print(df_main.head(10))

df_main.to_excel('All_data_no_filtrated.xlsx', engine='xlsxwriter')




