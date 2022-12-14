''' Asynchronous Concurrent Exec '''
import time
from collections import namedtuple
import asyncio
import aiohttp

Conf = namedtuple ('Conf', 'site_url, path_url, workload_limit, timeout')
Outcome = namedtuple ('Outcome', 'entity_id status result')

def show_outcome(outcome :Outcome ) -> None:
    ''' Show outcome '''
    print (f"Entity #{outcome.entity_id} - {outcome.status} - {outcome.result}")

async def get_entity (
    session :aiohttp.ClientSession
    ,from_url :str
    ,entity_id :int
) -> Outcome:
    ''' Get entity  '''
    try:
        async with session.get(
            url = from_url
            ,allow_redirects = False
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

async def aget_entities(conf :Conf) -> list[Outcome]:
    ''' Async get entities '''
    base_url = f"{conf.site_url}{conf.path_url}"
    #workload_items is a list of entity_id (int) from 1 up to conf.workload_limit
    workload_items = list(range(1,conf.workload_limit+1))
    async with aiohttp.ClientSession (
        timeout=aiohttp.ClientTimeout(total=conf.timeout)
        ,connector=aiohttp.TCPConnector(enable_cleanup_closed=True)
        ,raise_for_status=True
    ) as session:
        tasks = []
        for entity_id in workload_items:
            # Below marks the coroutine as Ready for Running
            # If the coroutine can run, it starts running right away.
            # Since all instances of coroutine are allowed to run,
            # we have concurrent executions.
            task = asyncio.create_task (
                get_entity (
                    session=session
                    ,from_url=f"{base_url}{entity_id}"
                    #if (entity_id % 2) != 0 else 'https://httpbin.org/status/504')
                    ,entity_id=entity_id
                )
            )
            tasks.append(task)
        #end for
        # Here, all tasks have been submitted for execution.
        # Await Gather below waits for completion of all tasks submitted,
        # and returns a list of the return value of each coroutine executed by the task,
        # in the same order as the tasks were submitted for execution.
        # In this particular case, the list returned shall be outcomes returned
        # by get_entity, sorted by asc entity_id, since the tasks were submitted
        # in asc entity_id order.
        return await asyncio.gather(*tasks)

def get_entities () -> list[Outcome]:
    ''' get entities '''
    conf = Conf (
        site_url = 'https://pokeapi.co'
        ,path_url= '/api/v2/pokemon/' # +ve integer path param is added to this path
        ,workload_limit = 50
        ,timeout = 2 # Timeout in seconds for connection + read
    )
    return asyncio.run (aget_entities(conf))

if __name__ == "__main__":
    time1 = time.time()
    outcomes :list[Outcome] = get_entities()
    time2 = time.time()
    print ("All Get Entities completed")
    outcomes_success = [ outcome for outcome in outcomes if outcome.status=='Success']
    for os in outcomes_success:
        print (f"#{os.entity_id} - {os.result}")
    print (f"Asynchronous Concurrent Exec Elapsed Time: {time2 - time1} seconds"
            ,f"for successful retrieval of {len(outcomes_success)} entities"
    )
