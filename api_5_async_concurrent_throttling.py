''' Asynchronous Concurrent '''
import time
from collections import namedtuple
import asyncio
import aiohttp

Outcome = namedtuple('Outcome', 'worker_num entity_id status result')
Conf = namedtuple ('Conf', 'site_url, path_url, workload_limit, timeout, workers_count')

def show_outcome(outcome :Outcome ) -> None:
    ''' Show outcome '''
    print (
        f"Worker #{outcome.worker_num} -",
        f"Entity #{outcome.entity_id} - {outcome.status} - {outcome.result}"
    )

async def run_worker (
    worker_num :int,
    workload_items :list[int],
    names: list[str],
    session :aiohttp.ClientSession,
    base_url :str
) -> None:
    ''' run task '''
    while len(workload_items) != 0:
        entity_id = workload_items.pop(0)
        outcome :Outcome = await get_name (
            worker_num = worker_num,
            session=session,
            from_url=f"{base_url}{entity_id}",
            #from_url=f"{base_url}{i}" if (i % 2) != 0 else 'https://httpbin.org/status/504',
            entity_id = entity_id
        )
        if outcome.status == 'Success':
            names.append(f"#{outcome.entity_id} - {outcome.result}")
        #end if
    #end while

async def get_name(
    worker_num :int,
    session :aiohttp.ClientSession,
    from_url :str,
    entity_id :int
) -> Outcome:
    ''' Get name  '''
    try:
        async with session.get(
            url = from_url,
            allow_redirects=False
        ) as resp:
            resp_dict = await resp.json()
            name = resp_dict['name']
            status = 'Success'
            result = name
    except asyncio.TimeoutError as ex:
        status = 'Timeout'
        result = str(type(ex))
    except aiohttp.ClientResponseError as ex:
        if ex.status == 504:
            status = 'ClientResponseError/GatewayTimeout'
        else:
            status = 'ClientResponseError'
        #end if
        result = str(type(ex))
    except Exception as ex:
        status = 'Exception'
        result = str(type(ex))
    #end try - except
    outcome = Outcome(worker_num=worker_num,entity_id=entity_id, status=status, result=result)
    show_outcome (outcome)
    return outcome

async def get_names(conf :Conf) -> list[str]:
    ''' Get names  '''
    v_names = []
    base_url = f"{conf.site_url}{conf.path_url}"
    workload_items = list(range(1,conf.workload_limit+1))
    async with aiohttp.ClientSession (
        timeout=aiohttp.ClientTimeout(total=conf.timeout),
        connector=aiohttp.TCPConnector(enable_cleanup_closed=True),
        raise_for_status=True
    ) as session:
        tasks = []
        for i in range(1, conf.workers_count+1):
            # Below marks the coroutine as Ready for Running
            task = asyncio.create_task (
                run_worker (
                    worker_num=i,
                    workload_items = workload_items,
                    names = v_names,
                    session = session,
                    base_url=base_url
                ),
                name=f"Worker #{i}"
            )
            tasks.append(task)
            task.add_done_callback(tasks.remove)
        # All tasks started
        # Wait for all tasks to complete before returning results
        _ = await asyncio.gather(*tasks)
    #end with aiohttp.ClientSession
    return v_names

async def main() -> None:
    ''' main '''
    conf = Conf (
        site_url = 'https://pokeapi.co',
        path_url= '/api/v2/pokemon/', # +ve integer path param is added to this path
        workload_limit =500,
        timeout = 2, # Timeout in seconds for connection + read
        workers_count = 100
    )
    time1 = time.time()
    names = await get_names(conf=conf)
    time2 = time.time()
    print (f"Asynchronous Concurrent with Throttling Elapsed Time: {time2 - time1} seconds",
            f"for retrieval of {len(names)} names"
    )
    return

if __name__ == "__main__":
    asyncio.run(main())
