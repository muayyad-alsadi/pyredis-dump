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
- Dumps are lines
- 
- Can be used as a module in a larger program or as a standalone utility

## Basic usage

```
pyredis-dump.py -h
pyredis-dump.py dump -o outfile.pyredis
pyredis-dump.py restore -i outfile.pyredis
```

