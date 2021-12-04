#!/usr/bin/env python
# coding=utf-8
"""Utilities for convergence-related calculations.

Classes and functions within this module follow the nomenclature
presented in [1, 2]. References used in docstrings are presented in the
``References`` section below.

References
----------
[1] I. B. Celik, U. Ghia, P. J. Roache, C. J. Freitas, H. Coleman, and
    P. E. Raad, Procedure for Estimation and Reporting of Uncertainty
    Due to Discretization in CFD Applications,” J. Fluids Eng., vol.
    130, no. 7, p. 078001, Jul. 2008, doi: 10.1115/1.2960953.

[2] P. J. Roache, Quantification of Uncertainty in Computational Fluid
    Dynamics, Annu. Rev. Fluid Mech., vol. 29, no. 1, pp. 123–160, Jan.
    1997, doi: 10.1146/annurev.fluid.29.1.123.

[3] Examining Spatial (Grid) Convergence.
    https://www.grc.nasa.gov/WWW/wind/valid/tutorial/spatconv.html
    (accessed Oct. 22, 2020).

"""

import math


def apparent_order_of_convergence(
    h1: float,
    h2: float,
    h3: float,
    f1: float,
    f2: float,
    f3: float,
    omega: float = 0.5,
    tol: float = 1e-5,
    max_iter: float = 1e6,
    max_residual: float = 1e6,
) -> float:
    """Calculate the apparent order of convergence.

    Parameters
    ----------
    h1 : float
        Representative grid size for the 1st grid (finer).
    h2 : float
        Representative grid size for the 2nd grid (medium).
    h3 : float
        Representative grid size for the 3rd grid (coarser).
    f1 : float
        Solution on the 1st grid.
    f2 : float
        Solution on the 2nd grid.
    f3 : float
        Solution on the 3rd grid.
    min_ref_factor : float, optional
        Minimum refinement factor allowed.
    omega : float, optional
        Relaxation factor used in the bleding fuction during the
        iterative process. Should be between zero and one.
    tol : float
        Maximum tolerance for the iterative process.
    max_iter : int
        Maximum number of iterations. Prevents an infinite interation
        loop.
    max_residual : float
        Maximum residual for the interative process.

    Returns
    -------
    float
        The apparent order of convergence.

    Raises
    ------
    RuntimeError
        The iterative process did not converge before reaching either
        the maximum number of iterations or the maximum residual.
    ValueError
        `omega` is out of bounds
    """
    if omega < 0 or omega > 1:
        raise ValueError("Relaxation factor `omega` out of bound.")

    # Compute the grid refinement factor
    r21 = h2 / h1
    r32 = h3 / h2

    epsilon21 = f2 - f1
    epsilon32 = f3 - f2
    epsilon_ratio = epsilon32 / epsilon21

    # Get the signal of 'epsilon_ratio'
    s = 1 - 2 * (epsilon_ratio < 0)

    # Initial values for the iteration loop
    residual = 0
    iterations = 0
    p = (1.0 / math.log(r21)) * abs(math.log(abs(epsilon_ratio)))

    while abs(residual) > tol:
        # If it all goes wrong, stop it!
        if iterations > max_iter or residual > max_residual:
            raise RuntimeError(
                "Could not find the apparent order of convergence. "
                "The iterative process did not converge."
            )

        # Update p1 as p
        p1 = p

        # Calculate q
        q = math.log((r21 ** p1 - s) / (r32 ** p1 - s))

        # Calculate p2
        p2 = (1.0 / math.log(r21)) * abs(math.log(abs(epsilon_ratio)) + q)

        # Update p using a relaxation factor 'omega' that blends p1 and p2
        p = (1 - omega) * p1 + omega * p2

        # Calculate the residual of the current iteration
        residual = p - p1

        # Increase the interation number
        iterations += 1

    # Return the resulting value of p
    return p


