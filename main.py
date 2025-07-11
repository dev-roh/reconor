# main.py

import argparse
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Import your modules
from modules import defaultscan, portscan
from modules import webscan
from modules import dnsenum
from utils import output_formatter

# Initialize Rich Console for pretty output
console = Console()

def main():
    """
    Main function to parse arguments and orchestrate the reconnaissance tool.
    """
    parser = argparse.ArgumentParser(
        description="A command-line reconnaissance tool for CTF and pentesting.",
        formatter_class=argparse.RawTextHelpFormatter # Keeps help text formatting
    )

    # --- Global Arguments ---
    parser.add_argument(
        "-t", "--target",
        help="Target IP address or hostname (e.g., 192.168.1.1, example.com)",
        required=True
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Increase output verbosity."
    )
    parser.add_argument(
        "-o", "--output",
        help="Output results to a file (e.g., results.json, results.txt).",
        type=str
    )

    # --- Module-Specific Arguments (using subparsers for better organization) ---
    subparsers = parser.add_subparsers(
        dest="module",
        help="Select a reconnaissance module to run.",
        required=True
    )

    # Port Scan Module
    portscan_parser = subparsers.add_parser(
        "portscan",
        help="Perform a port scan on the target using Nmap."
    )
    portscan_parser.add_argument(
        "-p", "--ports",
        help="Ports to scan (e.g., '80,443,22' or '1-1024'). Default: common ports.",
        default="top1000" # Nmap's default top 1000 ports
    )
    portscan_parser.add_argument(
        "--full",
        action="store_true",
        help="Perform a full TCP port scan (1-65535). Overrides -p."
    )
    portscan_parser.add_argument(
        "--udp",
        action="store_true",
        help="Include UDP port scanning (requires root/sudo for Nmap)."
    )

    # Web Scan Module
    webscan_parser = subparsers.add_parser(
        "webscan",
        help="Perform web enumeration and vulnerability checks."
    )
    webscan_parser.add_argument(
        "-u", "--url",
        help="Specify the full URL for web scanning (e.g., http://example.com:8080). If not provided, will try common HTTP/S ports.",
        type=str
    )
    webscan_parser.add_argument(
        "--dir-brute",
        action="store_true",
        help="Perform directory and file brute-forcing."
    )
    webscan_parser.add_argument(
        "--wordlist",
        help="Path to a custom wordlist for directory brute-forcing. Default: wordlists/common.txt",
        default="wordlists/common.txt"
    )

    # DNS Enumeration Module
    dnsenum_parser = subparsers.add_parser(
        "dnsenum",
        help="Perform DNS and subdomain enumeration."
    )
    dnsenum_parser.add_argument(
        "--sub-brute",
        action="store_true",
        help="Perform subdomain brute-forcing."
    )
    dnsenum_parser.add_argument(
        "--sub-wordlist",
        help="Path to a custom wordlist for subdomain brute-forcing. Default: wordlists/subdomains.txt",
        default="wordlists/subdomains.txt"
    )
    dnsenum_parser.add_argument(
        "--dns-server",
        help="Specify a custom DNS server to use (e.g., 8.8.8.8).",
        type=str
    )

    args = parser.parse_args()

    console.print(Panel(Text(f"Starting Reconnaissance on [bold green]{args.target}[/bold green]", justify="center"), style="bold blue", markup=True ))
    if args.verbose:
        console.print(f"[dim]Verbose mode enabled.[/dim]")

    # --- Call the appropriate module based on user selection ---
    try:
        # If no module is specified, or if explicitly called as 'defaultscan', run defaultscan
        if args.module is None or args.module == "defaultscan":
            console.print(f"\n[bold yellow]Running Default Scan Mode...[/bold yellow]")
            defaultscan.run_scan(args.target, args.verbose, args.output, console)
        elif args.module == "portscan":
            console.print(f"\n[bold yellow]Running Port Scan Module...[/bold yellow]")
            portscan.run_scan(args.target, args.ports, args.full, args.udp, args.verbose, args.output, console)
        elif args.module == "webscan":
            console.print(f"\n[bold yellow]Running Web Scan Module...[/bold yellow]")
            webscan.run_scan(args.target, args.url, args.dir_brute, args.wordlist, args.verbose, args.output, console)
        elif args.module == "dnsenum":
            console.print(f"\n[bold yellow]Running DNS Enumeration Module...[/bold yellow]")
            dnsenum.run_scan(args.target, args.sub_brute, args.sub_wordlist, args.dns_server, args.verbose, args.output, console)
        else:
            parser.print_help()
            sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]An error occurred during module execution: {e}[/bold red]", style="red")
        if args.verbose:
            import traceback
            console.print(traceback.format_exc(), style="red")
        sys.exit(1)

    console.print(Panel(Text(f"Reconnaissance complete for [bold green]{args.target}[/bold green]", justify="center"), style="bold blue"))


if __name__ == "__main__":
    main()
