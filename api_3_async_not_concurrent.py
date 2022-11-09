''' Asynchronous API Calls with 1 coroutine '''
import time
from collections import namedtuple
import asyncio
import aiohttp

Outcome = namedtuple('Outcome', 'entity_id status result')
Conf = namedtuple ('Conf', 'site_url, path_url, workload_limit, timeout')

def show_outcome(outcome :Outcome ) -> None:
    ''' Show outcome '''
    print (f"#{outcome.entity_id} - {outcome.status} - {outcome.result}")

async def get_name (
    session :aiohttp.ClientSession,
    from_url :str,
    entity_id :int
) -> Outcome:
    ''' Get name '''
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
    outcome = Outcome(entity_id=entity_id, status=status, result=result)
    show_outcome (outcome)
    return outcome

async def get_names (conf :Conf) -> list[str]:
    '''  Get names '''
    v_names = []
    base_url = f"{conf.site_url}{conf.path_url}"
    async with aiohttp.ClientSession (
        timeout=aiohttp.ClientTimeout(total=conf.timeout),
        connector=aiohttp.TCPConnector(enable_cleanup_closed=True),
        raise_for_status=True
    ) as session:
        for entity_id in range(1, conf.workload_limit+1):
            outcome :Outcome = await get_name (
                session=session,
                from_url=f"{base_url}{entity_id}",
                #from_url=f"{base_url}{i}" if (i % 2) != 0 else 'https://httpbin.org/status/504',
                entity_id = entity_id
            )
            if outcome.status == 'Success':
                v_names.append(f"#{outcome.entity_id} - {outcome.result}")
            #end if
        #end for
    #end with aiohttp.ClientSession
    return v_names

async def main() -> None:
    ''' main '''
    conf = Conf (
        site_url = 'https://pokeapi.co',
        path_url= '/api/v2/pokemon/', # +ve integer path param is added to this path
        workload_limit =150,
        timeout = 1 # Timeout in seconds for connection + read
    )
    time1 = time.time()
    names = await get_names(conf=conf)
    time2 = time.time()
    print (
        f"Asynchronous Single Coroutine Elapsed Time: {time2 - time1} seconds",
        f"for retrieval of {len(names)} names"
    )

if __name__ == "__main__":
    asyncio.run(main())
