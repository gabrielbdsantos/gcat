#!/usr/bin/env python
# coding=utf-8
"""Grid Convergence Analysis Tool kit (GCAT)."""

__version__ = "0.1.0-alpha"

from .convergence import (
    apparent_order_of_convergence,
    asymptotic_ratio,
    gci_coarse,
    gci_fine,
    relative_error,
    richardson_extrapolation,
)
