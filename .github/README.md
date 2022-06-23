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
- SSL support
- Can load options from a INI configuration file
- Can be used as a module in a larger program or as a standalone utility
- Compatible with Docker

## Python 2/3 Compatability

Use python2 for restoring dumps taken using python2
Use python3 for restoring dumps taken using python3

## Basic usage

```bash
# From the command-line
$ python3 pyredis-dump.py -h
$ python3 pyredis-dump.py dblist
$ python3 pyredis-dump.py dump -o dump.outfile
$ python3 pyredis-dump.py restore -i dump.outfile
$ python3 pyredis-dump.py dblist --ssl -H my.host -w SECRET

# Using a configuration file
$ python3 pyredis-dump.py dblist -c config.ini
$ python3 pyredis-dump.py dump -c config.ini
$ python3 pyredis-dump.py restore -c config.ini
```

## Docker usage

```bash
# Run with arguments
$ docker run --rm -it --name redis-dump ghcr.io/younited/pyredis-dump dblist -H remote.host -w SECRET
$ docker run --rm -it --name redis-dump ghcr.io/younited/pyredis-dump dump -H remote.host -w SECRET

# Run from a configuration file
$ docker run --rm -it \
  -v $(pwd)/config.ini:/app/config.ini \
  --name redis-dump ghcr.io/younited/pyredis-dump dblist -c config.ini

# Dump to host
$ docker run --rm -it \
  -v $(pwd)/config.ini:/app/config.ini \
  --name redis-dump ghcr.io/younited/pyredis-dump dump -c config.ini > /path/to/dump.outfile

# Dump to a volume
$ docker volume create myvol
$ docker run --rm -it \
  -v $(pwd)/config.ini:/app/config.ini \
  -v myvol:/data \
  --name redis-dump ghcr.io/younited/pyredis-dump dump -c config.ini -o /data/dump.outfile

# Restore from a volume
$ docker run --rm -it \
  -v $(pwd)/config.ini:/app/config.ini \
  -v myvol:/data \
  --name redis-dump ghcr.io/younited/pyredis-dump restore -c config.ini -i /data/dump.outfile
```
