"""LogFlow CLI — multi-agent log analysis pipeline."""

import sys
import click
from rich.console import Console
from rich.panel import Panel

from src.pipeline import Pipeline
from src.llm.client import LLMConfig

console = Console()


@click.group()
@click.version_option(version="0.1.0", prog_name="logflow")
def cli():
    """LogFlow — AI-powered multi-agent log analysis pipeline.

    Four specialized agents collaborate in sequence:
    Collector → Analyzer → Diagnoser → Advisor
    """


@cli.command()
@click.argument("target", type=click.Path(exists=True))
@click.option("--dry-run", is_flag=True, help="Run collector only, skip analysis stages")
@click.option("--output", "-o", default="logflow_report.json", help="Save full report to JSON file")
@click.option("--model", envvar="DEEPSEEK_MODEL", default="deepseek-chat", help="Model name override")
@click.option("--temperature", default=0.3, help="LLM temperature (0.0-1.0)")
def run(target, dry_run, output, model, temperature):
    """Run the full pipeline on TARGET directory containing log files."""
    config = LLMConfig.from_env()
    config.model = model
    config.temperature = temperature

    console.print(Panel.fit(
        "[bold]LogFlow Pipeline[/]\n"
        f"Target: {target}\n"
        f"Model: {config.model}\n"
        f"Mode: {'Dry Run (Collector only)' if dry_run else 'Full Pipeline'}",
        border_style="blue"
    ))

    try:
        pipeline = Pipeline(config)
        result = pipeline.run(target, dry_run=dry_run)

        if output and result.success:
            pipeline.save_report(output)
        elif result.errors:
            console.print("[red]Pipeline errors:[/]")
            for err in result.errors:
                console.print(f"  • {err}")
            sys.exit(1)
    except ValueError as e:
        console.print(f"[red]Configuration Error:[/] {e}")
        console.print("[dim]Make sure DEEPSEEK_API_KEY is set in your .env file[/]")
        sys.exit(1)
    except Exception as e:
        console.print(f"[red]Unexpected Error:[/] {e}")
        sys.exit(1)


@cli.command()
@click.argument("target", type=click.Path(exists=True))
def collect(target):
    """Run only the Collector agent on TARGET directory."""
    config = LLMConfig.from_env()
    try:
        pipeline = Pipeline(config)
        result = pipeline.run(target, dry_run=True)
        if result.success:
            pipeline.save_report("logflow_collect.json")
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        sys.exit(1)


@cli.command()
def config():
    """Show current configuration."""
    cfg = LLMConfig.from_env()
    console.print(f"API Base: {cfg.base_url}")
    console.print(f"Model: {cfg.model}")
    console.print(f"API Key: {'***' + cfg.api_key[-4:] if cfg.api_key else 'NOT SET'}")
    console.print(f"Temperature: {cfg.temperature}")


if __name__ == "__main__":
    cli()
