# modules/dnsenum.py

import dns.resolver
import dns.reversename
from rich.progress import Progress, SpinnerColumn, TextColumn
import os

def run_scan(target, sub_brute, sub_wordlist_path, dns_server, verbose, output_file, console):
    """
    Performs DNS and subdomain enumeration on the target.
    """
    console.print(f"[blue]Starting DNS Enumeration on {target}...[/blue]")
    dns_results = {'target': target}

    resolver = dns.resolver.Resolver()
    if dns_server:
        resolver.nameservers = [dns_server]
        console.print(f"[dim]Using custom DNS server: {dns_server}[/dim]")

    # Basic DNS Records
    record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA']
    dns_results['records'] = {}

    console.print(f"\n[bold underline]Basic DNS Records:[/bold underline]")
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("[cyan]Querying DNS records...", total=len(record_types))
        for rtype in record_types:
            try:
                answers = resolver.resolve(target, rtype)
                dns_results['records'][rtype] = [str(rdata) for rdata in answers]
                console.print(f"  [bold]{rtype}:[/bold]")
                for rdata in answers:
                    console.print(f"    [green]- {rdata}[/green]")
            except dns.resolver.NoAnswer:
                console.print(f"  [dim]{rtype}: No records found.[/dim]")
            except dns.resolver.NXDOMAIN:
                console.print(f"  [red]Error: Domain does not exist for {target}[/red]")
                break # No point continuing if domain doesn't exist
            except Exception as e:
                console.print(f"  [red]Error querying {rtype}: {e}[/red]")
            progress.update(task, advance=1)
        progress.update(task, description="[green]DNS record query complete![/green]")

    # Reverse DNS Lookup (if target is an IP)
    try:
        ip_parts = target.split('.')
        if len(ip_parts) == 4 and all(part.isdigit() and 0 <= int(part) <= 255 for part in ip_parts):
            console.print(f"\n[bold underline]Performing Reverse DNS Lookup:[/bold underline]")
            addr = dns.reversename.from_address(target)
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
                transient=True
            ) as progress:
                task = progress.add_task("[cyan]Reverse lookup...", total=None)
                ptr_records = resolver.resolve(addr, "PTR")
                dns_results['reverse_dns'] = [str(rdata) for rdata in ptr_records]
                for rdata in ptr_records:
                    console.print(f"  [green]{rdata}[/green]")
                progress.update(task, description="[green]Reverse DNS lookup complete![/green]")
        else:
            if verbose:
                console.print("[dim]Skipping reverse DNS lookup as target is not a valid IPv4 address.[/dim]")
    except dns.resolver.NXDOMAIN:
        console.print(f"  [dim]No reverse DNS record found for {target}.[/dim]")
    except Exception as e:
        console.print(f"[red]Error during reverse DNS lookup: {e}[/red]")


    # Subdomain Brute-forcing
    if sub_brute:
        console.print(f"\n[bold yellow]Starting Subdomain Brute-forcing with {sub_wordlist_path}...[/bold yellow]")
        if not os.path.exists(sub_wordlist_path):
            console.print(f"[bold red]Error: Subdomain wordlist not found at {sub_wordlist_path}[/bold red]")
            return

        dns_results['subdomains'] = []
        with open(sub_wordlist_path, 'r') as f:
            wordlist = [line.strip() for line in f if line.strip()]

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            console=console,
            transient=False
        ) as progress:
            sub_task = progress.add_task("[cyan]Brute-forcing subdomains...", total=len(wordlist))
            for sub in wordlist:
                full_domain = f"{sub}.{target}"
                try:
                    answers = resolver.resolve(full_domain, 'A')
                    for rdata in answers:
                        ip_address = str(rdata)
                        console.print(f"    [green]Found {full_domain} -> {ip_address}[/green]")
                        dns_results['subdomains'].append({'subdomain': full_domain, 'ip': ip_address})
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                    if verbose:
                        console.print(f"[dim]    {full_domain}: No record.[/dim]")
                except Exception as e:
                    if verbose:
                        console.print(f"[red]    Error resolving {full_domain}: {e}[/red]")
                progress.update(sub_task, advance=1)
            progress.update(sub_task, description="[green]Subdomain brute-forcing complete![/green]")

    if output_file:
        output_formatter.save_results(output_file, dns_results, console)

# Example usage (for testing this module directly)
if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    console.print("[bold green]Running standalone dnsenum.py for testing.[/bold green]")
    # run_scan("example.com", True, "../wordlists/subdomains.txt", None, True, None, console)
    console.print("[dim]To test, run: python3 main.py dnsenum -t example.com --sub-brute[/dim]")
