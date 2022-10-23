import time
import asyncio
import aiohttp

start_time = time.time()

async def get_pokemon(session, url, number):
    """ xxx  """
    try:
        get_url = f'{url}/{number}' # if (number % 2) == 0 else ""
        async with session.get(get_url) as resp:
            pokemon = await resp.json()
            return f"#{number} - SUCCESS - {pokemon['name']}"
    except asyncio.TimeoutError as ex:
        return f"#{number} - TIMEOUT - {type(ex)}"
    except Exception as ex:
        return f"#{number} - ERROR - {type(ex)} - {ex.args}"

async def main():
    """ xxxx """
    url = 'https://pokeapi.co/api/v2/pokemon'

    client_timeout = aiohttp.ClientTimeout(total=0.5)
    async with aiohttp.ClientSession(timeout=client_timeout) as session:

        tasks = []
        for number in range(1, 151):
            task = asyncio.ensure_future(get_pokemon(session, url, number))
            task.add_done_callback(tasks.remove)
            tasks.append(task)

        original_pokemon = await asyncio.gather(*tasks)
        for pokemon in original_pokemon:
            print(pokemon)

asyncio.run(main())
print(f"--- {time.time() - start_time} seconds ---")
