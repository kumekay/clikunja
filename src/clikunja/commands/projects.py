from __future__ import annotations

import typer

from clikunja.commands._common import call, print_json, print_table

projects_app = typer.Typer(name="projects", help="Manage Vikunja projects.", no_args_is_help=True)


@projects_app.command("list")
def list_projects(
    json_out: bool = typer.Option(False, "--json", help="Emit raw JSON."),
) -> None:
    data = call("GET", "/projects")
    if json_out:
        print_json(data)
        return
    print_table(
        data or [],
        [("ID", "id"), ("TITLE", "title"), ("PARENT", "parent_project_id")],
    )


@projects_app.command("view")
def view_project(
    project_id: int = typer.Argument(..., metavar="ID"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    data = call("GET", f"/projects/{project_id}")
    if json_out:
        print_json(data)
        return
    typer.echo(f"#{data.get('id')} {data.get('title')}")
    if data.get("description"):
        typer.echo(f"\n{data['description']}")


@projects_app.command("create")
def create_project(
    title: str = typer.Option(..., "--title"),
    description: str | None = typer.Option(None, "--description"),
) -> None:
    body: dict = {"title": title}
    if description is not None:
        body["description"] = description
    data = call("PUT", "/projects", json=body)
    typer.echo(f"Created project #{data.get('id')} {data.get('title', title)}")


@projects_app.command("edit")
def edit_project(
    project_id: int = typer.Argument(..., metavar="ID"),
    title: str | None = typer.Option(None, "--title"),
    description: str | None = typer.Option(None, "--description"),
) -> None:
    body: dict = {}
    if title is not None:
        body["title"] = title
    if description is not None:
        body["description"] = description
    data = call("POST", f"/projects/{project_id}", json=body)
    typer.echo(f"Updated project #{data.get('id', project_id)}")


@projects_app.command("delete")
def delete_project(project_id: int = typer.Argument(..., metavar="ID")) -> None:
    call("DELETE", f"/projects/{project_id}")
    typer.echo(f"Deleted project #{project_id}")
