''' Synchronous Exec '''
import time
from collections import namedtuple
from requests.exceptions import HTTPError
from requests.exceptions import Timeout
import requests

Conf = namedtuple ('Conf', 'site_url, path_url, workload_limit, timeout')
Outcome = namedtuple('Outcome', 'entity_id status result')

def show_outcome(outcome :Outcome ) -> None:
    ''' Show outcome '''
    print (f"Entity #{outcome.entity_id} - {outcome.status} - {outcome.result}")

def get_entity (
    from_url :str
    ,entity_id :int
    ,timeout :float
) -> Outcome:
    ''' Get entity '''
    try:
        resp = requests.get(
            url = from_url
            ,timeout = timeout
            ,allow_redirects = False
        )
        resp.raise_for_status()
        resp_dict = resp.json()
        outcome = Outcome (entity_id=entity_id, status = 'Success', result=resp_dict['name'])
    except Timeout as ex:
        # Timeout will catch both ConnectTimeout and ReadTimeout
        outcome = Outcome (entity_id=entity_id, status = 'Timeout', result = str(type(ex)))
    except HTTPError as ex:
        outcome = Outcome (
            entity_id=entity_id
            ,status=f"Response{'GatewayTimeout' if ex.response.status_code == 504 else 'Error'}"
            ,result=str(type(ex))
        )
    except Exception as ex:
        outcome = Outcome (entity_id=entity_id, status = 'Exception', result = str(type(ex)))
    #end try - except
    show_outcome (outcome)
    return outcome

def get_entities () -> list[Outcome]:
    ''' Get entities '''
    conf = Conf (
        site_url = 'https://pokeapi.co'
        ,path_url= '/api/v2/pokemon/' # +ve integer path param is added to this path
        ,workload_limit = 50
        ,timeout = 1
        # timeout can be a Tuple as in (ConnectTimeout :float, readTimeout :float) both in seconds
    )
    base_url = f"{conf.site_url}{conf.path_url}"
    #workload_items is a list of entity_id (int) from 1 up to conf.workload_limit
    workload_items = list(range(1,conf.workload_limit+1))
    l_outcomes :list[Outcome] = []
    for entity_id in workload_items:
        l_outcomes.append (
            get_entity (
                from_url=f"{base_url}{entity_id}"
                #if (i % 2) != 0 else 'https://httpbin.org/status/504'
                ,entity_id=entity_id
                ,timeout=conf.timeout
            )
        )
    #end for
    return l_outcomes

if __name__ == "__main__":
    time1 = time.time()
    outcomes :list[Outcome] = get_entities()
    time2 = time.time()
    print ("All Get Entities completed")
    outcomes_success = [ outcome for outcome in outcomes if outcome.status=='Success']
    for outcome in outcomes_success:
        print (f"#{outcome.entity_id} - {outcome.result}")
    print (f"Synchronous Exec w/o Session Elapsed Time: {time2 - time1} seconds"
            ,f"for successful retrieval of {len(outcomes_success)} entities"
    )
