import subprocess
import os
from rich.console import Console

def nmap_scan(target):
    """
    Runs an nmap scan with -sC -sV options on the target.
    """
    print(f"[*] Running Nmap scan on {target}...")
    cmd = ["nmap", "-sC", "-sV", target]
    console = Console()
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        console.print(f"[!] Nmap scan failed: {e}", style="bold red")

def dir_scan(target, wordlist_path=None):
    """
    Runs gobuster dir scan on the target using the specified wordlist.
    """
    console = Console()
    if wordlist_path is None:
        wordlist_path = os.path.join(os.path.dirname(__file__), "..", "wordlists", "directories.txt")
    console.print(f"[*] Running Gobuster directory scan on {target}...", style="bold cyan")
    url = f"http://{target}"
    cmd = [
        "gobuster", "dir",
        "-u", url,
        "-w", wordlist_path
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        console.print(f"[!] Gobuster directory scan failed: {e}", style="bold red")

def vhost_scan(target, wordlist_path=None):
    """
    Runs gobuster vhost scan on the target using the specified wordlist.
    """
    console = Console()
    if wordlist_path is None:
        wordlist_path = os.path.join(os.path.dirname(__file__), "..", "wordlists", "common.txt")
    console.print(f"[*] Running Gobuster vhost scan on {target}...", style="bold cyan")
    url = f"http://{target}"
    cmd = [
        "gobuster", "vhost",
        "-u", url,
        "-w", wordlist_path,
        "-H", f"Host: {target}"
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        console.print(result.stdout)
    except subprocess.CalledProcessError as e:
        console.print(f"[!] Gobuster vhost scan failed: {e}", style="bold red")
        
def subdomain_scan(target, wordlist_path=None):
            """
            Uses ffuf to scan for subdomains of the target using the specified wordlist.
            """
            console = Console()
            if wordlist_path is None:
                wordlist_path = os.path.join(os.path.dirname(__file__), "..", "wordlists", "common.txt")
            console.print(f"[*] Running ffuf subdomain scan on {target}...", style="bold cyan")
            url = f"http://FUZZ.{target}"
            cmd = [
                "ffuf",
                "-w", wordlist_path,
                "-u", url,
                "-H", f"Host: {target}"
            ]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                console.print(result.stdout)
            except subprocess.CalledProcessError as e:
                console.print(f"[!] ffuf subdomain scan failed: {e}", style="bold red")
            """
            Uses ffuf to scan for subdomains of the target using the specified wordlist.
            """
            console = Console()
            if wordlist_path is None:
                wordlist_path = os.path.join(os.path.dirname(__file__), "..", "wordlists", "common.txt")
            console.print(f"[*] Running ffuf subdomain scan on {target}...", style="bold cyan")
            url = f"http://FUZZ.{target}"
            cmd = [
                "ffuf",
                "-w", wordlist_path,
                "-u", url,
                "-H", f"Host: {target}"
            ]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                console.print(result.stdout)
            except subprocess.CalledProcessError as e:
                console.print(f"[!] ffuf subdomain scan failed: {e}", style="bold red")

def run_scan(target):
    vhost_scan(target)
    dir_scan(target)
    nmap_scan(target)
    subdomain_scan(target)


if __name__ == "__main__":
    console = Console()
    target = "example.com"  # Replace with your target
    nmap_scan(target)
    dir_scan(target)
    vhost_scan(target)