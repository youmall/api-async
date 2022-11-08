''' Asynchronous API Calls with 1 coroutine '''
import time
import asyncio
import aiohttp

conf = {
    'site_url':'https://pokeapi.co',
    'path_url':'/api/v2/pokemon/', # +ve integer path param is added to this path
    'workload_limit': 150,
    'timeout': 2,  # Timeout in seconds for connection + read
}

async def get_names() -> list[str]:
    '''  Get names '''
    v_names = []
    async with aiohttp.ClientSession (
        base_url=conf.get('site_url'),
        timeout=aiohttp.ClientTimeout(total=conf.get('timeout')),
        connector=aiohttp.TCPConnector(enable_cleanup_closed=True),
        raise_for_status=True
    ) as session:
        for i in range(1, conf.get('workload_limit')+1):
            try:
                async with session.get(
                    url = f"{conf.get('path_url')}{i}",
                    # url = f"{conf.get('site_url')}{conf.get('path_url')}{i}" \
                    # if (i % 2) != 0 else 'https://httpbin.org/status/404',
                    allow_redirects=False
                ) as resp:
                    resp_dict = await resp.json()
                    name = resp_dict['name']
                    v_names.append(name)
                    print (f"#{i} - {name}")
            except asyncio.TimeoutError as ex:
                print(f"#{i} - Timeout {type(ex)}")
            except aiohttp.ClientResponseError as ex:
                if ex.status == 504:
                    print(f"#{i} - GatewayTimeout {type(ex)}")
                else:
                    print(f"#{i} - ClientResponseError {type(ex)}")
                #end if
            except Exception as ex:
                print(f"#{i} - Exception {type(ex)}")
        # end for
    # end aiohttp.ClientSession
    return v_names

async def main():
    ''' main '''
    time1 = time.time()
    names = await get_names()
    time2 = time.time()
    print (f"Asynchronous Single Coroutine Elapsed Time: {time2 - time1} seconds",
            f"for retrieval of {len(names)} names"
    )
    return

if __name__ == "__main__":
    asyncio.run(main())
