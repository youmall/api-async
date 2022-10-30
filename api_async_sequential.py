''' xxx '''
import time
import asyncio
import aiohttp

async def main():
    ''' xxx '''
    async with aiohttp.ClientSession() as session:
        for number in range(1, 151):
            pokemon_url = f'https://pokeapi.co/api/v2/pokemon/{number}'
            async with session.get(pokemon_url) as resp:
                pokemon = await resp.json()
                print(f"#{number} - {pokemon['name']}")

time1 = time.time()
asyncio.run(main())
time2 = time.time()

print (f"Asynchronous Sequential Elapsed Time: {time2 - time1} seconds")
