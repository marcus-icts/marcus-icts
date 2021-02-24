#!/usr/bin/env python
import click
from typing import Optional
from core import consume as _consume, run as _run

@click.command()
def consume():
  _consume()

@click.command()
@click.option('-s', '--subject', required=True, type=str, help="Crawler's file name (without extension .robot)")
@click.option('-d', '--related-data', type=str, help="Related data need to execute the task in JSON")
def run(subject: str, related_data: Optional[str]):
  _run(subject, related_data)

@click.group()
def cli():
  # não precisa de implementação
  pass

cli.add_command(consume)
cli.add_command(run)

if __name__ == "__main__":
  cli()
