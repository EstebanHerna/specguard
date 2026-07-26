from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from specguard.parsers.kiro_spec import parse_requirements, parse_tasks

# Each example overwrites and immediately reads back the same tmp_path file,
# so reusing it across examples (instead of a fresh dir per example) is safe.
PROPERTY_SETTINGS = settings(
    max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture]
)

TEXT_ALPHABET = st.characters(whitelist_categories=("Ll", "Lu", "Nd"), whitelist_characters=" _-")
SAFE_TEXT = st.text(alphabet=TEXT_ALPHABET, min_size=0, max_size=20).map(lambda s: s.strip())
NONEMPTY_TEXT = SAFE_TEXT.filter(lambda s: s != "")


@st.composite
def requirement_block(draw):
    level = draw(st.sampled_from(["##", "###", "####"]))
    lang = draw(st.sampled_from(["Requirement", "Requisito"]))
    req_id = draw(st.integers(min_value=1, max_value=9999))
    title = draw(SAFE_TEXT)
    has_colon = draw(st.booleans())
    if title:
        header = f"{level} {lang} {req_id}{': ' if has_colon else ' '}{title}"
    else:
        header = f"{level} {lang} {req_id}"
    filler = draw(st.lists(NONEMPTY_TEXT, max_size=3))
    expected_title = title if title else f"Requirement {req_id}"
    return str(req_id), expected_title, [header, *filler]


@given(blocks=st.lists(requirement_block(), min_size=0, max_size=8))
@PROPERTY_SETTINGS
def test_property_1_requirement_recognition_order_and_isolation(tmp_path, blocks):
    # Feature: specguard-core, Property 1: Reconocimiento, orden y aislamiento de requisitos
    lines = [line for _, _, block_lines in blocks for line in block_lines]
    md = tmp_path / "requirements.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = parse_requirements(md)
    assert [r.id for r in result] == [b[0] for b in blocks]
    assert [r.title for r in result] == [b[1] for b in blocks]


@st.composite
def criterion_line(draw):
    marker = draw(st.sampled_from(["1.", "2)", "-", "*"]))
    pad = draw(st.sampled_from(["", "  "]))
    text = draw(NONEMPTY_TEXT)
    return f"{marker}{pad} {text}", text


@st.composite
def requirement_with_criteria_state(draw):
    req_id = draw(st.integers(min_value=1, max_value=9999))
    section_state = draw(st.sampled_from(["populated", "empty", "absent"]))
    decoys = draw(st.lists(criterion_line(), max_size=2))
    lines = [f"### Requirement {req_id}"] + [line for line, _ in decoys]
    expected: list[str] = []
    if section_state in ("populated", "empty"):
        lines.append("#### Acceptance Criteria")
        if section_state == "populated":
            entries = draw(st.lists(criterion_line(), min_size=1, max_size=5))
            lines.extend(line for line, _ in entries)
            expected = [text for _, text in entries]
    return str(req_id), expected, lines


@given(reqs=st.lists(requirement_with_criteria_state(), min_size=1, max_size=6))
@PROPERTY_SETTINGS
def test_property_2_criteria_confined_to_section(tmp_path, reqs):
    # Feature: specguard-core, Property 2: Criterios confinados a su seccion
    lines = [line for _, _, block_lines in reqs for line in block_lines]
    md = tmp_path / "requirements.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = parse_requirements(md)
    assert len(result) == len(reqs)
    for parsed, (req_id, expected, _) in zip(result, reqs):
        assert parsed.id == req_id
        assert [c.text for c in parsed.criteria] == expected
        assert [c.id for c in parsed.criteria] == [f"{req_id}.{i + 1}" for i in range(len(expected))]


@st.composite
def story_block(draw):
    req_id = draw(st.integers(min_value=1, max_value=9999))
    lines = [f"### Requirement {req_id}"]
    decoy_labels = ["Not A Label", "Nota", "Design Note", "Etiqueta Falsa"]
    for _ in range(draw(st.integers(min_value=0, max_value=2))):
        label = draw(st.sampled_from(decoy_labels))
        lines.append(f"**{label}:** {draw(NONEMPTY_TEXT)}")
    label = draw(st.sampled_from(["User Story", "Historia de Usuario"]))
    has_colon = draw(st.booleans())
    story_text = draw(NONEMPTY_TEXT)
    lines.append(f"**{label}{':' if has_colon else ''}** {story_text}")
    if draw(st.booleans()):
        label2 = draw(st.sampled_from(["User Story", "Historia de Usuario"]))
        lines.append(f"**{label2}:** {draw(NONEMPTY_TEXT)}")
    return str(req_id), story_text, lines


@given(bodies=st.lists(story_block(), min_size=1, max_size=5))
@PROPERTY_SETTINGS
def test_property_3_bilingual_user_story_extraction(tmp_path, bodies):
    # Feature: specguard-core, Property 3: Extraccion bilingue de historia de usuario
    lines = [line for _, _, block_lines in bodies for line in block_lines]
    md = tmp_path / "requirements.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = parse_requirements(md)
    assert [r.user_story for r in result] == [expected for _, expected, _ in bodies]


@st.composite
def nested_id(draw):
    depth = draw(st.integers(min_value=1, max_value=4))
    segments = draw(st.lists(st.integers(min_value=0, max_value=99), min_size=depth, max_size=depth))
    return ".".join(str(s) for s in segments)


@st.composite
def task_block(draw):
    task_id = draw(nested_id())
    state = draw(st.sampled_from([" ", "x", "X"]))
    text = draw(NONEMPTY_TEXT)
    lines = [f"- [{state}] {task_id}. {text}"]
    refs: list[str] = []
    if draw(st.booleans()):
        refs = draw(st.lists(nested_id(), min_size=1, max_size=3))
        lines.append(f"  - _Requirements: {', '.join(refs)}_")
    return task_id, state.lower() == "x", refs, lines


@given(tasks=st.lists(task_block(), min_size=1, max_size=8))
@PROPERTY_SETTINGS
def test_property_4_task_identity_state_and_order(tmp_path, tasks):
    # Feature: specguard-core, Property 4: Identidad, estado y orden de tareas
    lines = [line for _, _, _, block_lines in tasks for line in block_lines]
    md = tmp_path / "tasks.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    result = parse_tasks(md)
    assert [t.id for t in result] == [tid for tid, _, _, _ in tasks]
    assert [t.done for t in result] == [done for _, done, _, _ in tasks]
    assert [t.requirement_refs for t in result] == [refs for _, _, refs, _ in tasks]
