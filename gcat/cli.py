# coding: utf-8
"""Provide utilities for the command line interface."""

import math

import typer

import gcat

app = typer.Typer(
    help="A simple cli for the grid convergence analysis toolkit (GCAT)",
    add_completion=False,
    no_args_is_help=True,
)


def MutuallyExclusiveGroup(size: int = 2, at_least_one: bool = True):
    """Create a mutually exclusive callback for typer."""
    group = set()
    active = set()

    def callback(_: typer.Context, param: typer.CallbackParam, value: str):
        group.add(param.name)

        if (
            value != param.default
            and value is not None
            and param.name not in active
        ):
            active.add(param.name)

        if len(active) > 1:
            raise typer.BadParameter(
                f"{param.name} is mutually exclusive with {active.pop()}"
            )

        if at_least_one and len(group) == size and len(active) == 0:
            typer.echo(
                f"Error: Expected one of the options: {[x for x in group]}"
            )
            raise typer.Exit(2)

        return value

    return callback


exclusivity_callback = MutuallyExclusiveGroup()


@app.command()
def check(
    n1: int = typer.Option(
        ...,
        help="Number of elements of the fine grid.",
        metavar="",
    ),
    n2: int = typer.Option(
        ...,
        help="Number of elements of the medium grid.",
        metavar="",
    ),
    n3: int = typer.Option(
        ...,
        help="Number of elements of the coarse grid.",
        metavar="",
    ),
    area: float = typer.Option(
        default=0.0,
        help="Area of the computational domain (in squared meters).",
        show_default=False,
        metavar="",
        callback=exclusivity_callback,
    ),
    volume: float = typer.Option(
        default=0.0,
        help="Volume of the computational domain (in cubic meters).",
        show_default=False,
        metavar="",
        callback=exclusivity_callback,
    ),
) -> None:
    """Check the representative size and refinement ratios."""
    # Note that area and volume are mutually exclusive. Thus, if volume is
    # zero, it is a two-dimensional case. Otherwise, it will be a
    # three-dimensional one.
    num_dimensions: int = 2 + 1 * (volume > 0.0)

    total_size = volume + area

    def representative_size(
        num_elements: int, total_size: float, num_dimensions: int
    ) -> float:
        """Compute the representative size of a given mesh."""
        return math.pow((total_size / num_elements), (1 / num_dimensions))

    # Compute the individual representative sizes
    h1 = representative_size(n1, total_size, num_dimensions)  # in meters
    h2 = representative_size(n2, total_size, num_dimensions)  # in meters
    h3 = representative_size(n3, total_size, num_dimensions)  # in meters

    # Compute the refinement ratio
    ratio21 = h2 / h1
    ratio32 = h3 / h2

    log = (
        "# Grid summary",
        "+ ------------",
        f"  N1 = {n1} elements",
        f"  N2 = {n2} elements",
        f"  N3 = {n3} elements",
        f"  Area = {area} m^2" if area > 0 else f"  Volume = {volume} m^3",
        "",
        "# Representative grid size",
        "+ ------------------------",
        f"  h1 = {h1 * 1e3:.6f} mm",
        f"  h2 = {h2 * 1e3:.6f} mm",
        f"  h3 = {h3 * 1e3:.6f} mm",
        "",
        "# Refinement ratio",
        "+ ----------------",
        f"  r21 = {ratio21:.6f}",
        f"  r32 = {ratio32:.6f}",
    )

    print("\n".join([x for x in log]))


@app.command()
def gci(
    h1: float = typer.Option(
        ...,
        help="Representative grid size of the fine mesh (in mm).",
        metavar="",
    ),
    h2: float = typer.Option(
        ...,
        help="Representative grid size of the medium mesh (in mm).",
        metavar="",
    ),
    h3: float = typer.Option(
        ...,
        help="Representative grid size of the coarse mesh (in mm).",
        metavar="",
    ),
    f1: float = typer.Option(
        ...,
        help="Model output for the fine mesh.",
        metavar="",
    ),
    f2: float = typer.Option(
        ...,
        help="Model output for the medium mesh.",
        metavar="",
    ),
    f3: float = typer.Option(
        ...,
        help="Model output for the coarse mesh.",
        metavar="",
    ),
    safety: float = typer.Option(
        default=1.25,
        help="Safety factor",
        metavar="",
    ),
) -> None:
    """Compute the grid convergence index."""
    p = gcat.convergence.apparent_order_of_convergence(h1, h2, h3, f1, f2, f3)

    r21 = h2 / h1
    r32 = h3 / h2

    gci21_fine = gcat.convergence.gci_fine(f1, f2, r21, p)
    gci21_coarse = gcat.convergence.gci_coarse(f1, f2, r21, p)

    gci32_fine = gcat.convergence.gci_fine(f2, f3, r32, p)
    gci32_coarse = gcat.convergence.gci_coarse(f2, f3, r32, p)

    r = gcat.convergence.asymptotic_ratio(gci21_fine, gci32_fine, r21, p)

    log = (
        "# Grid summary",
        "+ ---------------------------------------",
        f"  h1 = {h1:.6e} m, f1 = {f1:.6e}",
        f"  h2 = {h2:.6e} m, f2 = {f2:.6e}",
        f"  h3 = {h3:.6e} m, f3 = {f3:.6e}",
        "",
        f"# GCI (safety factor = {safety})",
        "+ ---------------------------------------",
        f"  GCI21_fine   = {gci21_fine * safety:.6e}",
        f"  GCI21_coarse = {gci21_coarse * safety:.6e}",
        "",
        f"  GCI32_fine   = {gci32_fine * safety:.6e}",
        f"  GCI32_coarse = {gci32_coarse * safety:.6e}",
        "",
        f"  Asymptotic ratio = {r:.6f}",
        f"  Observed order of convergence = {p:.6f}",
    )

    print("\n".join([x for x in log]))
