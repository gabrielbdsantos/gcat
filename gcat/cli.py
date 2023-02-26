# coding: utf-8
"""Provide utilities for the command line interface."""

import math

import typer

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
        help="Area of the computational domain.",
        show_default=False,
        metavar="",
        callback=exclusivity_callback,
    ),
    volume: float = typer.Option(
        default=0.0,
        help="Volume of the computational domain.",
        show_default=False,
        metavar="",
        callback=exclusivity_callback,
    ),
):
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
    h1 = representative_size(n1, total_size, num_dimensions)
    h2 = representative_size(n2, total_size, num_dimensions)
    h3 = representative_size(n3, total_size, num_dimensions)

    # Compute the refinement ratio
    ratio21 = h2 / h1
    ratio32 = h3 / h2

    log = (
        "Representative grid size",
        "------------------------",
        f"h1 = {h1:.6f}",
        f"h2 = {h2:.6f}",
        f"h3 = {h3:.6f}",
        "",
        "Refinement ratio",
        "----------------",
        f"r21 = {ratio21:.6f}",
        f"r32 = {ratio32:.6f}",
    )

    typer.echo("\n".join([x for x in log]))
