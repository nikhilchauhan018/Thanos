import asyncio
import multiprocessing
import subprocess

# To run Jarvis
def startJarvis():
        # Code for process 1
        print("Process 1 is running.")
        from main import start
        start()

# To run hotword
def listenHotword():
    # Code for process 2
    print("Process 2 is running.")
    from engine.features import hotword
    hotword()

async def main():
    # Start both processes
    loop = asyncio.get_event_loop()
    p1 = loop.run_in_executor(None, startJarvis)
    p2 = loop.run_in_executor(None, listenHotword)
    await asyncio.gather(p1, p2)

if __name__ == '__main__':
    asyncio.run(main())
    print("system stop")