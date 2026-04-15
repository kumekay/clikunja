from __future__ import annotations

import typer

from clikunja.commands._common import call, print_json, print_table

comments_app = typer.Typer(
    name="comments", help="Manage comments on Vikunja tasks.", no_args_is_help=True
)


@comments_app.command("list")
def list_comments(
    task: int = typer.Option(..., "--task", help="Task ID."),
    json_out: bool = typer.Option(False, "--json"),
) -> None:
    data = call("GET", f"/tasks/{task}/comments")
    if json_out:
        print_json(data)
        return
    rows = [
        {
            "id": c.get("id"),
            "author": (c.get("author") or {}).get("username"),
            "comment": (c.get("comment") or "").splitlines()[0] if c.get("comment") else "",
        }
        for c in (data or [])
    ]
    print_table(rows, [("ID", "id"), ("AUTHOR", "author"), ("COMMENT", "comment")])


@comments_app.command("add")
def add_comment(
    task: int = typer.Option(..., "--task"),
    body: str = typer.Argument(..., metavar="BODY"),
) -> None:
    data = call("PUT", f"/tasks/{task}/comments", json={"comment": body})
    typer.echo(f"Added comment #{data.get('id')} on task #{task}")


@comments_app.command("edit")
def edit_comment(
    comment_id: int = typer.Argument(..., metavar="ID"),
    task: int = typer.Option(..., "--task"),
    body: str = typer.Option(..., "--body"),
) -> None:
    call("POST", f"/tasks/{task}/comments/{comment_id}", json={"comment": body})
    typer.echo(f"Updated comment #{comment_id}")


@comments_app.command("delete")
def delete_comment(
    comment_id: int = typer.Argument(..., metavar="ID"),
    task: int = typer.Option(..., "--task"),
) -> None:
    call("DELETE", f"/tasks/{task}/comments/{comment_id}")
    typer.echo(f"Deleted comment #{comment_id}")
