"""Minimal check that the model endpoint, key, and access all work."""
from airlock.llm_client import complete


def main():
    print("Calling the model (confirms endpoint + key + account access)...")
    reply = complete([{"role": "user", "content": "Reply with exactly: AIRLOCK OK"}])
    print("\nSUCCESS — model replied:")
    print(reply)


if __name__ == "__main__":
    main()