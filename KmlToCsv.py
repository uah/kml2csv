"""
A script to take all of the LineString information out of a very large KML file. It formats it into a CSV file so
that you can import the information into the NDB of Google App Engine using the Python standard library. I ran this
script locally to generate the CSV. It processed a ~70 MB KML down to a ~36 MB CSV in about 8 seconds.

The KML had coordinates ordered by
    [Lon, Lat, Alt, ' ', Lon, Lat, Alt, ' ',...]   (' ' is a space)
The script removes the altitude to put the coordinates in a single CSV row ordered by
    [Lat,Lon,Lat,Lon,...]

Dependencies:
 - Beutiful Soup 4
 - lxml

I found a little bit of help online for using BeautifulSoup to process a KML file. I put this online to serve as
another example. Some things I learned:
 - the BeautifulSoup parser *needs* to be 'xml'. I spent too much time debugging why the default one wasn't working, and
   it was because the default is an HTML parse, not XML.


tl;dr
KML --> CSV so that GAE can go CSV --> NDB
"""

from bs4 import BeautifulSoup
import csv
import sys


def process_coordinate_string(str):
    """
    Take the coordinate string from the KML file, and break it up into [Lat,Lon,Lat,Lon...] for a CSV row
    """
    space_splits = str.split(" ")
    ret = []
    space_splits = [split.strip() for split in space_splits if not split.isspace()]
    for split in space_splits:
        comma_split = split.split(',')
        #ret.append(comma_split[1])    # lat
        #ret.append(comma_split[0])    # lng
        _ = (comma_split[1], comma_split[0])
        ret.append(_)
    return ret

def process_folder(folder):
    f_ret = []

    for placemark in folder.find_all('Placemark'):
        p_name = placemark.find('name').string

        p_coordinates = process_coordinate_string(placemark.find('coordinates').string)
        p_coordinates_string = str(p_coordinates)
        for bad in list("[]'"):
            p_coordinates_string = p_coordinates_string.replace(bad, "")

        p_description_element = placemark.find('description')
        if p_description_element is None:
            p_description = None
        else:
            #I cannot believe I'm doing this
            p_description_html = BeautifulSoup(p_description_element.string, 'lxml')
            p_description = p_description_html.get_text()

        p_ret = [p_name, p_description, p_coordinates_string]
        f_ret.append(p_ret)

    return f_ret

def main():
    with open(sys.argv[1], 'r') as f:
        s = BeautifulSoup(f, 'xml')
        folders = s.find_all('Folder')
        if len(folders) == 0:
            folders = [s,] #The "List" just contains the entire document, since it has no folder structure, so we will just output one "folder".
        for folder in folders:
            folder_name = folder.find('name').string
            with open(sys.argv[2] + "/" + ''.join(filter(str.isalnum, folder_name)) + ".csv", 'w') as csvfile:
                writer = csv.writer(csvfile)
                folder = process_folder(folder)
                for placemark in folder:
                    writer.writerow(placemark)

if __name__ == "__main__":
    main()
