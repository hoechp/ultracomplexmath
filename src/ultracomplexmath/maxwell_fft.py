"""Optional NumPy adapter for periodic, band-limited vacuum initial data."""

import importlib
import math
from collections.abc import Sequence
from typing import Any

from .core import Ultra
from .maxwell import MaxwellField, MaxwellMode, _direction


def periodic_maxwell_field(
    electric: Any,
    magnetic: Any,
    lengths: Sequence[float],
    *,
    electric_tangent: Any = None,
    magnetic_tangent: Any = None,
    atol: float = 0.0,
) -> MaxwellField:
    """Fit real arrays shaped (nx,ny,nz,3), sampled at x_i=L*i/n.

    Drop FFT roundoff within each input layer and the requested absolute
    amplitude tolerance. Reject longitudinal content and occupied Nyquist
    planes where off-grid continuation of the real samples is ambiguous.
    """
    np = importlib.import_module("numpy")
    sides = _direction(lengths)
    if min(sides) <= 0 or not math.isfinite(atol) or atol < 0:
        raise ValueError("Positive periods and a finite nonnegative tolerance are required")
    e = np.asarray(electric)
    if e.ndim != 4 or e.shape[-1] != 3 or min(e.shape[:3]) < 1:
        raise ValueError("Expected rectangular real arrays of shape (nx,ny,nz,3)")
    spectra: list[Any] = []
    tolerances = []
    for array in (e, magnetic, electric_tangent, magnetic_tangent):
        if array is None:
            spectra.append(None)
            tolerances.append(0.0)
            continue
        v = np.asarray(array)
        if v.shape != e.shape or v.dtype.kind not in "fiu" or not np.isfinite(v).all():
            raise ValueError(
                "Field samples and tangents must be finite real arrays of matching shape"
            )
        v = v.astype(float)
        spectrum = np.fft.fftn(v, axes=(0, 1, 2), norm="forward")
        spectra.append(spectrum)
        tolerances.append(max(atol, 32 * np.finfo(float).eps * float(np.max(np.abs(v)))))
    if spectra[1] is None:
        raise ValueError("Magnetic samples are required")
    shape = e.shape[:3]
    modes = []

    def phasors(body: Any, tangent: Any) -> list[Ultra]:
        return [
            Ultra(real=z.real, i=z.imag, eps=w.real, eps_i=w.imag)
            for z, w in zip(body, tangent, strict=True)
        ]

    for index in np.ndindex(shape):
        partner = tuple((-k) % n for k, n in zip(index, shape, strict=True))
        if index > partner:
            continue
        freq = tuple(i if i <= n // 2 else i - n for i, n in zip(index, shape, strict=True))
        k = tuple(math.tau * f / L for f, L in zip(freq, sides, strict=True))
        length = math.hypot(*k)
        normal = np.array(k) / length if length else None
        amplitudes = []
        for spectrum, threshold in zip(spectra, tolerances, strict=True):
            a = np.zeros(3, dtype=complex) if spectrum is None else spectrum[index].copy()
            if max(abs(a)) <= threshold:
                a[:] = 0
            elif any(n % 2 == 0 and i == n // 2 for i, n in zip(index, shape, strict=True)):
                raise ValueError("An occupied Nyquist plane needs a finer sampling grid")
            elif normal is not None:
                longitudinal = np.dot(normal, a)
                if abs(longitudinal) > 4 * threshold:
                    raise ValueError("Initial samples violate a vacuum divergence constraint")
                a -= normal * longitudinal
                # FFT roundoff can leave a tiny real part beside an imaginary
                # signal (or vice versa). Apply the same noise floor to each.
                for quadrature in (a.real, a.imag):
                    if max(abs(quadrature)) <= threshold:
                        quadrature[:] = 0
            amplitudes.append(a if index == partner else 2 * a)
        if any(np.any(a) for a in amplitudes):
            e0, b0, de, db = amplitudes

            modes.append(MaxwellMode(k, phasors(e0, de), phasors(b0, db)))
    return MaxwellField(modes)
