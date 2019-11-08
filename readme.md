## LMDB notes

LMDB is a useful tool to  accelerating dataloading in NFS computing clusters, especially for small files io.

According to testing, using lmdb can accelerate data loading for 15 times.

### code usage
```python gen_lmdb.py```

### resources
1. https://lmdb.readthedocs.io/en/release/
2. https://zhuanlan.zhihu.com/p/70359311