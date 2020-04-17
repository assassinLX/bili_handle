import logging
import subprocess
# to install run `pip install futures` on Python <3.2
from concurrent.futures import ThreadPoolExecutor as Pool

info = logging.getLogger(__name__).info

def callback(future):
    if future.exception() is not None:
        info("got exception: %s" % future.exception())
    else:
        info("process returned %d" % future.result())

def main():
    logging.basicConfig(
        level=logging.INFO,
        format=("%(relativeCreated)04d %(process)05d %(threadName)-10s "
                "%(levelname)-5s %(msg)s"))

    # wait for the process completion asynchronously
    info("begin waiting")
    pool = Pool(max_workers=1)
    f = pool.submit(subprocess.call, "sleep 2; echo done", shell=True)
    f.add_done_callback(callback)
    pool.shutdown(wait=False) # no .submit() calls after that point
    info("continue waiting asynchronously")

if __name__=="__main__":
    main()