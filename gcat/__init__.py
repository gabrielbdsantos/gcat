#!/usr/bin/env python
# coding=utf-8
"""Grid Convergence Analysis Toolkit (GCAT)."""

__version__ = "1.1.0"

from .convergence import (
    apparent_order_of_convergence,
    asymptotic_ratio,
    gci_coarse,
    gci_fine,
    relative_error,
    richardson_extrapolation,
)
