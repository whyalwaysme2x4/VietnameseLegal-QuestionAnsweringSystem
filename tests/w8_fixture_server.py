"""Explicit fixture-only browser acceptance server; never start through Start-Demo."""
import json
import os
import sys
import tempfile
import time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
os.environ['HF_HUB_OFFLINE']='1'
os.environ['AWS_EC2_METADATA_DISABLED']='true'
from source.data.db.demo_history import HistoryStore
from w8_fixture import start,stop


def main():
    folder=ROOT/'runs/w8';folder.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        server,engine,old=start(HistoryStore(Path(tmp)/'browser-fixture.sqlite3'))
        (folder/'fixture-server.json').write_text(json.dumps({'url':'http://127.0.0.1:'+str(server.server_port),
            'pid':os.getpid(),'fixture_execution':True,'aws_calls':0}),encoding='utf-8')
        print('W8 browser fixture ready',flush=True)
        try:
            while True:time.sleep(.5)
        finally:stop(server,old)


if __name__=='__main__':main()
