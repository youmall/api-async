''' Asynchronous Concurrent '''
import time
import asyncio
import aiohttp

conf = {
    'site_url':'https://pokeapi.co',
    'path_url':'/api/v2/pokemon/', # +ve integer path param is added to this path
    'workload_limit': 150,
    'timeout': 1,  # Timeout in seconds for connection + read
}

async def get_name(session :aiohttp.ClientSession, i :int ) -> object:
    ''' Get name  '''
    try:
        async with session.get(
            url = f"{conf.get('path_url')}{i}",
            allow_redirects=False
        ) as resp:
            resp_dict = await resp.json()
            name = resp_dict['name']
            print (f"Task #{i} completed. {name}")
            return name
    except asyncio.TimeoutError as ex:
        print(f"Task #{i} completed. Timeout {type(ex)}")
        return ex
    except aiohttp.ClientResponseError as ex:
        if ex.status == 504:
            print(f"Task #{i} completed. GatewayTimeout {type(ex)}")
        else:
            print(f"Task #{i} completed. ClientResponseError {type(ex)}")
        #end if
        return ex
    except Exception as ex:
        print(f"Task #{i} completed. Exception {type(ex)}")
        return ex

async def get_names() -> list[str]:
    ''' Get names  '''
    v_names = []
    async with aiohttp.ClientSession (
        base_url=conf.get('site_url'),
        timeout=aiohttp.ClientTimeout(total=conf.get('timeout')),
        connector=aiohttp.TCPConnector(enable_cleanup_closed=True),
        raise_for_status=True
    ) as session:
        tasks = []
        for i in range(1, conf.get('workload_limit')+1):
            # Below marks the coroutine as Ready for Running
            task = asyncio.create_task(get_name(session, i))
            tasks.append(task)
            task.add_done_callback(tasks.remove)
        # All tasks started
        # Wait for all tasks to complete before returning results
        results = await asyncio.gather(*tasks)
    # ClientSession ends here
    for i, result in enumerate(results, start=1):
        if not isinstance(result, Exception):
            v_names.append(result) # result shall contain name
            print(f"#{i} - {result}")
        else:
            print(f"#{i} - Exception {type(result)}")
        #end if
    return v_names

async def main():
    ''' main '''
    time1 = time.time()
    names = await get_names()
    time2 = time.time()
    print (f"Asynchronous Concurrent Elapsed Time: {time2 - time1} seconds",
            f"for retrieval of {len(names)} names"
    )
    return

if __name__ == "__main__":
    asyncio.run(main())
