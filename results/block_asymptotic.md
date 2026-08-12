# Fixed-block exponential-loss data

Every value is an exact power of a one-block Ehrhart ratio; literal reduced fractions are in the CSV. For the linear regime `t=n` and erosion `s=2`, the theorem predicts the family-independent limit `exp(-2)=0.135335283237...`.

| family | b | n | regime | t | exact expression | A |
|---|---:|---:|---|---:|---|---:|
| cross | 4 | 16 | fixed t=32 | 32 | `(579081/746241)^4` | 0.362610885407 |
| cross | 4 | 16 | linear t=n | 16 | `(29961/50049)^4` | 0.128423233421 |
| cross | 4 | 32 | fixed t=32 | 32 | `(579081/746241)^8` | 0.131486654216 |
| cross | 4 | 32 | linear t=n | 32 | `(579081/746241)^8` | 0.131486654216 |
| cross | 4 | 64 | fixed t=32 | 32 | `(579081/746241)^16` | 0.017288740237 |
| cross | 4 | 64 | linear t=n | 64 | `(10181641/11548161)^16` | 0.133315055828 |
| cross | 4 | 128 | fixed t=32 | 32 | `(579081/746241)^32` | 0.000298900539 |
| cross | 4 | 128 | linear t=n | 128 | `(170752009/181808129)^32` | 0.134301476830 |
| cross | 4 | 256 | fixed t=32 | 32 | `(579081/746241)^64` | 0.000000089342 |
| cross | 4 | 256 | linear t=n | 256 | `(2796941321/2885900289)^64` | 0.134812492854 |
| hexagon | 2 | 16 | fixed t=32 | 32 | `(2791/3169)^8` | 0.361993505025 |
| hexagon | 2 | 16 | linear t=n | 16 | `(631/817)^8` | 0.126607205102 |
| hexagon | 2 | 32 | fixed t=32 | 32 | `(2791/3169)^16` | 0.131039297680 |
| hexagon | 2 | 32 | linear t=n | 32 | `(2791/3169)^16` | 0.131039297680 |
| hexagon | 2 | 64 | fixed t=32 | 32 | `(2791/3169)^32` | 0.017171297537 |
| hexagon | 2 | 64 | linear t=n | 64 | `(11719/12481)^32` | 0.133204063696 |
| hexagon | 2 | 128 | fixed t=32 | 32 | `(2791/3169)^64` | 0.000294853459 |
| hexagon | 2 | 128 | linear t=n | 128 | `(48007/49537)^64` | 0.134273835520 |
| hexagon | 2 | 256 | fixed t=32 | 32 | `(2791/3169)^128` | 0.000000086939 |
| hexagon | 2 | 256 | linear t=n | 256 | `(194311/197377)^128` | 0.134805595919 |