def richardson_extrapolation(
    h1: float, h2: float, f1: float, f2: float, p: float
) -> float:
    """Estimate the Richardson extrapolation.

    Richardson extrapolation is a method for obtaining a higher-order
    estimate of the continuum value (value at zero grid spacing) from a
    series of lower-order discrete values.

    A simulation will yield a quantity f that can be expressed in a
    general form by the series expansion:

        f = f_exact + g1*h + g2*h2 + g3*h3 + ...                (1)

    where h is the grid spacing and the functions g1, g2, and g3 are
    independent of the grid spacing. The quantity f is considered
    "second-order" if g1 = 0. The f_exact = 0 is the continuum value at
    zero grid spacing.

    If one assumes a second-order solution and has computed f on two
    grids of spacing h1 and h2 with h1 being the finer (smaller)
    spacing, then one can write two equations for the above expansion,
    neglect third-order and higher terms, and solve for f_exact = 0 to
    estimate the continuum value,

        f_exact = f1 + (f1 - f2) / (r^p - 1)                    (2)

    where the grid refinement factor ratio is:

        r = h2 / h1                                             (3)

    In general, we will consider f_exact = 0 to be p + 1 order accurate.
    Richardson extrapolation can be applied for the solution at each
    grid point, or to solution functionals, such as pressure recovery or
    drag. This assumes that the solution is globally second-order in
    addition to locally second-order and that the solution functionals
    were computed using consistent second-order methods. Other cautions
    with using Richardson extrapolation (non-conservative, amplification
    of round-off error, etc...) are discussed in Ref. [2].

    Parameters
    ----------
    h1 : float
        Representative grid size for the 1st grid (finer).
    h2 : float
        Representative grid size for the 2nd grid (coarser).
    f1 : float
        Solution on the 1st grid.
    f2 : float
        Solution on the 2nd grid.
    p : float
        Apparent order of convergence.

    Returns
    -------
    float
        The continuum solution on a zero-spacing grid.

    Raises
    ------
    ZeroDivisionError
        Either (h1) or ((h2/h1)**p - 1.0) is zero.
    TypeError
        At least one of the input parameters does not follow the type
        requirements presented in the ``Parameters`` section.

    """
    # Compute the grid refinement factor
    r21 = h2 / h1

    # Compute the continue value at zero grid spacing
    f_exact = ((r21 ** p) * f1 - f2) / (r21 ** p - 1.0)

    return f_exact


def relative_error(f1: float, f2: float) -> float:
    """Compute the relative error between two values.

    Parameters
    ----------
    f1 : float
        The reference value.
    f2 : float
        The value being compared.

    Returns
    -------
    float
        The relative error.

    Raises
    ------
    ZeroDivisionError
        `f1` is zero.

    """
    return abs((f1 - f2) / f1)


def gci_fine(
    f1: float, f2: float, r21: float, p: float, safety_factor: float = 1.25
) -> float:
    """Calculate an error estimation for the fine grid.

    A fine-grid Richardson error estimator approximates the error in a
    fine-grid solution by comparing the solution to that with of a
    coarse grid. It can be defined as:

        E_fine = Fs * (f1/f2) / (r21^p - 1)                     (1)

    where Fs is a safety factor, f1 is the solution on the fine grid, f2
    is the solution on the coarse grid, r21 is the refinement factor
    between the coarse and fine grid, and p is the apparent order of
    convergence.

    Parameters
    ----------
    f1 : float
        The solution on the fine grid.
    f2 : float
        The solution on the coarse grid.
    r21 : float
        The refinement factor between the coarse and the fine grid.
    p : float
        The apparent order of convergence.
    safety_factor : float, optional
        The safety factor.

    Returns
    -------
    float
        The estimated error for the fine-grid solution.

    """
    return (safety_factor * relative_error(f1, f2)) / (r21 ** p - 1.0)


def gci_coarse(
    f1: float, f2: float, r21: float, p: float, safety_factor: float = 1.25
) -> float:
    """Calculate an error estimation for the coarse grid.

    A coarse-grid Richardson error estimator approximates the error in a
    coarse-grid solution by comparing the solution to that with of a
    coarse grid. It can be defined as:

        E_fine = Fs * (f1/f2)*r21^p / (r21^p - 1)               (1)

    where Fs is a safety factor, f1 is the solution on the fine grid, f2
    is the solution on the coarse grid, r21 is the refinement factor
    between the coarse and fine grid, and p is the apparent order of
    convergence.

    Parameters
    ----------
    f1 : float
        The solution on the fine grid.
    f2 : float
        The solution on the coarse grid.
    r21 : float
        The refinement factor between the coarse and the fine grid.
    p : float
        The apparent order of convergence.
    safety_factor : float, optional
        The safety factor.

    Returns
    -------
    float
        The estimated error for the coarse-grid solution.

    """
    return (
        (safety_factor * relative_error(f1, f2)) * r21 ** p / (r21 ** p - 1.0)
    )


def asymptotic_ratio(
    gci21_fine: float, gci32_fine: float, r21: float, p: float
) -> float:
    """Calculate the ratio between succesive solutions.

    If the ratio is close to the unit, then the grids are within the
    asymptotic range.

    Parameters
    ----------
    gci21_fine : float
    gci32_fine : float
    r21 : float
        The refinement factor between the coarse and the fine grid.
    p : float
        The apparent order of convergence.

    Returns
    -------
    float
        The asymptotic ratio of convergence.

    """
    return r21 ** p * (gci21_fine / gci32_fine)
