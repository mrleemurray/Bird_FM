### BirdFM

import urllib.request
import json
import time
from playsound import playsound

def makeApiCall(_url, _country, _since):
    assembledUrl = _url + '?query=cnt:"' + _country.replace(' ', '%20') + '"+since:' + str(_since)
    print(assembledUrl)
    with urllib.request.urlopen(assembledUrl) as response:
        return json.loads(response.read())

def playBirdsong(_recordings, _index, _location=None):
    try:
        if (_location is not None):
            if (_location not in _recordings['recordings'][_index]['loc']):
                return
        sound_file_url = 'https://'
        sound_file_url += _recordings['recordings'][_index]['sono']['small'].split('ffts')[0].replace('//', '')
        sound_file_url += _recordings['recordings'][_index]['file-name'].replace(' ', '%20')
        print(_recordings['recordings'][_index]['en'] + ', ' + _recordings['recordings'][_index]['loc'])
        playsound(sound_file_url)
        time.sleep(2)
    except KeyError:
        print('Cannot play audio')

while True:
    with open('countries.json') as country_file:
        countries = json.load(country_file)
        for x in range(0, len(countries['countries'])):
            xeno_data = (makeApiCall('https://www.xeno-canto.org/api/2/recordings', countries['countries'][x], 1))
            for i in range(0, int(xeno_data['numRecordings'])):
                playBirdsong(xeno_data, i)
        country_file.close()