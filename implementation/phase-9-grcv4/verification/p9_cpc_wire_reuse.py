"""Bounded exact-content JCS reuse for single-thread research workers only.

V4 still detaches and validates every caller value before this hook. A fast,
lossless JSON representation keys already checked primitive trees; the cached
value is immutable RFC 8785 bytes produced by the original encoder. There is
no object-identity key, numerical substitution, disk cache, or failed admission
memo. Nothing survives the context. Small trees bypass the memo.
"""
from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
import json
from unittest.mock import patch
from pygrc.models import grc_v4_codec as codec

MIN_BYTES=64*1024
MAX_BYTES=8*1024*1024
TOTAL_BYTES=64*1024*1024
MAX_ENTRIES=16
_ACTIVE=ContextVar('cpc_research_wire_memo',default=None)


@contextmanager
def wire_reuse():
    active=_ACTIVE.get()
    if active is not None:
        yield active
        return
    dependency=codec._dependency
    original=dependency('rfc8785')
    entries=OrderedDict()
    stats=dict(requests=0,hits=0,evictions=0,retained_bytes=0,max_payload_bytes=0,
        max_entries=MAX_ENTRIES,total_byte_budget=TOTAL_BYTES,failed_results_cached=False)
    def dumps(data):
        # Both codec call sites supply detached, I-JSON-checked primitive trees.
        # JSON's binary64 roundtrip representation is injective on this domain;
        # preserving integer/float spellings causes only conservative misses.
        key=json.dumps(data,ensure_ascii=True,allow_nan=False,sort_keys=True,separators=(',',':')).encode('ascii')
        size=len(key);stats['requests']+=1;stats['max_payload_bytes']=max(stats['max_payload_bytes'],size)
        if not MIN_BYTES<=size<=MAX_BYTES:return original.dumps(data)
        if key in entries:
            result=entries.pop(key);entries[key]=result;stats['hits']+=1
            return result
        result=original.dumps(data)
        cost=size+len(result)
        if cost>TOTAL_BYTES:return result
        while entries and (len(entries)>=MAX_ENTRIES or stats['retained_bytes']+cost>TOTAL_BYTES):
            old,value=entries.popitem(last=False);stats['retained_bytes']-=len(old)+len(value);stats['evictions']+=1
        entries[key]=result;stats['retained_bytes']+=cost
        return result
    class Encoder:
        def __getattr__(self,name):return dumps if name=='dumps' else getattr(original,name)
    proxy=Encoder()
    def selected(name):return proxy if name=='rfc8785' else dependency(name)
    token=_ACTIVE.set(stats)
    try:
        with patch.object(codec,'_dependency',selected):yield stats
    finally:
        entries.clear();stats['retained_bytes']=0;_ACTIVE.reset(token)
