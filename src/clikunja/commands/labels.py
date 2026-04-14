from __future__ import annotations

import typer

from clikunja.commands._common import call, print_json, print_table

labels_app = typer.Typer(
    name="labels", help="Manage Vikunja labels.", no_args_is_help=True
)


@labels_app.command("list")
def list_labels(json_out: bool = typer.Option(False, "--json")) -> None:
    data = call("GET", "/labels")
    if json_out:
        print_json(data)
        return
    print_table(
        data or [],
        [("ID", "id"), ("TITLE", "title"), ("COLOR", "hex_color")],
    )


@labels_app.command("create")
def create_label(
    title: str = typer.Option(..., "--title"),
    color: str | None = typer.Option(None, "--color", help="Hex color without '#'."),
) -> None:
    body: dict = {"title": title}
    if color is not None:
        body["hex_color"] = color
    data = call("PUT", "/labels", json=body)
    typer.echo(f"Created label #{data.get('id')} {data.get('title', title)}")


@labels_app.command("edit")
def edit_label(
    label_id: int = typer.Argument(..., metavar="ID"),
    title: str | None = typer.Option(None, "--title"),
    color: str | None = typer.Option(None, "--color"),
) -> None:
    body: dict = {}
    if title is not None:
        body["title"] = title
    if color is not None:
        body["hex_color"] = color
    call("PUT", f"/labels/{label_id}", json=body)
    typer.echo(f"Updated label #{label_id}")


@labels_app.command("delete")
def delete_label(label_id: int = typer.Argument(..., metavar="ID")) -> None:
    call("DELETE", f"/labels/{label_id}")
    typer.echo(f"Deleted label #{label_id}")
