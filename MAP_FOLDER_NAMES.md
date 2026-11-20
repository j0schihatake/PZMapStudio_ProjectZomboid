# ASCII map folder names

Project Zomboid's map spawn list is unreliable with non-ASCII map folder
names. The compiled folders are therefore ASCII:

```text
Isilkul, Omsk Oblast
Solntsevka_Vodnoye
Omsk
Krasnodar
Novosibirsk
Moscow
Trumbull_Valley
```

`map.info` keeps the Russian display titles. `SpawnPoints()` files are
unchanged.

Existing old saves and old copies with Cyrillic folder names must not be
reused; copy the new build and create a new save.
