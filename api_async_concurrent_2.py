''' xxx '''

import time
import functools
import asyncio
import aiohttp

async def do_task(task_id: str, session :aiohttp.ClientSession) -> object:
    ''' xxx  '''
    try:
        async with session.get(url=task_id, allow_redirects=False) as resp:
            return await resp.json()
    except Exception as ex:
        return ex

def task_completed (tasks:list[asyncio.Task], task:asyncio.Task):
    ''' xxx '''
    outcome = f"Task #{task.get_name()} completed with outcome = "
    task_result = task.result()
    if not (isinstance(task_result, Exception)):
        outcome += task_result.get('name')
    else:
        outcome += str(type(task_result))
    #end if
    tasks.remove(task)
    print(f"{outcome}. Count of Remaining tasks = {len(tasks)}")

async def do_job(proc_list:list[str], conf:dict[str,any]) -> None:
    ''' xxx  '''
    tcp_conn = aiohttp.TCPConnector(enable_cleanup_closed=True, limit=conf.get('workers_count'))
    client_timeout = aiohttp.ClientTimeout(total=conf.get('timeout'))
    async with aiohttp.ClientSession (
        base_url=conf.get('site_url'),
        timeout=client_timeout, connector=tcp_conn
    ) as session:
        # Prepare all tasks
        tasks = []
        for activity_no, activity in enumerate(proc_list):
            task = asyncio.create_task(
                do_task( task_id=activity, session=session),
                name=f"{activity_no+1:0>3}"
            )
            tasks.append(task)
            #task.add_done_callback(tasks.remove)
            task.add_done_callback(functools.partial(task_completed, tasks))
        # Task list prepared
        # Wait for all tasks to complete before returning results
        #result_list = await asyncio.gather(*tasks)
        while (len(tasks)!=0):
            await asyncio.sleep(0)
    # ClientSession ends here
    # for i in range(len(result_list)):
    for i, result in enumerate(result_list):
        if not (isinstance(result, Exception)):
            print(f"#{i+1:0>3} - {result['name']}")
        elif (isinstance (result, asyncio.TimeoutError )):
            print(f"#{i+1:0>3} - TIMEOUT - {type(result)}")
        else:
            print(f"#{i+1:0>3} - ERROR - {type(result)} - {result.args}")
        #end if
    # end for
    return

def build_proc_list(conf) -> list[str]:
    ''' xxx '''
    proc_list = []
    for i in range(1,conf.get('proc_items_count')+1):
        proc_list.append(f"{conf.get('path_url')}{i}")
    #end for
    return proc_list

CONF = {
    'site_url':'https://pokeapi.co',
    'path_url':'/api/v2/pokemon/',
    'proc_items_count':300 ,
    'workers_count':100 ,
    'timeout':2
}

if (__name__ == "__main__"):
    proc_list = build_proc_list(conf=CONF)
    time1 = time.time()
    asyncio.run(do_job(proc_list=proc_list, conf=CONF))
    time2 = time.time()
    print (f"Concurrent Elapsed Time: {time2 - time1} seconds")
#end if
