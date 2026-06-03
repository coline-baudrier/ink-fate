from backend.app.core.scene_result_parser import (
    build_fallback_scene_result,
    extract_json_object,
    parse_scene_result,
    remove_trailing_commas,
)


def test_extract_json_object_from_text():
    response = """
Here is the scene:
{
  "narration": []
}
"""

    assert extract_json_object(response) == '{\n  "narration": []\n}'


def test_remove_trailing_commas():
    json_text = """
{
  "narration": [],
  "dialogues": [],
}
"""

    cleaned = remove_trailing_commas(json_text)

    assert '"dialogues": []' in cleaned
    assert ",\n}" not in cleaned


def test_parse_scene_result_valid_json():
    response = """
{
  "narration": [],
  "dialogues": []
}
"""

    parsed = parse_scene_result(response)

    assert parsed["narration"] == []
    assert parsed["dialogues"] == []


def test_parse_scene_result_repairs_trailing_commas():
    response = """
{
  "narration": [],
  "dialogues": [],
}
"""

    parsed = parse_scene_result(response)

    assert parsed["narration"] == []
    assert parsed["dialogues"] == []


def test_parse_scene_result_returns_fallback_on_invalid_json():
    parsed = parse_scene_result(
        "{ invalid json"
    )

    assert parsed == build_fallback_scene_result()