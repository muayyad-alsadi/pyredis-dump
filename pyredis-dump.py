#! /usr/bin/env python

import time
import optparse
import ast
import re
from redis import StrictRedis as Redis

class RedisDump(Redis):
  def __init__(self, *a, **kw):
    Redis.__init__(self, *a, **kw)
    version = [int(part) for part in self.info()['redis_version'].split('.')]
    self._have_pttl = version >= [2, 6]
    self._types = set(['string', 'list', 'set', 'zset', 'hash'])

  def get_one(self, key):
    type = self.type(key)
    p = self.pipeline()
    p.watch(key)
    p.multi()
    p.type(key)
    if self._have_pttl:
      p.pttl(key)
    else:
      p.ttl(key)
    if type=='string': p.get(key)
    elif type=='list': p.lrange(key, 0, -1)
    elif type=='set':  p.smembers(key)
    elif type=='zset': p.zrange(key, 0, -1, False, True)
    elif type=='hash': p.hgetall(key)
    else: raise TypeError('Unknown type=%r' % type)
    type2, ttl, value = p.execute()
    if self._have_pttl and ttl>0:
      ttl = ttl / 1000.0
    if type!=type2: raise TypeError("Type changed")
    if ttl>0:
      expire_at = time.time() + ttl
    else: expire_at=-1
    return type, key, ttl, expire_at, value

  def pattern_iter(self, pattern="*"):
    for key in self.keys(pattern):
      yield self.get_one(key)
  
  def dump(self, outfile, pattern="*"):
    for type, key, ttl, expire_at, value in self.pattern_iter(pattern):
      line=repr((type, key, ttl, expire_at, value,))
      outfile.write(line+"\n")

  def set_one(self, p, use_ttl, key_type, key, ttl, expire_at, value):
    p.delete(key)
    if key_type=='string':
      p.set(key, value)
    elif key_type=='list':
      for element in value:
        p.rpush(key, element)
    elif key_type=='set':
      for element in value:
        p.sadd(key, element)
    elif key_type=='zset':
      for element, score in value:
        p.zadd(key, score, element)
    elif key_type=='hash':
      p.hmset(key, value)
    else: raise TypeError('Unknown type=%r' % type)
    if ttl<=0: return
    if use_ttl:
      if type(ttl) is int:
        p.expire(key, ttl)
      else: p.pexpire(key, int(ttl * 1000))
    else:
      if type(expire_at) is int:
        p.expireat(key, expire_at)
      else: p.pexpireat(key, int(expire_at * 1000))

  def restore(self, infile, use_ttl=False, bulk_size=1000):
    p = self.pipeline(transaction=False)
    dirty=False
    for i, line in enumerate(infile):
      line = line.strip()
      if not line: continue
      a=ast.literal_eval(line)
      if len(a)!=5: raise ValueError("expecting type, key, ttl, expire_at, value got %r" % a)
      type, key, ttl, expire_at, value = a
      self.set_one(p, use_ttl, type, key, ttl, expire_at, value)
      dirty=True
      if i % bulk_size == 0:
        dirty=False
        p.execute()
        p = self.pipeline(transaction=False)
    if dirty: p.execute()

def dump(filename, pattern="*", **kw):
  r=RedisDump(**kw)
  with open(filename, "w+") as outfile:
    r.dump(outfile, pattern)

def restore(filename, use_ttl=True, bulk_size=1000, **kw):
  r=RedisDump(**kw)
  with open(filename, "r+") as infile:
    r.restore(infile)

db_re=re.compile(r'db\d+')

def dblist(**kw):
  r=Redis(**kw)
  for i in sorted(filter( lambda k: db_re.match(k), r.info().keys() )):
    print(i.replace("db", ""))

def options2kw(options):
  kw={'db':options.db}
  if options.socket: kw['unix_socket_path']=options.socket
  else:
    kw['host']=options.host
    kw['port']=options.port
  if options.password: kw['password']=options.password
  return kw

def main():
  host = 'localhost'
  db = 0
  parser = optparse.OptionParser(usage="usage: %prog [options] dump|restore|dblist")
  parser.add_option('-H', '--host', help='connect to HOST (default localhost)', default='localhost')
  parser.add_option('-P', '--port', help='connect to PORT (default 6379)', default=6379, type="int")
  parser.add_option('-s', '--socket', help='connect to SOCKET')
  parser.add_option('-d', '--db', help='database', default=0, type="int")
  parser.add_option('-w', '--password', help='connect with PASSWORD')
  parser.add_option('-p', '--pattern', help='pattern', default='*')
  parser.add_option('-o', '--outfile', help='write to OUTFILE')
  parser.add_option('-i', '--infile', help='read from INFILE')
  # parser.add_option("-e", action="store_true", dest="use_expire_at", help="use expire_at when in restore mode")
  parser.add_option("-t", action="store_true", dest="use_ttl", help="use ttl when in restore mode")
  parser.add_option('-b', '--bulk', help='restore bulk size', default=1000, type="int")
  options, args = parser.parse_args()
  if len(args)!=1:
    parser.print_help()
    parser.error("wrong number of arguments")
    
  mode=args[0]
  kw = options2kw(options)
  if mode=='dump':
    if not options.outfile: parser.error("missing outfile, use '-o'")
    print("dumping to %r" % options.outfile)
    print("connecting to %r" % kw)
    dump(options.outfile, options.pattern, **kw)
  elif mode=='restore':
    if not options.infile: parser.error("missing infile, use '-i'")
    print("restore from %r" % options.infile)
    print("connecting to %r" % kw)
    restore(options.infile, use_ttl=options.use_ttl, bulk_size=options.bulk, **kw)
  elif mode=='dblist':
    dblist(**kw)
  else:
    parser.print_help()
    parser.error("unknown mode %r" % mode)

if __name__=='__main__':
  main()

