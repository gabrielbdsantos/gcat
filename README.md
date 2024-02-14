# GCAT: grid convergence analysis toolkit

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![black](https://github.com/gabrielbdsantos/gcat/actions/workflows/black.yml/badge.svg?branch=master&event=push)](https://github.com/gabrielbdsantos/gcat/actions/workflows/black.yml)

> [!NOTE]
> The implementation is completed. Thus, do not expect updates to the code
> anymore.

## Installation

### Rye

1. Clone the repository

       git clone https://github.com/gabrielbdsantos/gcat
       cd gcat

2. Pin a specific Python version (optional)

       rye pin 3.x

3. Install

       rye sync

4. Activate the virtual environment.

       source .venv/bin/activate


### Pip

1. Clone the repository

       git clone https://github.com/gabrielbdsantos/gcat
       cd gcat

2. Create a virtual environment (optional)

       python3 -m venv .venv --clear

3. Install

       pip install -r requirements.lock

4. Activate it

       source .venv/bin/activate


## Quick start

1. Check the refinement ratios and representative grid sizes.

       $ gcat check --n1 1000 --n2 2000 --n3 3000 --area 0.5
       # Grid summary
       + ------------
         N1 = 2900 elements
         N2 = 1700 elements
         N3 = 1000 elements
         Area = 0.2 m^2

       # Representative grid size
       + ------------------------
         h1 = 8.304548 mm
         h2 = 10.846523 mm
         h3 = 14.142136 mm

       # Refinement ratio
       + ----------------
         r21 = 1.306094
         r32 = 1.303840

2. Compute the grid convergence index

       $ gcat gci --h1 8.30 --h2 10.84 --h3 14.14 --f1 1 --f2 1.02 --f3 1.08
       # Grid summary
       + ---------------------------------------
         h1 = 8.300000e+00 m, f1 = 1.000000e+00
         h2 = 1.084000e+01 m, f2 = 1.020000e+00
         h3 = 1.414000e+01 m, f3 = 1.080000e+00

       # GCI (safety factor = 1.25)
       + ---------------------------------------
         GCI21_fine   = 1.562500e-02
         GCI21_coarse = 4.687500e-02

         GCI32_fine   = 4.630449e-02
         GCI32_coarse = 1.382163e-01

         Asymptotic ratio = 1.012321


## References

 1. I. B. Celik, U. Ghia, P. J. Roache, C. J. Freitas, H. Coleman, and P. E.
    Raad, Procedure for Estimation and Reporting of Uncertainty Due to
    Discretization in CFD Applications,” J. Fluids Eng., vol. 130, no. 7, p.
    078001, Jul. 2008, doi: [10.1115/1.2960953][1].

 2. P. J. Roache, Quantification of Uncertainty in Computational Fluid Dynamics,
    Annu. Rev. Fluid Mech., vol. 29, no. 1, pp. 123–160, Jan. 1997, doi:
    [10.1146/annurev.fluid.29.1.123][2].

 3. Examining Spatial (Grid) Convergence.
    https://www.grc.nasa.gov/WWW/wind/valid/tutorial/spatconv.html (accessed
    Oct. 22, 2020).

## License

The code is licensed under the terms of the MIT license. For further
information refer to [LICENSE](./LICENSE).


[1]: https://doi.org/10.1115/1.2960953
[2]: https://doi.org/10.1146/annurev.fluid.29.1.123
