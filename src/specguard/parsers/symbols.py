from __future__ import annotations

try:
    from tree_sitter import Language, Node, Parser
except ImportError:  # pragma: no cover - optional dependency
    Language = Parser = Node = None  # type: ignore[assignment,misc]

DEFINITION_TYPES = {
    "function_definition",
    "class_definition",
    "function_declaration",
    "class_declaration",
    "method_definition",
    "interface_declaration",
    "type_alias_declaration",
}
ANONYMOUS_FUNCTION_VALUE_TYPES = {"function_expression", "arrow_function"}

_LANGUAGE_CACHE: dict[str, object | None] = {}


def _language_for(extension: str):
    if extension in _LANGUAGE_CACHE:
        return _LANGUAGE_CACHE[extension]
    language = None
    try:
        if extension == ".py":
            import tree_sitter_python as ts_py

            language = Language(ts_py.language())
        elif extension in (".js", ".jsx", ".mjs", ".cjs"):
            import tree_sitter_javascript as ts_js

            language = Language(ts_js.language())
        elif extension == ".ts":
            import tree_sitter_typescript as ts_ts

            language = Language(ts_ts.language_typescript())
        elif extension == ".tsx":
            import tree_sitter_typescript as ts_ts

            language = Language(ts_ts.language_tsx())
    except ImportError:
        language = None
    _LANGUAGE_CACHE[extension] = language
    return language


def _definition_name_node(node: "Node") -> "Node | None":
    if node.type in DEFINITION_TYPES:
        return node.child_by_field_name("name")
    if node.type == "variable_declarator":
        value = node.child_by_field_name("value")
        if value is not None and value.type in ANONYMOUS_FUNCTION_VALUE_TYPES:
            return node.child_by_field_name("name")
    return None


def _collect_definitions(node: "Node", out: list[tuple[str, int, int]]) -> None:
    name_node = _definition_name_node(node)
    if name_node is not None:
        out.append((name_node.text.decode("utf-8", "replace"), node.start_point.row + 1, node.end_point.row + 1))
    for child in node.children:
        _collect_definitions(child, out)


def symbols_touching_lines(source: bytes, extension: str, touched_lines: set[int]) -> list[str] | None:
    if Parser is None:
        return None
    language = _language_for(extension)
    if language is None:
        return None
    try:
        tree = Parser(language).parse(source)
    except Exception:
        return None
    definitions: list[tuple[str, int, int]] = []
    _collect_definitions(tree.root_node, definitions)
    touched: list[str] = []
    for name, start, end in definitions:
        if name not in touched and any(start <= line <= end for line in touched_lines):
            touched.append(name)
    return touched
