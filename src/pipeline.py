"""Pipeline orchestrator — wires 4 agents together with structured data passing."""

import json
import time
from dataclasses import dataclass, field
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.llm.client import LLMClient, LLMConfig
from src.agents import collector, analyzer, diagnoser, advisor
from src.utils import collect_log_files, format_logs_for_prompt

console = Console()


@dataclass
class PipelineResult:
    collector_report: dict = field(default_factory=dict)
    analyzer_report: dict = field(default_factory=dict)
    diagnoser_report: dict = field(default_factory=dict)
    advisor_report: dict = field(default_factory=dict)
    token_usage: dict = field(default_factory=dict)
    elapsed_seconds: float = 0.0
    errors: list[str] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return len(self.errors) == 0

    @property
    def total_recommendations(self) -> int:
        return len(self.advisor_report.get("recommendations", []))


class Pipeline:
    """LogFlow pipeline: Collector → Analyzer → Diagnoser → Advisor."""

    def __init__(self, config: LLMConfig | None = None):
        self.client = LLMClient(config)
        self.result = PipelineResult()

    def run(self, target_dir: str, dry_run: bool = False) -> PipelineResult:
        """Execute the full 4-agent pipeline on a target directory."""
        t0 = time.time()

        # Stage 1: Collect
        console.print(Panel.fit("[bold blue]STAGE 1/4: Collector Agent[/] — parsing logs", border_style="blue"))
        files = collect_log_files(target_dir)
        if not files:
            self.result.errors.append("No log files found in target directory")
            return self.result
        log_text = format_logs_for_prompt(files)
        self.result.collector_report = collector.run(log_text, self.client)
        self._print_collector_summary()

        if dry_run:
            self.result.elapsed_seconds = time.time() - t0
            return self.result

        # Stage 2: Analyze
        console.print(Panel.fit("[bold yellow]STAGE 2/4: Analyzer Agent[/] — detecting patterns", border_style="yellow"))
        self.result.analyzer_report = analyzer.run(self.result.collector_report, self.client)
        self._print_analyzer_summary()

        # Stage 3: Diagnose
        console.print(Panel.fit("[bold green]STAGE 3/4: Diagnoser Agent[/] — tracing root causes", border_style="green"))
        self.result.diagnoser_report = diagnoser.run(self.result.analyzer_report, self.client)
        self._print_diagnoser_summary()

        # Stage 4: Advise
        console.print(Panel.fit("[bold red]STAGE 4/4: Advisor Agent[/] — generating recommendations", border_style="red"))
        self.result.advisor_report = advisor.run(self.result.diagnoser_report, self.client)
        self._print_advisor_summary()

        self.result.elapsed_seconds = time.time() - t0
        self._print_final_summary()
        return self.result

    def _print_collector_summary(self):
        r = self.result.collector_report
        m = r.get("metrics", {})
        table = Table(title="Collector Results")
        table.add_column("Metric", style="cyan")
        table.add_column("Count", style="magenta")
        for key in ["total_lines", "total_entries", "error_entries", "unique_sources"]:
            table.add_row(key.replace("_", " ").title(), str(m.get(key, "?")))
        console.print(table)
        dist = r.get("level_distribution", {})
        if dist:
            console.print(f"[dim]Levels: {dist}[/dim]")
        if r.get("summary"):
            console.print(f"[dim]{r['summary']}[/dim]")

    def _print_analyzer_summary(self):
        a = self.result.analyzer_report
        clusters = a.get("error_clusters", [])
        anomalies = a.get("anomalies", [])
        console.print(f"[yellow]Error clusters:[/] {len(clusters)}")
        for c in clusters:
            console.print(f"  • [bold]{c.get('cluster_id', '?')}[/] [{c.get('severity', '?')}] {c.get('pattern', 'N/A')} (×{c.get('count', '?')})")
        console.print(f"[yellow]Anomalies:[/] {len(anomalies)}")
        if a.get("summary"):
            console.print(f"[dim]{a['summary']}[/dim]")

    def _print_diagnoser_summary(self):
        d = self.result.diagnoser_report
        diags = d.get("diagnoses", [])
        console.print(f"[green]Diagnoses:[/] {len(diags)}")
        for diag in diags:
            console.print(f"  • [bold]{diag.get('cluster_id', '?')}[/] confidence={diag.get('confidence', '?')}: {diag.get('root_cause', 'N/A')[:80]}")
        if d.get("summary"):
            console.print(f"[dim]{d['summary']}[/dim]")

    def _print_advisor_summary(self):
        a = self.result.advisor_report
        recs = a.get("recommendations", [])
        console.print(f"[red]Recommendations:[/] {len(recs)}")
        for r in recs:
            console.print(f"  • [bold]{r.get('priority', '?')}[/] {r.get('title', 'N/A')} ({r.get('estimated_effort', '?')})")
        if a.get("quick_wins"):
            console.print(f"[dim]Quick wins: {len(a['quick_wins'])}[/]")
        if a.get("summary"):
            console.print(f"[dim]{a['summary']}[/dim]")

    def _print_final_summary(self):
        console.print()
        console.print(Panel.fit(
            f"[bold]Pipeline Complete[/]\n"
            f"Time: {self.result.elapsed_seconds:.1f}s\n"
            f"Error clusters: {len(self.result.analyzer_report.get('error_clusters', []))}\n"
            f"Recommendations: {self.result.total_recommendations}\n"
            f"Errors: {len(self.result.errors)}",
            border_style="green" if self.result.success else "red"
        ))

    def save_report(self, path: str):
        """Save the full pipeline result as JSON."""
        with open(path, "w", encoding="utf-8") as f:
            json.dump({
                "collector_report": self.result.collector_report,
                "analyzer_report": self.result.analyzer_report,
                "diagnoser_report": self.result.diagnoser_report,
                "advisor_report": self.result.advisor_report,
                "elapsed_seconds": self.result.elapsed_seconds,
                "errors": self.result.errors,
            }, f, ensure_ascii=False, indent=2)
        console.print(f"[green]Report saved to {path}[/]")
