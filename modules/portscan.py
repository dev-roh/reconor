# modules/portscan.py

import nmap
from rich.progress import Progress, SpinnerColumn, TextColumn

def run_scan(target, ports, full_scan, udp_scan, verbose, output_file, console):
    """
    Performs a port scan on the target using python-nmap.
    """
    console.print(f"[blue]Starting Nmap scan on {target}...[/blue]")

    nm = nmap.PortScanner()
    nmap_args = f"-sV {'-sU' if udp_scan else ''} {'-p 1-65535' if full_scan else f'-p {ports}'}"

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("[cyan]Nmap scanning...", total=None) # Total is None for indefinite task

            # Execute Nmap scan
            # Note: Nmap often requires root privileges for certain scan types (e.g., -sS, -sU)
            # You might need to run your main script with `sudo python3 main.py ...`
            # or configure Nmap to run without sudo for specific users (advanced)
            nm.scan(target, arguments=nmap_args)

            progress.update(task, description="[green]Nmap scan complete![/green]")

        scan_results = {}
        if target in nm.all_hosts():
            host = nm[target]
            scan_results['host'] = target
            scan_results['status'] = host.state()
            scan_results['protocols'] = {}

            console.print(f"\n[bold underline]Scan Results for {target}:[/bold underline]")
            console.print(f"  Status: [green]{host.state()}[/green]")

            for proto in host.all_protocols():
                scan_results['protocols'][proto] = {}
                console.print(f"  Protocol: [bold magenta]{proto}[/bold magenta]")
                lport = host[proto].keys()
                sorted_ports = sorted(lport)
                for port in sorted_ports:
                    port_info = host[proto][port]
                    state = port_info['state']
                    service = port_info['name']
                    product = port_info['product']
                    version = port_info['version']
                    extra_info = port_info['extrainfo']

                    scan_results['protocols'][proto][port] = {
                        'state': state,
                        'service': service,
                        'product': product,
                        'version': version,
                        'extrainfo': extra_info
                    }

                    console.print(
                        f"    Port: [cyan]{port}/{proto}[/cyan]\t"
                        f"State: [yellow]{state}[/yellow]\t"
                        f"Service: [green]{service}[/green] "
                        f"{product} {version} {extra_info}"
                    )
        else:
            console.print(f"[red]No hosts found or target is down.[/red]")

        # You can then use output_formatter to save these results
        if output_file:
            output_formatter.save_results(output_file, scan_results, console)

    except nmap.PortScannerError as e:
        console.print(f"[bold red]Nmap Error: {e}[/bold red]")
        console.print("[dim]Please ensure Nmap is installed and you have sufficient permissions (e.g., run with sudo for full scans).[/dim]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during port scan: {e}[/bold red]")

# Example usage (for testing this module directly)
if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    console.print("[bold green]Running standalone portscan.py for testing.[/bold green]")
    # This will likely fail without Nmap installed or root permissions
    # run_scan("scanme.nmap.org", "80,443", False, False, True, None, console)
    console.print("[dim]To test, run: python3 main.py portscan -t scanme.nmap.org[/dim]")
