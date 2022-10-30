''' xxx '''
import time
import requests

time1 = time.time()
for number in range(1, 151):
    url = f'https://pokeapi.co/api/v2/pokemon/{number}'
    resp = requests.get(url,timeout=2)
    pokemon = resp.json()
    print(pokemon['name'])
time2 = time.time()

print (f"Synchronous Elapsed Time: {time2 - time1} seconds")
