"""
Manual API scenario runner.

Run this script to exercise the API with realistic data. Useful for quick
exploration and manual testing of the full flow (create, list, get, update, close).

Start the API first in another terminal:
    uv run uvicorn app.main:app --reload

Then run:
    uv run python -m tests.manual_api_scenarios

Or from the project root:
    uv run python tests/manual_api_scenarios.py
"""

from pprint import pprint

import httpx

BASE_URL = "http://127.0.0.1:8000"


def run_scenarios() -> None:
    """Send a sequence of realistic requests to the API."""
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        print("1. Create ticket")
        r = client.post(
            "/tickets/",
            json={
                "title": "Fix broken button on the landing page",
                "description": "The primary button is not clickable.",
                "status": "open",
            },
        )
        r.raise_for_status()
        ticket = r.json()
        print(f"   Created: {ticket}")
        ticket_id = ticket["id"]

        print("\n2. Create another ticket")
        r = client.post(
            "/tickets/",
            json={
                "title": "Add auto complete to the search input",
                "description": "The search input should show auto complete suggestions as the user types.",
            },
        )
        r.raise_for_status()
        print(f"   Created: {r.json()['title']}")

        print("\n3. List all tickets")
        r = client.get("/tickets/")
        r.raise_for_status()
        tickets = r.json()
        print(f"   Found {len(tickets)} tickets")
        pprint(tickets)

        print(f"\n4. Get ticket {ticket_id}")
        r = client.get(f"/tickets/{ticket_id}")
        r.raise_for_status()
        print(f"   {r.json()}")

        print(f"\n5. Update ticket {ticket_id} (set stalled)")
        r = client.put(
            f"/tickets/{ticket_id}",
            json={
                "title": "Fix broken button on the landing page",
                "description": "The primary button is not clickable. It should be clickable.",
                "status": "stalled",
            },
        )
        r.raise_for_status()
        print(f"   Updated: {r.json()}")

        print(f"\n6. Close ticket {ticket_id}")
        r = client.patch(f"/tickets/{ticket_id}/close")
        r.raise_for_status()
        print(f"   Closed: {r.json()}")

        print("\nDone.")


if __name__ == "__main__":
    run_scenarios()
