# imvc-audit

Audit toolkit for incomplete multi-view clustering (IMVC) evaluation protocols. Surfaces two hidden statistics that current IMVC papers don't report:

- **r̂** (effective cell missing rate): the actual fraction of missing entries in the mask matrix `M`.
- **p_c** (complete-sample proportion): the fraction of samples that retain all V views.

Different protocols realizing the same nominal missing rate `r` can produce r̂ and p_c values that differ by ~50×, and reconstruction-based IMVC methods collapse to near-random accuracy when p_c falls below 1%.

This package computes r̂ and p_c either in closed form (for the four protocols catalogued below) or empirically from any user-supplied mask matrix.

## Install

```bash
pip install git+<repo-url>
```

Or, if you cloned the repo:

```bash
pip install -e .
```

Only depends on `numpy`.

## CLI

Print closed-form r̂ and p_c at `V=6` for the four built-in protocols:

```
$ imvc-audit --V 6 --rates 0.1,0.3,0.5,0.7
V=6
           r=0.1            r=0.3            r=0.5            r=0.7
Proto    r_hat      p_c   r_hat      p_c   r_hat      p_c   r_hat      p_c
P1        0.017    0.900   0.050    0.700   0.083    0.500   0.117    0.300
P2        0.017    0.904   0.050    0.737   0.083    0.590   0.117    0.470
P3        0.100    0.531   0.300    0.118   0.497    0.016   0.680    0.001
P4        0.100    0.528   0.300    0.107   0.500    0.010   0.700    0.000
```

Note how P1 and P4 at the nominal rate `r = 0.5` produce p_c values 50× apart (0.500 vs 0.010), even though they share the same `r`. Both rows summarize the same data but expose very different difficulty regimes.

## Python API

```python
import numpy as np
from imvc_audit import expected_stats, empirical_stats, generate_mask

# 1. Closed-form (Table 1) for built-in protocols P1-P4
expected_stats(V=6, r=0.5, protocol="P4")
# -> {'r_hat': 0.5, 'p_c': 0.01024}

# 2. Direct computation on any mask matrix (your own protocol)
def my_protocol(n, V, r, rng):
    """Example: view 0 always observed, others iid missing with rate r."""
    M = rng.random((n, V)) >= r
    M[:, 0] = True
    return M

mask = my_protocol(5000, 6, 0.5, np.random.default_rng(0))
empirical_stats(mask)
# -> {'r_hat': 0.4168, 'p_c': 0.0299, 'avg_views': 3.499, 'min_views_per_sample': 1}

# 3. Sample masks from built-in protocols
mask = generate_mask(n=5000, V=6, r=0.5, protocol="P3",
                     rng=np.random.default_rng(0))
```

## The four protocols

| Protocol | Mechanism                              | r̂ (closed-form)     | p_c (closed-form)            |
|----------|----------------------------------------|----------------------|------------------------------|
| P1       | Sample-level deletion (protected)      | r/V                  | 1 − r                        |
| P2       | Cell-level Bernoulli (protected)       | r/V                  | (1 − r/(V−1))^(V−1)          |
| P3       | Per-view independent (one-hot)         | r − r^V/V            | (1 − r)^V                    |
| P4       | Cell-level uniform deletion            | min(r, (V−1)/V)      | max(0, (1 − Vr/(V−1)))^(V−1) |

`generate_mask(n, V, r, "P1"|"P2"|"P3"|"P4")` samples from each. For any other protocol, build the mask yourself and call `empirical_stats(mask)`.

## Tests

Closed-form vs Monte Carlo agreement at `n=10000`:

```bash
python -m unittest discover tests
```

## License

MIT.
