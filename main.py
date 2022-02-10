from geopy.geocoders import Nominatim
from haversine import haversine
import numpy as np
import folium
import argparse

def get_info_argparse():
    """
    Get the info from command line

    The arguments are: year, latitude, longitude, path to file with data
    """
    parser = argparse.ArgumentParser()
    # 2000 49.83826 24.02324 path_to_dataset
    parser.add_argument('year', type=str)
    parser.add_argument('lt', type=float)
    parser.add_argument('ln', type=float)
    parser.add_argument('path_to_dataset', type=str)

    args = parser.parse_args()

    year = args.year
    lat = args.lt
    lon = args.ln
    path_data = args.path_to_dataset
    return year, lat, lon, path_data


def read_data_from_file(path_to_file, year):
    """
    Read the file with data and return list with
    tuples
    first element -> movie name
    second element -> name of the place
    """
    my_file = open(path_to_file, "r", encoding = 'latin1')
    content_list = my_file.readlines()
    # print(content_list)
    # year = "1895"
    del content_list[:14]
    movies = []
    for line in content_list:
        if "("+year+")" in line:
            line= line.replace("\t", " ")
            line= line.strip()
            try:
                uu = line.index("{")
                vv = line.index("}")
                line = line[0:uu]+line[vv+1:len(line)]
                # line[uu:vv+1]
            except ValueError: pass
            scob = line.index("(")
            while line[scob+5] != ")":
                scob = line[:scob+1].index("(")
            checking = line[scob+8:].strip()
            try:
                ff = checking.index("(")
                checking = checking[:ff-1]
            except: checking = checking
            tup = (line[:scob-1], checking)
            movies.append(tup)

    movies = list(set(movies))
    return movies


def locate_movie_places(movies, lat, lon):
    """
    Locates places and counts distance to them
    from the initial coordinates
    Returns list with tuples:
    first element -> movie name
    second element -> its latitude
    third element -> its longtitude
    forth element -> distance
    and list with distances
    """
    loc = Nominatim(user_agent="GetLoc")
    movie_distances = []
    lengs = []
    for tup in movies:
        name = tup[1]
        try:
            getLoc = loc.geocode(name)
            lt = getLoc.latitude
            ln = getLoc.longitude
        except: 
            try:
                name = name.split(",")
                # print(name)
                if len(name) >= 4:
                    name = name[-3:]
                # print(name)
                name = ",".join(name)
                name= name.strip()
                getLoc = loc.geocode(name)
                lt = getLoc.latitude
                ln = getLoc.longitude
            except: 
                try:
                    name = name.split(",")
                    # print(name)
                    if len(name) >= 3:
                        name = name[-2:]
                    # print(name)
                    name = ",".join(name)
                    name= name.strip()
                    getLoc = loc.geocode(name)
                    lt = getLoc.latitude
                    ln = getLoc.longitude
                except: pass#print(name)
        # print(name)
        getLoc = loc.geocode(name)
        lt = getLoc.latitude
        ln = getLoc.longitude
        # print(lt, ln)
        leng = haversine((lt, ln), (lat, lon))
        if (tup[0], lt, ln, leng) not in movie_distances:
            movie_distances.append((tup[0], lt, ln, leng))
        lengs.append(leng)
    return movie_distances, lengs


def find_top_ten(movie_distances, lengs):
    """
    Finds 10 closest places by picking
    10 min lengths
    
    """
    top_ten = []
    if len(lengs) > 10:
        numbers = np.array(lengs)
        qq = np.argpartition(numbers,10)[-10:]
        for i in qq:
            top_ten.append(movie_distances[i])
        # print(qq)
    else: top_ten = movie_distances
    return top_ten


def create_map(lat, lon, top_ten):
    """
    Creates htmp file with map and ten markers
    using folium library
    """
    map = folium.Map(location=[lat, lon],
                    zoom_start = 10)

    fg = folium.FeatureGroup(name = 'movies')
    for tup in top_ten:
        fg.add_child(folium.Marker(location=[tup[1], tup[2]],
            popup = tup[0],
            icon = folium.Icon()))

    map.add_child(fg)

    third_layer = folium.FeatureGroup(name = 'location')
    third_layer.add_child(folium.CircleMarker(location = [lat, lon], radius = 25, color = 'blue', fillcolor='yellow'))

    map.add_child(third_layer)

    map.add_child(folium.LayerControl())
    map.save('Map_third.html')


def main():
    """
    Main function
    """
    year, lat, lon, path_data = get_info_argparse()
    movies = read_data_from_file(path_data, year)
    movie_distances, lengs = locate_movie_places(movies, lat, lon)
    top_ten = find_top_ten(movie_distances, lengs)
    create_map(lat, lon, top_ten)


if __name__ == "__main__":
    main()
