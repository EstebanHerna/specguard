from specguard.parsers.git_diff import enhance_symbols_with_treesitter
from specguard.models import FileChange, Hunk
from specguard.parsers.symbols import symbols_touching_lines

PY_SOURCE = b"""def untouched():
    pass


def touched(x):
    return x + 1


class Widget:
    def render(self):
        return "widget"
"""

JS_SOURCE = b"""function untouched() { return 0; }

function touched(x) { return x + 1; }

class Widget {
  render() { return "widget"; }
}

const arrowTouched = (x) => x + 1;
"""

TS_SOURCE = b"""interface Untouched { a: number; }

interface Touched { b: string; }

class Service {
  method(): void {}
}
"""


def test_python_symbol_touched_by_line_is_detected():
    result = symbols_touching_lines(PY_SOURCE, ".py", {5})
    assert result == ["touched"]


def test_python_untouched_symbol_is_excluded():
    result = symbols_touching_lines(PY_SOURCE, ".py", {1})
    assert result == ["untouched"]


def test_python_class_method_touched():
    result = symbols_touching_lines(PY_SOURCE, ".py", {10})
    assert "render" in result


def test_javascript_function_class_and_arrow_are_detected():
    assert symbols_touching_lines(JS_SOURCE, ".js", {3}) == ["touched"]
    # Line 6 is both inside Widget's body and is the render method itself -
    # reporting both the containing class and the specific method touched
    # is the more precise (not incorrect) signal.
    assert symbols_touching_lines(JS_SOURCE, ".js", {6}) == ["Widget", "render"]
    assert symbols_touching_lines(JS_SOURCE, ".js", {9}) == ["arrowTouched"]


def test_typescript_interface_and_class_are_detected():
    assert symbols_touching_lines(TS_SOURCE, ".ts", {3}) == ["Touched"]
    assert symbols_touching_lines(TS_SOURCE, ".ts", {6}) == ["Service", "method"]


def test_no_overlapping_lines_returns_empty_list_not_none():
    result = symbols_touching_lines(PY_SOURCE, ".py", {200})
    assert result == []


def test_unsupported_extension_returns_none_for_regex_fallback():
    result = symbols_touching_lines(b"puts 'hello'", ".rb", {1})
    assert result is None


def test_enhance_symbols_reads_file_and_overrides_regex_result(tmp_path):
    py_file = tmp_path / "module.py"
    py_file.write_text(PY_SOURCE.decode("utf-8"), encoding="utf-8")
    change = FileChange(
        path="module.py",
        symbols=["stale_regex_guess"],
        hunks=[Hunk(header="", added=["def touched(x):"], added_lines=[5])],
    )
    enhance_symbols_with_treesitter([change], repo=tmp_path)
    assert change.symbols == ["touched"]


def test_enhance_symbols_keeps_regex_fallback_for_unsupported_extension(tmp_path):
    rb_file = tmp_path / "module.rb"
    rb_file.write_text("def touched\nend\n", encoding="utf-8")
    change = FileChange(
        path="module.rb",
        symbols=["touched"],
        hunks=[Hunk(header="", added=["def touched"], added_lines=[1])],
    )
    enhance_symbols_with_treesitter([change], repo=tmp_path)
    assert change.symbols == ["touched"]


def test_enhance_symbols_skips_deleted_files(tmp_path):
    change = FileChange(path="gone.py", status="deleted", symbols=["old_symbol"])
    enhance_symbols_with_treesitter([change], repo=tmp_path)
    assert change.symbols == ["old_symbol"]


def test_enhance_symbols_skips_missing_file_on_disk(tmp_path):
    change = FileChange(
        path="does_not_exist.py",
        symbols=["regex_guess"],
        hunks=[Hunk(header="", added=["def x():"], added_lines=[1])],
    )
    enhance_symbols_with_treesitter([change], repo=tmp_path)
    assert change.symbols == ["regex_guess"]


def test_enhance_symbols_refuses_absolute_path(tmp_path):
    outside = tmp_path.parent / "outside_secret.py"
    outside.write_text("def secret():\n    pass\n", encoding="utf-8")
    change = FileChange(
        path=str(outside),
        symbols=["regex_guess"],
        hunks=[Hunk(header="", added=["def secret():"], added_lines=[1])],
    )
    enhance_symbols_with_treesitter([change], repo=tmp_path)
    assert change.symbols == ["regex_guess"]
    outside.unlink()


def test_enhance_symbols_refuses_parent_traversal(tmp_path):
    repo_dir = tmp_path / "repo"
    repo_dir.mkdir()
    outside = tmp_path / "outside_secret.py"
    outside.write_text("def secret():\n    pass\n", encoding="utf-8")
    change = FileChange(
        path="../outside_secret.py",
        symbols=["regex_guess"],
        hunks=[Hunk(header="", added=["def secret():"], added_lines=[1])],
    )
    enhance_symbols_with_treesitter([change], repo=repo_dir)
    assert change.symbols == ["regex_guess"]
    outside.unlink()
