"""Test command line interface."""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent.parent))

from splitpo.split import main as split_main
from splitpo.join import main as join_main
from splitpo.common import parse_po_file


class TestSplitCLI:
    """Test split command line interface."""

    def test_split_help(self, capsys):
        """Test split help output."""
        with pytest.raises(SystemExit):
            sys.argv = ["split", "--help"]
            split_main()
        
        captured = capsys.readouterr()
        assert "Split a .po file into chunks" in captured.out
        assert "--output-dir" in captured.out
        assert "--entries" in captured.out

    def test_split_missing_file(self, capsys):
        """Test split with missing input file."""
        with pytest.raises(SystemExit):
            sys.argv = ["split", "nonexistent.po"]
            split_main()
        
        captured = capsys.readouterr()
        assert "does not exist" in captured.out

    def test_split_default_options(self, tmp_path):
        """Test split with default options."""
        # Create a test po file
        test_po = tmp_path / "test.po"
        test_po.write_text("""# Test po file
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "Hello"
msgstr "こんにちは"

msgid "World"
msgstr "世界"
""")
        
        # Run split with default options
        sys.argv = ["split", str(test_po)]
        split_main()
        
        # Check that splitted directory was created
        splitted_dir = Path("./splitted")
        assert splitted_dir.exists()
        
        # Check that split files were created
        split_files = list(splitted_dir.glob("test_part_*.po"))
        assert len(split_files) == 1
        assert split_files[0].name == "test_part_000.po"
        
        # Clean up
        shutil.rmtree(splitted_dir)

    def test_split_custom_options(self, tmp_path):
        """Test split with custom options."""
        # Create a test po file with 5 entries
        test_po = tmp_path / "test.po"
        test_po.write_text("""# Test po file
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "Entry 1"
msgstr "エントリ 1"

msgid "Entry 2"
msgstr "エントリ 2"

msgid "Entry 3"
msgstr "エントリ 3"

msgid "Entry 4"
msgstr "エントリ 4"

msgid "Entry 5"
msgstr "エントリ 5"
""")
        
        output_dir = tmp_path / "custom_output"
        
        # Run split with custom options
        sys.argv = ["split", str(test_po), "--output-dir", str(output_dir), "--entries", "2"]
        split_main()
        
        # Check that custom output directory was created
        assert output_dir.exists()
        
        # Check that split files were created (5 entries / 2 per file = 3 files)
        split_files = sorted(output_dir.glob("test_part_*.po"))
        assert len(split_files) == 3
        assert split_files[0].name == "test_part_000.po"
        assert split_files[1].name == "test_part_001.po"
        assert split_files[2].name == "test_part_002.po"
        
        # Check entry counts
        _, entries_0 = parse_po_file(str(split_files[0]))
        _, entries_1 = parse_po_file(str(split_files[1]))
        _, entries_2 = parse_po_file(str(split_files[2]))
        
        valid_entries_0 = [e for e in entries_0 if not e.is_empty()]
        valid_entries_1 = [e for e in entries_1 if not e.is_empty()]
        valid_entries_2 = [e for e in entries_2 if not e.is_empty()]
        
        assert len(valid_entries_0) == 2
        assert len(valid_entries_1) == 2
        assert len(valid_entries_2) == 1


class TestJoinCLI:
    """Test join command line interface."""

    def test_join_help(self, capsys):
        """Test join help output."""
        with pytest.raises(SystemExit):
            sys.argv = ["join", "--help"]
            join_main()
        
        captured = capsys.readouterr()
        assert "Join split .po files" in captured.out
        assert "--output" in captured.out

    def test_join_missing_output(self, capsys):
        """Test join without output option."""
        with pytest.raises(SystemExit):
            sys.argv = ["join", "test.po"]
            join_main()
        
        captured = capsys.readouterr()
        assert "required" in captured.err

    def test_join_no_files(self, capsys, tmp_path):
        """Test join with no input files."""
        output_file = tmp_path / "output.po"
        
        with pytest.raises(SystemExit):
            sys.argv = ["join", "--output", str(output_file)]
            join_main()
        
        captured = capsys.readouterr()
        assert "required: input_files" in captured.err

    def test_join_basic(self, tmp_path):
        """Test basic join functionality."""
        # Create two test po files
        part1 = tmp_path / "test_part_000.po"
        part1.write_text("""# Test po file
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "Hello"
msgstr "こんにちは"
""")
        
        part2 = tmp_path / "test_part_001.po"
        part2.write_text("""# Test po file
msgid ""
msgstr ""
"Content-Type: text/plain; charset=UTF-8\\n"

msgid "World"
msgstr "世界"
""")
        
        output_file = tmp_path / "joined.po"
        
        # Run join
        sys.argv = ["join", str(part1), str(part2), "--output", str(output_file)]
        join_main()
        
        # Check that output file was created
        assert output_file.exists()
        
        # Check that it contains both entries
        _, entries = parse_po_file(str(output_file))
        valid_entries = [e for e in entries if not e.is_empty()]
        assert len(valid_entries) == 2
        
        # Check entry content
        assert valid_entries[0].msgid == "Hello"
        assert valid_entries[0].msgstr == "こんにちは"
        assert valid_entries[1].msgid == "World"
        assert valid_entries[1].msgstr == "世界"