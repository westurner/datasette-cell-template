from unittest.mock import Mock
import datasette_cell_template as plugin


def test_extra_template_paths():
    datasette = Mock()
    paths = plugin.extra_template_paths(datasette)
    assert len(paths) == 1
    assert paths[0].endswith("templates")


def test_id_column_list_behavior():
    value = 123
    # Case 1: First column matches
    row = {"AltId": 999, "id": 888}
    mock_datasette = Mock()
    mock_datasette.plugin_config.return_value = {
        "id_column": ["AltId", "id"],
        "url_template": "https://example.com/{id}",
    }

    # Should use AltId (999)
    result = plugin.render_cell(row, value, "id", "items", "db", mock_datasette)
    assert "https://example.com/999" in str(result)

    # Case 2: First column missing, second matches
    mock_datasette.plugin_config.return_value = {
        "id_column": ["MissingCol", "id"],
        "url_template": "https://example.com/{id}",
    }
    result = plugin.render_cell(row, value, "id", "items", "db", mock_datasette)
    assert "https://example.com/888" in str(result)

    # Case 3: All missing (Fallback to value)
    mock_datasette.plugin_config.return_value = {
        "id_column": ["Missing1", "Missing2"],
        "url_template": "https://example.com/{id}",
    }
    result = plugin.render_cell(row, value, "id", "items", "db", mock_datasette)
    assert f"https://example.com/{value}" in str(result)


class DictLikeRow:
    def __init__(self, data):
        self.data = data

    def __getitem__(self, key):
        return self.data[key]

    # No keys() method


class BrokenRow:
    def __getitem__(self, key):
        raise TypeError("Broken")


class KeysOkButGetitemRaises:
    """Row that reports column via keys() but raises on __getitem__ access."""

    def __init__(self, keys):
        self._keys = keys

    def keys(self):
        return self._keys

    def __getitem__(self, key):
        raise TypeError("access denied")


def test_row_type_detection_edge_cases():
    value = 123
    mock_datasette = Mock()
    base_config = {
        "url_template": {
            "story": "https://story.com/{id}",
            "default": "https://default.com/{id}",
        },
        "type_column": "type",
    }
    mock_datasette.plugin_config.return_value = base_config

    # Case 1: Row without keys() but with __getitem__ (like some proxies)
    row = DictLikeRow({"type": "story", "id": 123})
    result = plugin.render_cell(row, value, "id", "items", "db", mock_datasette)
    assert "https://story.com/123" in str(result)

    # Case 2: Row where accessing type_column raises KeyError
    row_missing_type = DictLikeRow({"id": 123})  # "type" missing
    # Should raise KeyError inside try/except block and default to "default"
    result = plugin.render_cell(
        row_missing_type, value, "id", "items", "db", mock_datasette
    )
    assert "https://default.com/123" in str(result)

    # Case 3: Row where accessing type_column raises TypeError
    row_broken = BrokenRow()
    result = plugin.render_cell(row_broken, value, "id", "items", "db", mock_datasette)
    assert "https://default.com/123" in str(result)


def test_type_column_val_access_raises(monkeypatch):
    """Lines 104-105: has_type_column=True but row[type_column] raises on value read."""
    value = 42
    mock_datasette = Mock()
    mock_datasette.plugin_config.return_value = {
        "url_template": {
            "default": "https://default.com/{id}",
        },
        "type_column": "type",
    }
    # keys() says "type" exists, but __getitem__ raises -> except branch (104-105) hit
    row = KeysOkButGetitemRaises(["type", "id"])
    result = plugin.render_cell(row, value, "id", "items", "db", mock_datasette)
    assert "https://default.com/42" in str(result)


def test_url_template_dict_no_default_key():
    """Line 113: dict url_template has no 'default' key, falls back to first value."""
    value = 99
    mock_datasette = Mock()
    mock_datasette.plugin_config.return_value = {
        "url_template": {
            "other_type": "https://other.com/{id}",
        },
        "type_column": "type",
    }
    # item_type will be "default" (DEFAULT_FALLBACK_KEY) since type column is absent;
    # neither "default" nor any other match exists -> line 113 fires, uses first value.
    row = {"id": 99}
    result = plugin.render_cell(row, value, "id", "items", "db", mock_datasette)
    assert "https://other.com/99" in str(result)
