# pyredis-dump - A Redis Dump/Restore Tool

Inspired by [redis-dump-load](https://github.com/p/redis-dump-load)
but can handle binary blobs not just text.

Dumps Redis data sets into a format suitable for long-term storage
(currently Python Literals using [AST](https://docs.python.org/2/library/ast.html))
and loads data from such dump files back into Redis.

## Features

- Supports all Redis data types;
- Dumps TTL and expiration times;
- Can load TTL OR original expiration time for expiring keys;
- Dumps are human readable
- Dumps are line-aligned (can be streamed)
- Can be used as a module in a larger program or as a standalone utility

## Python 2/3 Compatability

Use python2 for restoring dumps taken using python2
Use python3 for restoring dumps taken using python3

## Basic usage

```
python3 pyredis-dump.py -h
python3 pyredis-dump.py dblist
python3 pyredis-dump.py dump -o outfile.py3redis
python3 pyredis-dump.py restore -i outfile.py3redis
```


