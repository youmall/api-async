''' Asynchronous Sequential Exec '''
import time
from collections import namedtuple
import asyncio
import aiohttp

Conf = namedtuple ('Conf', 'site_url, path_url, workload_limit, timeout')
Outcome = namedtuple('Outcome', 'entity_id status result')

def show_outcome(outcome :Outcome ) -> None:
    ''' Show outcome '''
    print (f"Entity #{outcome.entity_id} - {outcome.status} - {outcome.result}")

async def get_entity (
    session :aiohttp.ClientSession
    ,from_url :str
    ,entity_id :int
) -> Outcome:
    ''' Get entity '''
    try:
        async with session.get(
            url = from_url
            ,allow_redirects=False
        ) as resp:
            resp_dict = await resp.json()
            outcome = Outcome (entity_id=entity_id, status = 'Success', result=resp_dict['name'])
    except asyncio.TimeoutError as ex:
        outcome = Outcome (entity_id=entity_id, status = 'Timeout', result = str(type(ex)))
    except aiohttp.ClientResponseError as ex:
        outcome = Outcome (
            entity_id=entity_id
            ,status=f"Response{'GatewayTimeout' if ex.status == 504 else 'Error'}"
            ,result=str(type(ex))
        )
    except Exception as ex:
        outcome = Outcome (entity_id=entity_id, status = 'Exception', result = str(type(ex)))
    #end try - except
    show_outcome (outcome)
    return outcome

async def aget_entities (conf :Conf) -> list[Outcome]:
    '''  Async Get entities '''
    base_url = f"{conf.site_url}{conf.path_url}"
    #workload_items is a list of entity_id (int) from 1 up to conf.workload_limit
    workload_items = list(range(1,conf.workload_limit+1))
    async with aiohttp.ClientSession (
        timeout=aiohttp.ClientTimeout(total=conf.timeout)
        ,connector=aiohttp.TCPConnector(enable_cleanup_closed=True)
        ,raise_for_status=True
    ) as session:
        l_outcomes :list[Outcome] = []
        for entity_id in workload_items:
            #Because of the await below, the get_entity coroutine must complete its execution
            #before the next iteration.
            #Hence, executions of get_entity are sequential.
            l_outcomes.append (
                await get_entity (
                    session=session
                    ,from_url=f"{base_url}{entity_id}"
                    #if (entity_id % 2) != 0 else 'https://httpbin.org/status/504'
                    ,entity_id=entity_id
                )
            )
        #end for
        return l_outcomes

def get_entities () -> list[Outcome]:
    ''' get entities '''
    conf = Conf (
        site_url = 'https://pokeapi.co'
        ,path_url= '/api/v2/pokemon/' # +ve integer path param is added to this path
        ,workload_limit = 50
        ,timeout = 1 # Timeout in seconds for connection + read
    )
    return asyncio.run (aget_entities(conf))

if __name__ == "__main__":
    time1 = time.time()
    outcomes :list[Outcome] = get_entities()
    time2 = time.time()
    print ("All Get Entities completed")
    outcomes_success = [ outcome for outcome in outcomes if outcome.status=='Success']
    _ = [print (f"#{outcome.entity_id} - {outcome.result}") for outcome in outcomes_success]
    print (f"Asynchronous Sequential Exec Elapsed Time: {time2 - time1} seconds"
            ,f"for successful retrieval of {len(outcomes_success)} entities"
    )
