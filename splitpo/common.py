"""Common utilities for po file processing."""

import sys
from pathlib import Path
from typing import List, Tuple


class PoEntry:
    """Represents a single po file entry."""
    def __init__(self):
        self.msgid = ""
        self.msgstr = ""
        self.comments = []
        self.references = []
        self.flags = []
        self.msgctxt = ""
        self.raw_lines = []
    
    def is_empty(self) -> bool:
        """Check if this is an empty entry (no msgid)."""
        return not self.msgid and not self.msgctxt
    
    def to_string(self) -> str:
        """Convert entry back to po format."""
        return '\n'.join(self.raw_lines)


def parse_po_file(file_path: str) -> Tuple[List[str], List[PoEntry]]:
    """Parse a po file and return header lines and entries."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    header_lines = []
    entries = []
    current_entry = None
    in_header = True
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Handle header (before first msgid)
        if in_header and not line.strip().startswith('msgid '):
            if line.strip() == '' and current_entry is None:
                header_lines.append(line)
                i += 1
                continue
            elif line.strip().startswith('#') or line.strip().startswith('"') or line.strip() == '':
                header_lines.append(line)
                i += 1
                continue
        
        # Start of new entry
        if line.strip().startswith('msgid '):
            in_header = False
            if current_entry is not None:
                entries.append(current_entry)
            current_entry = PoEntry()
            current_entry.raw_lines = []
        
        # Add line to current entry
        if current_entry is not None:
            current_entry.raw_lines.append(line)
            
            # Parse msgid
            if line.strip().startswith('msgid '):
                current_entry.msgid = line.strip()[6:].strip('"')
            # Parse msgstr
            elif line.strip().startswith('msgstr '):
                current_entry.msgstr = line.strip()[7:].strip('"')
            # Parse msgctxt
            elif line.strip().startswith('msgctxt '):
                current_entry.msgctxt = line.strip()[8:].strip('"')
        
        i += 1
    
    # Add the last entry
    if current_entry is not None:
        entries.append(current_entry)
    
    return header_lines, entries


def write_po_file(file_path: str, header_lines: List[str], entries: List[PoEntry]) -> None:
    """Write po file with header and entries."""
    with open(file_path, 'w', encoding='utf-8') as f:
        # Write header
        for line in header_lines:
            f.write(line + '\n')
        
        # Write entries
        for i, entry in enumerate(entries):
            if i > 0:  # Add blank line between entries
                f.write('\n')
            f.write(entry.to_string())
            if not entry.to_string().endswith('\n'):
                f.write('\n')