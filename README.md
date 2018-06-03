# N-Way Set Associative Cache

This cache uses n daemon worker threads to distribute the workload
of each job it is given and store up to n * lines items within a set
associative cache.

## Using the cache:

1) Import the package

```
from n_way_set_associative_cache.NWaySetAssociativeCache import NWaySetAssociativeCache
```

2) Create a new cache object

```
cache = NWaySetAssociativeCache(n, replacement, lines)
```

n = the number of sets (and the number of worker threads)

replacement = 'LRU', 'MRU', or a custom static replacement algorithm. The custom replacement algorithm will take in the cache class instance, as well as the set number to do the replacement on as parameters.

lines = the number of lines within a single set

3) When you attempt to get an item that does not exist within the cache,
a ValueError will be thrown. A typical use case is as follows:

```
try:
    data = cache.get(resource_key)
except ValueError:
    data = method_to_retrieve_from_backing_store(resource_key)
    cache.put(resource_key, data)
```

## To run the tests, run the following command in the main directory:

```
python3 NWaySetAssociativeCache.test.py
```