''' Asynchronous Concurrent Exec with Throttling'''
import time
from collections import namedtuple
import asyncio
import aiohttp

Conf = namedtuple ('Conf', 'site_url, path_url, workload_limit, timeout, workers_count')
Outcome = namedtuple('Outcome', 'entity_id status result worker_id')

def outcome_sortkey (outcome :Outcome):
    ''' return sort key to use for sorting outcomes '''
    return outcome.entity_id

def show_outcome(outcome :Outcome ) -> None:
    ''' Show outcome '''
    print (
        f"Entity #{outcome.entity_id} - {outcome.status} - {outcome.result}"
        ,f"- Worker #{outcome.worker_id}"
    )

async def worker_task (
    worker_id :int
    ,workload_items :list[int]
    ,proc_outcomes :list[Outcome]
    ,session :aiohttp.ClientSession
    ,base_url :str
) -> None:
    ''' Worker Task '''
    while len(workload_items) != 0:
        entity_id = workload_items.pop(0)
        proc_outcomes.append (
            await get_entity (
                session = session
                ,from_url = f"{base_url}{entity_id}"
                #if (entity_id % 2) != 0 else 'https://httpbin.org/status/504'
                ,entity_id = entity_id
                ,worker_id = worker_id
            )
        )
    #end while

async def get_entity (
    session :aiohttp.ClientSession
    ,from_url :str
    ,entity_id :int
    ,worker_id :int
) -> Outcome:
    ''' Get entity  '''
    try:
        async with session.get(
            url = from_url
            ,allow_redirects = False
        ) as resp:
            resp_dict = await resp.json()
            outcome = Outcome (entity_id=entity_id, status = 'Success', result=resp_dict['name']
                ,worker_id=worker_id)
    except asyncio.TimeoutError as ex:
        outcome = Outcome (entity_id=entity_id, status = 'Timeout', result = str(type(ex))
            ,worker_id=worker_id)
    except aiohttp.ClientResponseError as ex:
        outcome = Outcome (
            entity_id=entity_id
            ,status=f"Response{'GatewayTimeout' if ex.status == 504 else 'Error'}"
            ,result=str(type(ex))
            ,worker_id=worker_id
        )
    except Exception as ex:
        outcome = Outcome (entity_id=entity_id, status = 'Exception', result = str(type(ex))
            ,worker_id=worker_id)
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
        l_outcomes :list[Outcome] = []
        tasks = []
        for i in range(1, conf.workers_count+1):
            # Below marks the coroutine as Ready for Running
            # If the coroutine can run, it starts running right away.
            # Since all instances of coroutine are allowed to run,
            # we have concurrent executions.
            task = asyncio.create_task (
                worker_task (
                    worker_id = i
                    ,workload_items = workload_items
                    ,proc_outcomes = l_outcomes
                    ,session = session
                    ,base_url = base_url
                )
                ,name = f"Worker #{i}"
            )
            tasks.append(task)
            task.add_done_callback(tasks.remove)
        #end for
        # Here, all tasks have been submitted for execution.
        # Await Gather below waits for completion of all tasks submitted,
        # and returns a list of the return value of each coroutine executed by the task,
        # in the same order as the tasks were submitted for execution.
        # In this particular case, the list returned shall be a list of None,
        # since each worker_task returns None.
        # Each worker_task shall collect into outcomes the return value of each get_entity
        # it calls. BUT outcomes shall not be sorted by entity_id.
        await asyncio.gather(*tasks) # we just wait and ignore what gather returns
        # Below, we sort outcomes by asc entity_id
        l_outcomes.sort(reverse=False, key=outcome_sortkey)
        return l_outcomes

def get_entities () -> list[Outcome]:
    ''' get entities '''
    conf = Conf (
        site_url = 'https://pokeapi.co'
        ,path_url= '/api/v2/pokemon/' # +ve integer path param is added to this path
        ,workload_limit = 900
        ,timeout = 2 # Timeout in seconds for connection + read
        ,workers_count = 50
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
    print (f"Asynchronous Concurrent Exec with Throttling Elapsed Time: {time2 - time1} seconds"
            ,f"for successful retrieval of {len(outcomes_success)} entities"
    )
