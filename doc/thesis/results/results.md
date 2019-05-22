Intel Core i7-4790k CPU @ 4.0 GHz with 32 Gb

### Quandenser-pipeline v0.071

**Cyano:** 1h50m (non-parallel, local), 1h12m (full parallel, local), 3h35m (full parallel, cluster), 


6*8 + 2*11 (p1), 10 (p2), 4+3+3+3+3+8+7+8+2+3+7+5+6+7+6+5+2+4 (p3) 4+5+5+8 (rest) = 255 m wait time


q < 0.05
1vs2: 2
1vs3: 8
1vs4: 4
1vs5: 1
2vs3: 4
2vs4: 4
2vs5: 0
3vs4: 0
3vs5: 1
4vs5: 0
Total: 24 diff, 10 unique

**Ralstonia:** 3h21m (non-parallel, local), 3h23m (full parallel, local), 4h30m (partial parallel, cluster)

q < 0.05
1vs2: 35
1vs3: 127
1vs4: 200
1vs5: 219
2vs3: 19
2vs4: 64
2vs5: 74
3vs4: 10
3vs5: 11
4vs5: 1
Total: 760 diff, 267 unique


### Custom OpenMS pipeline

**Cyano:** 1h16m

**Ralstonia:** 3h52min


### MaxQuant 1.6.3.3 (Using mono)

**Cyano:** 2h41m

**Ralstonia:** 8h11m
