"""r_hat and p_c on mask matrices.

- expected_stats(V, r, protocol): closed-form n -> infinity limits (Table 1)
  for the four built-in protocols.
- empirical_stats(M): Eqs (1, 2) applied to a given mask matrix; works for
  any user-supplied protocol.
"""
import numpy as np


def expected_stats(V, r, protocol):
    """Closed-form r_hat and p_c (Table 1) for built-in protocols.

    Args:
        V: number of views (>= 2).
        r: nominal missing rate in [0, 1].
        protocol: one of "P1", "P2", "P3", "P4".

    Returns:
        {"r_hat": float, "p_c": float}
    """
    if V < 2:
        raise ValueError(f"V must be >= 2, got {V}")
    if not 0.0 <= r <= 1.0:
        raise ValueError(f"r must be in [0, 1], got {r}")

    proto = protocol.upper()
    if proto == "P1":
        return {"r_hat": r / V, "p_c": 1.0 - r}
    if proto == "P2":
        return {"r_hat": r / V, "p_c": (1.0 - r / (V - 1)) ** (V - 1)}
    if proto == "P3":
        return {"r_hat": r - (r ** V) / V, "p_c": (1.0 - r) ** V}
    if proto == "P4":
        r_hat = min(r, (V - 1) / V)
        inner = 1.0 - V * r / (V - 1)
        p_c = inner ** (V - 1) if inner > 0 else 0.0
        return {"r_hat": r_hat, "p_c": p_c}
    raise ValueError(f"Unknown protocol {protocol!r}, expected one of P1, P2, P3, P4")


def empirical_stats(mask):
    """Eqs (1, 2) on a given mask matrix. Works for any protocol.

    Args:
        mask: bool ndarray of shape (n, V); True = observed.

    Returns:
        {"r_hat", "p_c", "avg_views", "min_views_per_sample"}
    """
    M = np.asarray(mask, dtype=bool)
    if M.ndim != 2:
        raise ValueError(f"mask must be 2D, got shape {M.shape}")
    views_per_sample = M.sum(axis=1)
    return {
        "r_hat": float(1.0 - M.mean()),
        "p_c": float((views_per_sample == M.shape[1]).mean()),
        "avg_views": float(views_per_sample.mean()),
        "min_views_per_sample": int(views_per_sample.min()),
    }
