import ipaddress
import platform
import shutil
import subprocess
import sys

import httpx
import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="lograda_time",
    help="LOGRADA_TIME - Cybersecurity and OSINT toolkit",
)

console = Console()

BANNER = r"""
 _      ___   ____  ____      _    ____   _
| |    / _ \ / ___||  _ \    / \  |  _ \ / \
| |   | | | | |  _ | |_) |  / _ \ | | | / _ \
| |___| |_| | |_| ||  _ <  / ___ \| |_| / ___ \
|_____|\___/ \____||_| \_\/_/   \_\____/_/
               LOGRADA_TIME
"""


@app.command()
def status():
    """Display application and system status."""
    console.print(BANNER, style="bold green")

    table = Table(title="LOGRADA_TIME System Status")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")

    table.add_row("Python", sys.version.split()[0])
    table.add_row("Operating System", platform.platform())

    for tool in ["nmap", "zaproxy", "tshark"]:
        table.add_row(tool, shutil.which(tool) or "Not installed")

    console.print(table)


@app.command()
def tools():
    """List supported external security tools."""
    for name in ["nmap", "zaproxy", "tshark"]:
        path = shutil.which(name)
        console.print(
            f"[green][+] {name}: {path}[/green]"
            if path
            else f"[yellow][-] {name}: not found[/yellow]"
        )


@app.command()
def check_headers(
    url: str = typer.Option(
        ...,
        "--url",
        help="HTTPS URL you own or are authorized to assess.",
    ),
):
    """Inspect basic HTTP security headers."""
    if not url.startswith("https://"):
        console.print("[red]Please provide an HTTPS URL.[/red]")
        raise typer.Exit(code=1)

    try:
        with httpx.Client(
            timeout=10,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            response = client.get(url)

        console.print(f"URL: {url}")
        console.print(f"HTTP status: {response.status_code}")

        table = Table(title="Security Header Review")
        table.add_column("Header", style="cyan")
        table.add_column("Result")

        headers = [
            "strict-transport-security",
            "content-security-policy",
            "x-content-type-options",
            "x-frame-options",
            "referrer-policy",
        ]

        for header in headers:
            value = response.headers.get(header)
            table.add_row(
                header,
                value if value else "[yellow]Not present[/yellow]",
            )

        console.print(table)

    except httpx.HTTPError as exc:
        console.print(f"[red]Request failed: {exc}[/red]")
        raise typer.Exit(code=1)


@app.command("network-scan")
def network_scan(
    target: str = typer.Option(
        ...,
        "--target",
        help="Private IP or private subnet, e.g. 192.168.1.10",
    ),
    confirm: bool = typer.Option(
        False,
        "--confirm",
        help="Confirm authorization to scan this network.",
    ),
):
    """Scan a small private network with Nmap."""
    if not confirm:
        console.print(
            "[yellow]Add --confirm only for a network "
            "you own or are authorized to test.[/yellow]"
        )
        raise typer.Exit(code=1)

    try:
        network = ipaddress.ip_network(target, strict=False)
    except ValueError:
        console.print("[red]Invalid IP address or subnet.[/red]")
        raise typer.Exit(code=1)

    if not (
        network.is_private
        or network.is_loopback
        or network.is_link_local
    ):
        console.print(
            "[red]Only private, loopback, or link-local networks "
            "are allowed in this initial version.[/red]"
        )
        raise typer.Exit(code=1)

    if network.num_addresses > 256:
        console.print(
            "[red]Limit exceeded: use a network with "
            "at most 256 addresses.[/red]"
        )
        raise typer.Exit(code=1)

    nmap = shutil.which("nmap")
    if not nmap:
        console.print("[red]Nmap is not installed.[/red]")
        raise typer.Exit(code=1)

    command = [
        nmap,
        "-sT",
        "-T3",
        "--top-ports",
        "100",
        "--max-retries",
        "2",
        "--host-timeout",
        "60s",
        str(network),
    ]

    console.print(f"[bold green]Scanning: {network}[/bold green]")

    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )

        console.print(result.stdout or "No scan output.")

        if result.returncode != 0:
            console.print(f"[red]{result.stderr}[/red]")
            raise typer.Exit(code=1)

    except subprocess.TimeoutExpired:
        console.print("[red]Scan timed out.[/red]")
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
