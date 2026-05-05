"""Mask generators for the four IMVC evaluation protocols (Table 1).

Each generator returns a bool ndarray M of shape (n, V) where M[i, v] = True
means sample i has view v observed.
"""
import numpy as np


PROTOCOLS = ("P1", "P2", "P3", "P4")


def generate_mask(n, V, r, protocol, rng=None):
    """Sample a mask from one of the four built-in protocols.

    Args:
        n: number of samples.
        V: number of views (>= 2).
        r: nominal missing rate in [0, 1].
        protocol: one of "P1", "P2", "P3", "P4".
        rng: numpy Generator. Defaults to a fresh default_rng().

    Returns:
        bool ndarray of shape (n, V).
    """
    if V < 2:
        raise ValueError(f"V must be >= 2, got {V}")
    if not 0.0 <= r <= 1.0:
        raise ValueError(f"r must be in [0, 1], got {r}")
    if rng is None:
        rng = np.random.default_rng()
    if r == 0.0:
        return np.ones((n, V), dtype=bool)

    proto = protocol.upper()
    if proto == "P1":
        return _p1(n, V, r, rng)
    if proto == "P2":
        return _p2(n, V, r, rng)
    if proto == "P3":
        return _p3(n, V, r, rng)
    if proto == "P4":
        return _p4(n, V, r, rng)
    raise ValueError(f"Unknown protocol {protocol!r}, expected one of {PROTOCOLS}")


def _p1(n, V, r, rng):
    """P1: pick round(n*r) samples, delete one random view from each."""
    mask = np.ones((n, V), dtype=bool)
    m = int(round(n * r))
    if m == 0:
        return mask
    selected = rng.choice(n, size=m, replace=False)
    deleted = rng.integers(0, V, size=m)
    mask[selected, deleted] = False
    return mask


def _p2(n, V, r, rng):
    """P2: each unprotected cell missing iid with prob r/(V-1); protected cell forced observed."""
    q = r / (V - 1)
    mask = rng.random((n, V)) >= q
    protected = rng.integers(0, V, size=n)
    mask[np.arange(n), protected] = True
    return mask


def _p3(n, V, r, rng):
    """P3: each cell missing iid with prob r; if a sample loses all V, restore one at random."""
    mask = rng.random((n, V)) >= r
    all_missing = np.where(mask.sum(axis=1) == 0)[0]
    if len(all_missing) > 0:
        keep = rng.integers(0, V, size=len(all_missing))
        mask[all_missing, keep] = True
    return mask


def _p4(n, V, r, rng):
    """P4: delete exactly round(n*V*r) cells uniformly from the n*(V-1) unprotected positions."""
    total_missing = int(round(n * V * r))
    max_missing = n * (V - 1)
    total_missing = min(total_missing, max_missing)
    if total_missing == 0:
        return np.ones((n, V), dtype=bool)

    protected = rng.integers(0, V, size=n)
    sample_idx = np.repeat(np.arange(n), V)
    view_idx = np.tile(np.arange(V), n)
    unprotected = view_idx != np.repeat(protected, V)
    cand_samples = sample_idx[unprotected]
    cand_views = view_idx[unprotected]

    perm = rng.permutation(len(cand_samples))[:total_missing]
    mask = np.ones((n, V), dtype=bool)
    mask[cand_samples[perm], cand_views[perm]] = False
    return mask
