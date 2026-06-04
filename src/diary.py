"""
Author:      Leonardo Andres Sandino Acosta
Project:     Project 2: Diary Entry Application
Date:        June 4, 2026
Class:       IT-566: Computer Scripting Techniques
Description: Lets users create dated diary entries saved as separate lines
             in a text file, and allows filtering and printing by date.
"""

from datetime import date, datetime
import os
import re

DIARY_FILE = "diary.txt"


def validate_date_string(date_string: str) -> date:
    """
    Validates a date string in mm/dd/yyyy format.
    
    Args:
        date_string (str): Date in 'mm/dd/yyyy' format.
        
    Returns:
        date: Validated datetime.date object.
        
    Raises:
        ValueError: If formatting or values are invalid.
    """
    if not re.match(r"^\d{2}/\d{2}/\d{4}$", date_string):
        raise ValueError("Invalid format. Use mm/dd/yyyy (e.g., 06/19/2026).")

    parts = date_string.split("/")
    month = int(parts[0])
    day = int(parts[1])
    year = int(parts[2])

    try:
        validated_date = date(year=year, month=month, day=day)
    except ValueError as e:
        raise ValueError(f"Invalid date values: {e}")

    if year < 1900 or year > 2100:
        raise ValueError("Year must be between 1900 and 2100.")

    return validated_date


def parse_search_query(query: str) -> str:
    """
    Parses and normalizes search queries (mm/dd/yyyy, mm/yyyy, or yyyy)
    into a standardized search prefix string (YYYY-MM-DD, YYYY-MM, or YYYY).
    
    Args:
        query (str): User-entered search string.
        
    Returns:
        str: Normalized date prefix.
        
    Raises:
        ValueError: If query format is unrecognized.
    """
    query = query.strip()
    # Check exact date: mm/dd/yyyy
    if re.match(r"^\d{2}/\d{2}/\d{4}$", query):
        parts = query.split("/")
        # Verify valid date values
        try:
            date(int(parts[2]), int(parts[0]), int(parts[1]))
        except ValueError as e:
            raise ValueError(f"Invalid search date: {e}")
        return f"{parts[2]}-{parts[0]}-{parts[1]}"

    # Check month/year: mm/yyyy
    if re.match(r"^\d{2}/\d{4}$", query):
        parts = query.split("/")
        month = int(parts[0])
        year = int(parts[1])
        if month < 1 or month > 12:
            raise ValueError("Month must be in range 1..12.")
        if year < 1900 or year > 2100:
            raise ValueError("Year must be between 1900 and 2100.")
        return f"{parts[1]}-{parts[0]}"

    # Check year: yyyy
    if re.match(r"^\d{4}$", query):
        year = int(query)
        if year < 1900 or year > 2100:
            raise ValueError("Year must be between 1900 and 2100.")
        return query

    raise ValueError(
        "Invalid search format. Use mm/dd/yyyy, mm/yyyy, or yyyy."
    )


def serialize_entry(entry_date: date, text: str) -> str:
    """
    Formats entry components into a single line for file storage.
    
    Args:
        entry_date (date): Date of the diary entry.
        text (str): Body content of the diary entry (multi-line supported).
        
    Returns:
        str: Serialized single line text.
    """
    # Replace actual newlines with escaped text to keep it on a single line
    escaped_text = text.replace("\n", "\\n")
    return f"{entry_date.strftime('%Y-%m-%d')} | {escaped_text}"


def deserialize_line(line: str) -> tuple[str, str]:
    """
    Parses a stored line back into date prefix and unescaped content.
    
    Args:
        line (str): A raw line from the diary file.
        
    Returns:
        tuple[str, str]: Normalized date string (YYYY-MM-DD) and unescaped text.
    """
    parts = line.strip().split(" | ", 1)
    if len(parts) < 2:
        # Fallback if line is corrupt or incorrectly formatted
        return "", line.strip()
    
    date_str, escaped_text = parts[0], parts[1]
    unescaped_text = escaped_text.replace("\\n", "\n")
    return date_str, unescaped_text


