''' xxx '''

import time
import asyncio
import aiohttp

async def do_task(session :aiohttp.ClientSession, task_url: str) -> object:
    ''' xxx  '''
    try:
        async with session.get(url=task_url, allow_redirects=False) as resp:
            return await resp.json()
    except Exception as ex:
        return ex

async def do_job(site_url:str) -> None:
    ''' xxx  '''
    client_timeout = aiohttp.ClientTimeout(total=2)
    tcp_conn = aiohttp.TCPConnector(enable_cleanup_closed=True)
    async with aiohttp.ClientSession(base_url=site_url, \
    timeout=client_timeout, connector=tcp_conn) as session:
        # Prepare all tasks
        tasks = []
        for task_no in range(1, 151):
            path_url = f'/api/v2/pokemon/{task_no}' # if taskNo %2 == 0 else f'/xxx/{taskNo}'
            # task = asyncio.ensure_future(do_task(session, path_url))
            task = asyncio.create_task(do_task(session, path_url))
            tasks.append(task)
            task.add_done_callback(tasks.remove)
        # Task list prepared
        # Wait for all tasks to complete before returning results
        result_list = await asyncio.gather(*tasks)
    # ClientSession ends here
    # for i in range(len(result_list)):
    for i, result in enumerate(result_list):
        if not (isinstance(result, Exception)):
            print(f"#{i+1} - {result['name']}")
        elif (isinstance (result, asyncio.TimeoutError )):
            print(f"#{i+1} - TIMEOUT - {type(result)}")
        else:
            print(f"#{i+1} - ERROR - {type(result)} - {result.args}")
        #end if
    return

if (__name__ == "__main__"):
    SITE_URL = 'https://pokeapi.co'
    time1 = time.time()
    asyncio.run(do_job(SITE_URL))
    time2 = time.time()
    print (f"Concurrent Elapsed Time: {time2 - time1} seconds")
