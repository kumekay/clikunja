from __future__ import annotations

import typer

from clikunja.commands._common import call, print_json, print_table

tasks_app = typer.Typer(name="tasks", help="Manage Vikunja tasks.", no_args_is_help=True)


@tasks_app.command("list")
def list_tasks(
    project: int | None = typer.Option(None, "--project", help="Filter by project ID."),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    path = f"/projects/{project}/tasks" if project is not None else "/tasks"
    data = call("GET", path)
    if json_out:
        print_json(data)
        return
    print_table(
        data or [],
        [
            ("ID", "id"),
            ("DONE", "done"),
            ("TITLE", "title"),
            ("PROJECT", "project_id"),
        ],
    )


@tasks_app.command("view")
def view_task(
    task_id: int = typer.Argument(..., metavar="ID"),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    data = call("GET", f"/tasks/{task_id}")
    if json_out:
        print_json(data)
        return
    done = "[x]" if data.get("done") else "[ ]"
    typer.echo(f"#{data.get('id')} {done} {data.get('title')}")
    if data.get("description"):
        typer.echo(f"\n{data['description']}")


@tasks_app.command("create")
def create_task(
    project: int = typer.Option(..., "--project", help="Project ID."),
    title: str = typer.Option(..., "--title"),
    description: str | None = typer.Option(None, "--description"),
    priority: int | None = typer.Option(None, "--priority", min=0, max=5),
    due: str | None = typer.Option(None, "--due", help="RFC3339 timestamp."),
) -> None:
    body: dict = {"title": title}
    if description is not None:
        body["description"] = description
    if priority is not None:
        body["priority"] = priority
    if due is not None:
        body["due_date"] = due
    data = call("PUT", f"/projects/{project}/tasks", json=body)
    typer.echo(f"Created task #{data.get('id')} {data.get('title', title)}")


@tasks_app.command("edit")
def edit_task(
    task_id: int = typer.Argument(..., metavar="ID"),
    title: str | None = typer.Option(None, "--title"),
    description: str | None = typer.Option(None, "--description"),
    priority: int | None = typer.Option(None, "--priority", min=0, max=5),
) -> None:
    body: dict = {}
    if title is not None:
        body["title"] = title
    if description is not None:
        body["description"] = description
    if priority is not None:
        body["priority"] = priority
    call("POST", f"/tasks/{task_id}", json=body)
    typer.echo(f"Updated task #{task_id}")


def _toggle(task_id: int, done: bool) -> None:
    call("POST", f"/tasks/{task_id}", json={"done": done})
    verb = "done" if done else "reopened"
    typer.echo(f"Task #{task_id} marked {verb}.")


@tasks_app.command("done")
def done_task(task_id: int = typer.Argument(..., metavar="ID")) -> None:
    _toggle(task_id, True)


@tasks_app.command("undone")
def undone_task(task_id: int = typer.Argument(..., metavar="ID")) -> None:
    _toggle(task_id, False)


@tasks_app.command("delete")
def delete_task(task_id: int = typer.Argument(..., metavar="ID")) -> None:
    call("DELETE", f"/tasks/{task_id}")
    typer.echo(f"Deleted task #{task_id}")
