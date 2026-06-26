from unittest.mock import Mock, MagicMock
import datasette_cell_template as plugin
import pytest

def test_reproduce_items_table_view():
    # Setup inputs as described in the scenario
    value = 123456
    column = "id"
    table = "items"
    database = "hnlog"
    # view_name would be "table" in table view
    view_name = "table"
    
    # Mock row to behave like sqlite3.Row or dict
    # In table view, it might not contain 'type' if it wasn't selected
    # but the id is being rendered.
    row = {"id": 123456, "type": "story", "title": "Something"}
    
    # Mock Datasette config to match hnlog.sqlite.meta.yml
    mock_datasette = Mock()
    config = {
        "link_text": "hnlog 🔗",
        "type_column": "type",
        "views": ["table", "row"],
        "url_template": {
            "story": "https://westurner.github.io/hnlog/#story-{id}",
            "comment": "https://westurner.github.io/hnlog/#comment-{id}",
            "default": "https://example.org/path/#{id}" # Fallback
        }
    }
    
    def get_config(name, database=None, table=None):
        if name == "datasette-cell-template" and database == "hnlog" and table == "items":
            return config
        return {}
    
    mock_datasette.plugin_config.side_effect = get_config

    # Execute
    result = plugin.render_cell(
        row, value, column, table, database, mock_datasette, view_name=view_name
    )
    
    # Verify
    print(f"Result: {result}")
    assert result is not None, "Should render for table view"
    assert "href" in str(result)
    assert "hnlog 🔗" in str(result)

def test_reproduce_items_table_view_missing_type_column():
    # Scenario: 'type' column is NOT in the row (e.g. not selected in query)
    value = 123456
    row = {"id": 123456, "title": "Something"} # No type
    
    mock_datasette = Mock()
    config = {
        "url_template": {
            "story": "https://story.com/{id}",
            "default": "https://default.com/{id}"
        }
    }
    mock_datasette.plugin_config.return_value = config
    
    result = plugin.render_cell(
        row, value, "id", "items", "hnlog", mock_datasette, view_name="table"
    )
    
    assert result is not None
    assert "https://default.com" in str(result)

if __name__ == "__main__":
    test_reproduce_items_table_view()
    test_reproduce_items_table_view_missing_type_column()
    print("Reproduction tests passed!")
