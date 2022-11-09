''' Synchronous API calls '''
import time
from collections import namedtuple
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
import requests

Outcome = namedtuple('Outcome', 'entity_id status result')
Conf = namedtuple ('Conf', 'site_url, path_url, workload_limit, timeout')

def show_outcome(outcome :Outcome ) -> None:
    ''' Show outcome '''
    print (f"#{outcome.entity_id} - {outcome.status} - {outcome.result}")

def get_name (
    from_url :str,
    entity_id :int,
    timeout :float
) -> Outcome:
    ''' Get name '''
    try:
        resp = requests.get(
            url = from_url,
            timeout = timeout,
            allow_redirects=False
        )
        resp.raise_for_status()
        resp_dict = resp.json()
        name = resp_dict['name']
        status = 'Success'
        result = name
    except Timeout as ex:
        # Timeout will catch both ConnectTimeout and ReadTimeout
        status = 'Timeout'
        result = str(type(ex))
    except HTTPError as ex:
        if ex.response.status_code == 504:
            status = 'HTTPError/GatewayTimeout'
        else:
            status = 'HTTPError'
        #end if
        result = str(type(ex))
    except Exception as ex:
        status = 'Exception'
        result = str(type(ex))
    #end try - except
    outcome = Outcome(entity_id=entity_id, status=status, result=result)
    show_outcome (outcome)
    return outcome

def get_names (conf :Conf) -> list[str]:
    ''' Get names '''
    v_names = []
    base_url = f"{conf.site_url}{conf.path_url}"
    for i in range(1, conf.workload_limit+1):
        outcome :Outcome = get_name (
            from_url=f"{base_url}{i}", #if (i % 2) != 0 else 'https://httpbin.org/status/504',
            entity_id = i,
            timeout=conf.timeout
        )
        if outcome.status == 'Success':
            v_names.append(f"#{outcome.entity_id} - {outcome.result}")
        #end if
    #end for
    return v_names

def main() -> None:
    ''' main '''
    conf = Conf (
        site_url = 'https://pokeapi.co',
        path_url= '/api/v2/pokemon/', # +ve integer path param is added to this path
        workload_limit =150,
        timeout = 1
        # timeout can be a Tuple as in (ConnectTimeout :float, readTimeout :float) both in seconds
    )
    time1 = time.time()
    names = get_names(conf=conf)
    time2 = time.time()
    print (
        f"Synchronous w/o Session Elapsed Time: {time2 - time1} seconds",
        f"for retrieval of {len(names)} names"
    )

if __name__ == "__main__":
    main()
