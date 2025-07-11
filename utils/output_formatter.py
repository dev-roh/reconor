# utils/output_formatter.py

import json
import os

def save_results(file_path, data, console):
    """
    Saves the reconnaissance results to a specified file.
    Supports JSON and plain text based on file extension.
    """
    try:
        # Ensure the directory exists
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if file_path.lower().endswith('.json'):
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=4)
            console.print(f"[green]Results saved to {file_path} (JSON).[/green]")
        elif file_path.lower().endswith('.txt'):
            with open(file_path, 'w') as f:
                f.write(json.dumps(data, indent=4)) # For simplicity, save JSON as text
            console.print(f"[green]Results saved to {file_path} (TXT).[/green]")
        else:
            console.print(f"[yellow]Unsupported output file format for {file_path}. Saving as JSON by default.[/yellow]")
            with open(f"{file_path}.json", 'w') as f:
                json.dump(data, f, indent=4)
            console.print(f"[green]Results saved to {file_path}.json (JSON).[/green]")

    except Exception as e:
        console.print(f"[bold red]Error saving results to {file_path}: {e}[/bold red]")

# Example usage (for testing this module directly)
if __name__ == "__main__":
    from rich.console import Console
    console = Console()
    test_data = {
        "target": "example.com",
        "module": "test",
        "results": ["item1", "item2"]
    }
    console.print("[bold green]Running standalone output_formatter.py for testing.[/bold green]")
    save_results("test_output.json", test_data, console)
    save_results("test_output.txt", test_data, console)
    save_results("test_output_no_ext", test_data, console)
