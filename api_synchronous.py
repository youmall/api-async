''' Synchronous API calls '''
import time
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
import requests

conf = {
    'site_url':'https://pokeapi.co',
    'path_url':'/api/v2/pokemon/', # +ve integer path param is added to this path
    'workload_limit': 150,
    'timeout': 1  # Can be a Tuple as in (ConnectTimeout :float, readTimeout :float) both in seconds
}

def get_names(from_url :str) -> list[str]:
    ''' Get names '''
    v_names = []
    for i in range(1, conf.get('workload_limit')+1):
        try:
            resp = requests.get(
                url = f"{from_url}{i}", #if (i % 2) != 0 else 'https://httpbin.org/status/504',
                timeout = conf.get('timeout'),
                allow_redirects=False
            )
            resp.raise_for_status()
            resp_dict = resp.json()
            name = resp_dict.get('name')
            v_names.append(name)
            print (f"#{i} - {name}")
        except Timeout as ex:
            # Timeout will catch both ConnectTimeout and ReadTimeout
            print(f"#{i} - Timeout {type(ex)}")
        except HTTPError as ex:
            if ex.response.status_code == 504:
                print(f"#{i} - GatewayTimeout {type(ex)}")
            else:
                print(f"#{i} - HTTPError {type(ex)}")
            #end if
        except Exception as ex:
            print(f"#{i} - Exception {type(ex)}")
    # end for
    return v_names

if __name__ == "__main__":
    time1 = time.time()
    names = get_names(from_url=f"{conf.get('site_url')}{conf.get('path_url')}")
    time2 = time.time()
    print (f"Synchronous Elapsed Time: {time2 - time1} seconds for retrieval of {len(names)} names")
