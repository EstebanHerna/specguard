from pathlib import Path

from specguard.parsers.kiro_spec import load_spec, parse_requirements, parse_tasks

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_requirements():
    reqs = parse_requirements(FIXTURES / "requirements.md")
    assert len(reqs) == 2
    assert reqs[0].id == "1"
    assert "spec" in reqs[0].title.lower() or reqs[0].title
    assert len(reqs[0].criteria) == 2
    assert reqs[0].criteria[0].id == "1.1"


def test_parse_tasks():
    tasks = parse_tasks(FIXTURES / "tasks.md")
    assert len(tasks) == 3
    assert tasks[0].done is True
    assert tasks[0].requirement_refs == ["1.1", "1.2"]
    assert tasks[2].done is False


def test_heading_variants_recognized_in_order_with_fallback_title():
    reqs = parse_requirements(FIXTURES / "requirements_heading_variants.md")
    assert [r.id for r in reqs] == ["1", "2", "3"]
    assert reqs[0].title == "Encabezado nivel dos con dos puntos"
    assert reqs[1].title == "Titulo sin dos puntos"
    assert reqs[2].title == "Requirement 3"
    assert [len(r.criteria) for r in reqs] == [1, 1, 1]


def test_criteria_variants_confined_to_section():
    reqs = parse_requirements(FIXTURES / "requirements_criteria_variants.md")
    req1, req2 = reqs
    assert [c.id for c in req1.criteria] == ["1.1", "1.2", "1.3", "1.4"]
    assert req1.criteria[0].text.startswith("WHEN extra whitespace")
    assert req1.criteria[2].text.startswith("WHEN a criterion uses a dash")
    assert len(req2.criteria) == 1
    assert req2.criteria[0].id == "2.1"


def test_bilingual_story_and_empty_or_missing_sections_dont_break_continuity():
    reqs = parse_requirements(FIXTURES / "requirements_stories_empty_sections.md")
    assert reqs[0].user_story.startswith("Como usuario")
    assert reqs[1].criteria == []
    assert reqs[2].criteria == []
    assert len(reqs[3].criteria) == 2
    assert reqs[3].criteria[1].id == "4.2"


def test_task_nested_ids_and_states_with_invalid_lines_ignored():
    tasks = parse_tasks(FIXTURES / "tasks_nested_ids_states.md")
    assert [t.id for t in tasks] == ["8", "8.1", "8.1.2.3", "9"]
    assert [t.done for t in tasks] == [True, True, False, True]
    assert tasks[2].requirement_refs == ["1.6"]
    assert tasks[3].requirement_refs == ["2.1", "2.2"]


def test_load_spec_returns_empty_lists_for_missing_files(tmp_path):
    reqs, tasks = load_spec(tmp_path)
    assert reqs == []
    assert tasks == []


def test_public_api_smoke():
    reqs = parse_requirements(FIXTURES / "requirements.md")
    tasks = parse_tasks(FIXTURES / "tasks.md")
    loaded_reqs, loaded_tasks = load_spec(FIXTURES)
    assert loaded_reqs == reqs
    assert loaded_tasks == tasks


def test_heading_level_one_and_five_are_not_recognized(tmp_path):
    md = tmp_path / "requirements.md"
    md.write_text(
        "# Requirement 1: too shallow\n\n"
        "##### Requirement 2: too deep\n\n"
        "### Requirement 3: just right\n\n"
        "#### Acceptance Criteria\n\n"
        "1. WHEN parsed THEN it SHALL be the only requirement\n",
        encoding="utf-8",
    )
    reqs = parse_requirements(md)
    assert [r.id for r in reqs] == ["3"]


def test_unrecognized_bold_label_does_not_set_user_story(tmp_path):
    md = tmp_path / "requirements.md"
    md.write_text(
        "### Requirement 1: unknown label\n\n"
        "**Not A Recognized Label:** this must not become the user story\n\n"
        "#### Acceptance Criteria\n\n"
        "1. WHEN parsed THEN the user story SHALL stay empty\n",
        encoding="utf-8",
    )
    reqs = parse_requirements(md)
    assert reqs[0].user_story == ""
    assert len(reqs[0].criteria) == 1


def test_criterion_outside_section_is_not_captured(tmp_path):
    md = tmp_path / "requirements.md"
    md.write_text(
        "### Requirement 1: sin seccion aun\n\n"
        "1. WHEN this appears before Acceptance Criteria THEN it SHALL be ignored\n\n"
        "#### Acceptance Criteria\n\n"
        "1. WHEN this appears inside THEN it SHALL be the only criterion\n",
        encoding="utf-8",
    )
    reqs = parse_requirements(md)
    assert len(reqs[0].criteria) == 1
    assert reqs[0].criteria[0].text == "WHEN this appears inside THEN it SHALL be the only criterion"


def test_invalid_checkbox_and_non_numeric_id_are_ignored(tmp_path):
    md = tmp_path / "tasks.md"
    md.write_text(
        "- [?] 1 invalid checkbox marker\n"
        "- [ ] no-id-here task without a numeric id\n"
        "- [x] 2. valid task\n",
        encoding="utf-8",
    )
    tasks = parse_tasks(md)
    assert [t.id for t in tasks] == ["2"]
