# modules/webscan.py

import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from rich.progress import Progress, SpinnerColumn, TextColumn
import os

def run_scan(target, url, dir_brute, wordlist_path, verbose, output_file, console):
    """
    Performs web enumeration on the target.
    """
    if not url:
        # Try common HTTP/S ports if no URL is explicitly provided
        console.print(f"[dim]No URL provided. Attempting to connect to http://{target} and https://{target}[/dim]")
        # Basic check for HTTP/HTTPS
        try_urls = [f"http://{target}", f"https://{target}"]
        found_url = None
        for u in try_urls:
            try:
                response = requests.get(u, timeout=5)
                if response.status_code < 400:
                    found_url = u
                    console.print(f"[green]Successfully connected to {found_url}[/green]")
                    break
            except requests.exceptions.ConnectionError:
                console.print(f"[red]Could not connect to {u}[/red]")
            except requests.exceptions.Timeout:
                console.print(f"[yellow]Connection to {u} timed out.[/yellow]")
            except Exception as e:
                console.print(f"[red]Error connecting to {u}: {e}[/red]")
        if not found_url:
            console.print("[bold red]Could not find an active web server on common HTTP/S ports.[/bold red]")
            return
        url = found_url

    console.print(f"[blue]Starting Web Scan on {url}...[/blue]")
    web_results = {'url': url}

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("[cyan]Fetching main page...", total=None)
            response = requests.get(url, timeout=10)
            progress.update(task, description="[green]Main page fetched![/green]")

        web_results['status_code'] = response.status_code
        web_results['headers'] = dict(response.headers)
        web_results['content_length'] = len(response.content)

        console.print(f"  [bold underline]Main Page Info:[/bold underline]")
        console.print(f"    Status Code: [green]{response.status_code}[/green]")
        console.print(f"    Content Length: {len(response.content)} bytes")
        console.print(f"    Headers:")
        for header, value in response.headers.items():
            console.print(f"      [dim]{header}: {value}[/dim]")

        soup = BeautifulSoup(response.text, 'lxml')
        title = soup.title.string if soup.title else "No Title"
        web_results['title'] = title
        console.print(f"    Title: [cyan]{title}[/cyan]")

        # Basic comment extraction
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))
        if comments:
            web_results['comments'] = [str(c).strip() for c in comments]
            console.print(f"    [bold yellow]Found Comments:[/bold yellow]")
            for comment in comments:
                console.print(f"      [dim]- {str(comment).strip()}[/dim]")

        # Directory Brute-forcing
        if dir_brute:
            console.print(f"\n[bold yellow]Starting Directory Brute-forcing with {wordlist_path}...[/bold yellow]")
            if not os.path.exists(wordlist_path):
                console.print(f"[bold red]Error: Wordlist not found at {wordlist_path}[/bold red]")
                return

            web_results['dir_brute_results'] = []
            with open(wordlist_path, 'r') as f:
                wordlist = [line.strip() for line in f if line.strip()]

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console,
                transient=False
            ) as progress:
                dir_task = progress.add_task("[cyan]Brute-forcing directories...", total=len(wordlist))
                for entry in wordlist:
                    test_url = urljoin(url, entry)
                    try:
                        dir_response = requests.get(test_url, timeout=5)
                        if dir_response.status_code not in [404]: # Filter out common "Not Found"
                            console.print(f"    [green]Found {test_url} (Status: {dir_response.status_code})[/green]")
                            web_results['dir_brute_results'].append({
                                'url': test_url,
                                'status_code': dir_response.status_code,
                                'content_length': len(dir_response.content)
                            })
                    except requests.exceptions.RequestException as req_e:
                        if verbose:
                            console.print(f"[dim]    Error accessing {test_url}: {req_e}[/dim]")
                    progress.update(dir_task, advance=1)
                progress.update(dir_task, description="[green]Directory brute-forcing complete![/green]")

        if output_file:
            output_formatter.save_results(output_file, web_results, console)

    except requests.exceptions.RequestException as e:
        console.print(f"[bold red]Web Scan Error: {e}[/bold red]")
    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during web scan: {e}[/bold red]")

# To extract comments from HTML
from bs4 import Comment

# Example usage (for testing this module directly)
if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    console.print("[bold green]Running standalone webscan.py for testing.[/bold green]")
    # run_scan("example.com", "http://example.com", True, "../wordlists/common.txt", True, None, console)
    console.print("[dim]To test, run: python3 main.py webscan -t example.com --dir-brute[/dim]")
