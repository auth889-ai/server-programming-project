import redis

r = redis.Redis(host='localhost', port=6380, db=0)
r.set('foo', 'bar')
print(r.get('foo'))   # Should print b'bar'