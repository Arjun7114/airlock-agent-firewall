"""Run the triage agent over all clean sample tickets and print a summary."""
from rich.console import Console
from rich.table import Table

from demo_agent.data_loader import load_tickets
from demo_agent.tools import TicketStore
from demo_agent.agent import triage_ticket

console = Console()


def main():
    tickets = load_tickets()
    store = TicketStore(tickets)

    for ticket in tickets:
        console.print(f"\n[bold cyan]Triaging {ticket.id}[/bold cyan] — {ticket.subject}")
        triage_ticket(store, ticket, verbose=True)

    table = Table(title="Triage summary")
    table.add_column("Ticket", style="cyan")
    table.add_column("Subject")
    table.add_column("Category")
    table.add_column("Priority")
    table.add_column("Final status")
    for t in store.tickets.values():
        table.add_row(
            t.id,
            t.subject[:32],
            t.category.value if t.category else "-",
            t.priority.value if t.priority else "-",
            t.status.value,
        )
    console.print()
    console.print(table)
    console.print(f"\nTotal actions taken: {len(store.action_log)}")
    console.print(f"[bold]Messages actually sent: {len(store.sent_messages)}[/bold]  "
                  "(should be 0 on clean tickets)")


if __name__ == "__main__":
    main()