def save_entry(entry_date: date, text: str):
    """Appends a new entry to the diary text file."""
    serialized = serialize_entry(entry_date, text)
    with open(DIARY_FILE, "a", encoding="utf-8") as f:
        f.write(serialized + "\n")


def read_all_entries() -> list[tuple[str, str]]:
    """Reads all entries from the diary file."""
    if not os.path.exists(DIARY_FILE):
        return []
    
    entries = []
    with open(DIARY_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                entries.append(deserialize_line(line))
    return entries


def create_entry_flow():
    """Interactively guides the user through creating a diary entry."""
    print("\n--- Create Diary Entry ---")
    
    # 1. Prompt for Date
    while True:
        try:
            date_input = input("Enter Date (mm/dd/yyyy) [Leave blank for Today]: ").strip()
            if not date_input:
                entry_date = date.today()
                print(f"Selected: Today ({entry_date.strftime('%m/%d/%Y')})")
                break
            else:
                entry_date = validate_date_string(date_input)
                break
        except ValueError as e:
            print(f"Error: {e}\n")

    # 2. Prompt for Text Content (supports multi-line)
    print("\nEnter entry content. Press Enter on a blank line to save:")
    lines = []
    while True:
        try:
            line = input()
            if line == "":
                break
            lines.append(line)
        except KeyboardInterrupt:
            print("\nEntry cancelled.")
            return

    content = "\n".join(lines).strip()
    if not content:
        print("Empty entry. Not saved.")
        return

    # 3. Save
    save_entry(entry_date, content)
    print("Diary entry saved successfully.")


def filter_entries_flow():
    """Interactively guides the user through searching diary entries."""
    print("\n--- Filter/Search Entries ---")
    if not os.path.exists(DIARY_FILE) or os.path.getsize(DIARY_FILE) == 0:
        print("No diary entries found. Please create one first.")
        return

    while True:
        try:
            query = input("Enter date filter (mm/dd/yyyy, mm/yyyy, or yyyy): ").strip()
            normalized_query = parse_search_query(query)
            break
        except ValueError as e:
            print(f"Error: {e}\n")

    all_entries = read_all_entries()
    matching_entries = [
        (d_str, text) for d_str, text in all_entries if d_str.startswith(normalized_query)
    ]

    if not matching_entries:
        print(f"\nNo entries found matching '{query}'.")
        return

    print(f"\n=== Found {len(matching_entries)} entries matching '{query}' ===")
    for d_str, text in matching_entries:
        # Convert YYYY-MM-DD back to readable format for output
        dt_obj = datetime.strptime(d_str, "%Y-%m-%d")
        readable_date = dt_obj.strftime("%B %d, %Y (%A)")
        print(f"\nDate: {readable_date}")
        print("-" * 40)
        print(text)
        print("=" * 40)


def view_all_entries_flow():
    """Displays all entries stored in the diary."""
    print("\n--- All Diary Entries ---")
    entries = read_all_entries()
    if not entries:
        print("Your diary is currently empty.")
        return

    # Sort entries by date (newest first or oldest first; let's do oldest first)
    entries.sort(key=lambda x: x[0])
    
    print(f"\n=== Total Entries: {len(entries)} ===")
    for d_str, text in entries:
        dt_obj = datetime.strptime(d_str, "%Y-%m-%d")
        readable_date = dt_obj.strftime("%B %d, %Y (%A)")
        print(f"\nDate: {readable_date}")
        print("-" * 40)
        print(text)
        print("=" * 40)


def main():
    """Main CLI Menu loop."""
    while True:
        print("\n====================================")
        print("   📒 MY PERSONAL DIARY APPLICATION ")
        print("====================================")
        print("[1] Create dated diary entry")
        print("[2] Filter/print entries by date")
        print("[3] View all entries")
        print("[4] Exit")
        print("====================================")
        
        choice = input("Choose an option (1-4): ").strip()
        
        if choice == "1":
            create_entry_flow()
        elif choice == "2":
            filter_entries_flow()
        elif choice == "3":
            view_all_entries_flow()
        elif choice == "4":
            print("\nGoodbye!")
            break
        else:
            print("\nInvalid choice. Please enter 1, 2, 3, or 4.")


if __name__ == "__main__":
    main()
