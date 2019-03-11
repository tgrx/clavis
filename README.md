# CLAVIS

## Description

Clavis is a Python library.
It provides an unusual way to use db transaction from SqlAlchemy as a context manager.
It also provides an easy way to postpone queries and execute them after commit/rollback.

## Shields

![](https://img.shields.io/pypi/implementation/clavis.svg?style=popout)  
![](https://img.shields.io/pypi/dm/clavis.svg?style=popout)  
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)  
[![coverage report](https://gitlab.com/tgrx/clavis/badges/master/coverage.svg)](https://gitlab.com/tgrx/clavis/commits/master)  
![](https://img.shields.io/pypi/pyversions/clavis.svg?style=popout)  
![](https://img.shields.io/pypi/l/clavis.svg?style=popout)  
![](https://img.shields.io/pypi/wheel/clavis.svg?style=popout)  
![](https://img.shields.io/pypi/status/clavis.svg?style=popout)  
![](https://img.shields.io/gitlab/pipeline/tgrx/clavis/master.svg?style=popout)  


## Notes

### Python

- 3.6
- 3.7

### Databases

- PostgreSQL
- MySQL

### Caveats

- Does not support nested transactions yet

## Examples

### Simple usage

```python
from clavis import Transaction

with Transaction() as txn:
    session = txn.session
    session.add("Object")
    # "COMMIT" is issued on the successful context exit

print("data committed")
```

### Calls to `commit`/`rollback` raise exceptions

#### Explicit COMMIT

```python
from clavis import Transaction

with Transaction() as txn:
    txn.session.add("Object")
    txn.commit()  # or txn.session.commit()
    print("never happens")
```

#### Explicit ROLLBACK

```python
from clavis import Transaction

with Transaction() as txn:
    txn.session.add("Object")
    txn.rollback()  # or txn.session.rollback()
    print("never happens")
```

#### Calls to `commit`/`rollback` within context

```python
from clavis import Transaction


def do(session, value):
    session.add(f"Object {value}")
    session.commit()  # XXX: intrinsic exception is raised here
    print("never happens")


with Transaction() as txn:
    do(txn.session, 1)  # intrinsic "Commit" exception is raised
    do(txn.session, 2)  # never reached
    print("never happens")  # never reached
```

### Exceptions are re-raised with ROLLBACK 

```python
from clavis import Transaction

try:
    with Transaction() as txn:
        txn.session.add("Object")
        x = 1 // 0
        print("never happens")
except ZeroDivisionError:
    print("transaction was rolled back")
```

### Configuring

Below different ways to configure database are described.
Note that these ways are processed with different priorities.
The configurations are applied in the order they are described here.
Hence, with both env and package configured, the database url will be used from the package level.
As well as in-place database url overrides ones from both package and env levels.

#### On environment level

```python
# bash: export DATABASE_URL="driver://user:pass@host:port/dbname"

from clavis import Transaction


with Transaction() as t:
    pass
```

#### On package level

```python
import clavis

clavis.configure("driver://user:pass@host:port/dbname")


# later in some other place ...


import clavis

with clavis.Transaction() as t:
    pass
```

#### Using factory

```python
import clavis

tf = clavis.TransactionFactory("driver://user:pass@host:port/dbname")

with tf.transaction() as t:
    pass
```

#### In-place configuration

```python
from clavis import Transaction

with Transaction("driver://user:pass@host:port/dbname") as t:
    pass
```
