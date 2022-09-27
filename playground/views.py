from django.shortcuts import render
from django.http import HttpResponse


def clearHTMLCode(htmlCode):
    result = htmlCode
    result = result.replace("['']", "")
    result = result.replace("']", "")
    result = result.replace("['", "")
    result = result.replace("', '", " ")
    return result


def addSortingButtons(newHTML, df):
    newHTML = newHTML.replace("<table ", '<table id="myTable" ')
    for col in df.columns:
        newHTML = newHTML.replace("<th>"+col+"</th>", '<th onclick="sortTable(0)">' + col + '</th>')
    # print(newHTML)
    return newHTML


def deleteIDColumn(newHTML, nrows=2):
    newHTML = newHTML.replace("<th></th>", '')
    for i in range(nrows):
        id = str(i)
        newHTML = newHTML.replace("<th>" + id + "</th>", '')
    return newHTML


def addLinksToRefNo(newHTML, RNList):
    for i in range(len(RNList)):
        id = str(RNList[i])
        ipaddress = "http://127.0.0.1:8000/playground/hello/" + id
        href = '<a href="' + ipaddress + '" target="_blank">' + id + '</a>'
        currrentTD = "<td>" + id + "</td>"
        newHTML = newHTML.replace(currrentTD, '<td>' + href + '</td>')
    return newHTML


def deleteNewLineSigns(newHTML):
    return newHTML.replace('\\n', '<br>').replace('\\t', '\t')


def addLinksToCityName(newHTML, RNList, cityNames):
    for i in range(len(RNList)):
        id = str(RNList[i])
        cityName = str(cityNames[i])
        ipaddress = "http://127.0.0.1:8000/playground/hello/" + id + "/city"
        href = '<a href="' + ipaddress + '" target="_blank">' + cityName + '</a>'
        currrentTD = "<td>" + cityName + "</td>"
        newHTML = newHTML.replace(currrentTD, '<td>' + href + '</td>')
    return newHTML


def say_hello(request):
    from scripts import loadFromCSV as load
    load.run()
    from playground.models import Offer
    offer_list = Offer.objects.all()

    import pandas as pd
    nrows = 3
    df = pd.read_csv("AllOffers_21_09_2022.csv", nrows=nrows)
    df = df[["RefNo", "City", "Deadline"]]
    newHTML = clearHTMLCode(df.to_html())
    newHTML = deleteNewLineSigns(newHTML)
    newHTML = deleteIDColumn(newHTML, nrows)
    newHTML = addSortingButtons(newHTML, df)
    newHTML = addLinksToRefNo(newHTML, df["RefNo"])
    newHTML = addLinksToCityName(newHTML, df["RefNo"], df["City"])

    with open('test.txt', 'w') as f:
        f.write(newHTML)

    return render(request, "playground_view_1.html", {"table": newHTML, "offer_list": offer_list})


def findGeocode(city):
    from geopy.exc import GeocoderTimedOut
    from geopy.geocoders import Nominatim
    import numpy as np
    # try and catch is used to overcome
    # the exception thrown by geolocator
    # using geocodertimedout
    try:
        # Specify the user_agent as your
        # app name it should not be none
        geolocator = Nominatim(user_agent="your_app_name")
        return geolocator.geocode(city)

    except GeocoderTimedOut:
        return findGeocode(city)

def getLongAndLat(cityName):
    import numpy as np
    loc = findGeocode(cityName)

    if loc != None:
        return loc.latitude, loc.longitude
    else:
        return 0,0

def createMap(cityName):
    import folium
    print('city:' + cityName)
    latitude, longitude = getLongAndLat(cityName)
    print('long lat:' + str(longitude) + " " + str(latitude))
    # adjust position of view of the map
    my_map = folium.Map(
        location=[13, 16],
        zoom_start=2,
    )

    # set marker for the offer
    #html = popup_html(offer)
    #popup = folium.Popup(folium.Html(html, script=True), max_width=500)
    folium.Marker(location=[latitude, longitude],
                  icon=folium.Icon(color='blue', icon='university', prefix='fa')).add_to(my_map)

    # save the map
    my_map.save("map.html")
    return my_map

    # open the map
    # webbrowser.open("map.html")


def findCityOfOfferWithId(question_id):
    import pandas as pd
    df = pd.read_csv("AllOffers_21_09_2022.csv")
    offer = df.loc[df['RefNo'] == question_id]
    return str(offer["City"].item())


def city(request, question_id):
    cityName = findCityOfOfferWithId(question_id)
    print("MAP:")
    print(cityName)
    map = createMap(cityName)
    print("-- \n\n")
    map.save("map.html")
    html_string = map.get_root().render()
    return render(request, "city_view_1.html", {"map": html_string})


def detail(request, question_id):
    from playground.models import Offer
    offer_list = Offer.objects.all()

    import pandas as pd
    OfferId = question_id
    df = pd.read_csv("AllOffers_21_09_2022.csv")
    rowWithOffer = df.loc[df['RefNo'] == OfferId]
    rowWithOffer = rowWithOffer.transpose() # to show it vertically
    newHTML = clearHTMLCode(rowWithOffer.to_html())
    newHTML = deleteNewLineSigns(newHTML)
    newHTML = deleteIDColumn(newHTML)
    return render(request, "detail_view_1.html", {"table": newHTML, "offer_list": offer_list})


def results(request, question_id):
    return HttpResponse("This is the result of the question: %s" % question_id)


def vote(request, question_id):
    tostr = str(question_id)
    return render(request, "view2.html", {"name": tostr})


from django_tables2 import SingleTableView

from .models import Person
from .tables import PersonTable
from django_filters.views import FilterView
from django_tables2.views import SingleTableMixin


class PersonListView(SingleTableMixin, FilterView):
    table_class = PersonTable
    model = Person
    template_name = "../templates/people.html"
