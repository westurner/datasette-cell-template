"""
datasette_cell_template.__init__
"""
from datasette import hookimpl
from markupsafe import Markup
import os

DEFAULT_COLUMNS = ["id"]
DEFAULT_ID_COLUMN = "id"
DEFAULT_URL_TEMPLATE = "https://example.org/path/#{id}"
DEFAULT_TYPE_COLUMN = "type"
DEFAULT_LINK_TEXT = "Open URL"
DEFAULT_LINK_ATTRS = 'target="_blank" rel="noopener noreferrer"'
DEFAULT_FALLBACK_KEY = "default"


@hookimpl
def extra_template_paths(datasette):
    return [
        os.path.join(os.path.dirname(__file__), "templates")
    ]


@hookimpl
def render_cell(
    row,
    value,
    column,
    table,
    database,
    datasette,
    view_name=None,
):
    if value is None:
        return None

    config = {}
    if datasette:
        config = (
            datasette.plugin_config(
                "datasette-cell-template", database=database, table=table
            )
            or {}
        )

    # Check view restrictions if configured
    configured_views = config.get("views")
    if configured_views and view_name:
        if view_name not in configured_views:
            return None

    configured_columns = config.get("columns", DEFAULT_COLUMNS)
    if column not in configured_columns:
        return None

    # Resolve the ID value
    id_column = config.get("id_column", DEFAULT_ID_COLUMN)
    id_value = value  # Default to current cell value

    if row:
        try:
            if isinstance(id_column, str):
                id_value = row[id_column]
            elif isinstance(id_column, list):
                # Try to find the first matching column in the row
                for col in id_column:
                    try:
                        id_value = row[col]
                        break
                    except (KeyError, IndexError):
                        continue
        except (KeyError, IndexError, TypeError):
            # Fallback to value if lookup fails
            pass

    url_template = config.get("url_template", DEFAULT_URL_TEMPLATE)

    # Handle dictionary configuration for type-based templates
    if isinstance(url_template, dict):
        # Get the column name to determine type, defaulting to "type"
        type_column = config.get("type_column", DEFAULT_TYPE_COLUMN)

        # Safely check for column presence
        has_type_column = False
        if row:
            try:
                # Some row types (sqlite3.Row) support 'in', others might not
                if hasattr(row, "keys"):
                    has_type_column = type_column in row.keys()
                else:
                    # Fallback for objects that support __getitem__ but maybe not keys()
                    _ = row[type_column]
                    has_type_column = True
            except (AttributeError, TypeError, KeyError, IndexError):
                has_type_column = False

        # Default to "default" if type column not present or null
        item_type = DEFAULT_FALLBACK_KEY
        if has_type_column:
            try:
                val = row[type_column]
                if val is not None:
                    item_type = str(val)
            except (KeyError, IndexError, TypeError):
                pass

        # Lookup with fallbacks: type -> default -> first item
        template_str = url_template.get(item_type)
        if not template_str:
            template_str = url_template.get(DEFAULT_FALLBACK_KEY)
        if not template_str:
            # Fallback to the first value or a safe default if dict is empty
            template_str = (
                next(iter(url_template.values()))
                if url_template
                else DEFAULT_URL_TEMPLATE
            )

        url = template_str.format(id=id_value)
    else:
        # String configuration
        url = url_template.format(id=id_value)

    link_text = config.get("link_text", DEFAULT_LINK_TEXT)
    link_attrs = config.get("link_attrs", DEFAULT_LINK_ATTRS)
    return Markup(f'{value}<br><a href="{url}" {link_attrs}>{link_text}</a>')
