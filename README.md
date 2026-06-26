# datasette-cell-template

A custom Datasette plugin that renders clickable links in table cells using configurable templates. Designed for `hnlog` to link IDs to external URLs.

## Table of Contents

- [Description](#description)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Development](#development)
- [License](#license)
- [Contributing](#contributing)

## Description

This plugin uses the `render_cell` hook in Datasette to modify how specific columns are displayed. It allows you to append clickable links to cell values based on templates.

Key features:
- **Template URLs**: Generate links based on cell values (e.g., `{id}`).
- **Type-based rendering**: Use different URL templates depending on the value of a "type" column (e.g., `story` vs `comment`).
- **Flexible Targeting**: Configure which columns to render the link in, and which column provides the ID value.
- **View Control**: Restrict rendering to specific views (e.g., only "table" or "row").

It was originally built to link `hnlog` item IDs to `westurner.github.io/hnlog`.

## Installation

This is designed as a local plugin. Point Datasette to the directory containing this plugin using the `--plugins-dir` argument:

```bash
datasette serve hnlog.sqlite --plugins-dir ./datasette_cell_template
```

## Configuration

Configure the plugin in your `metadata.yml` (or `metadata.json`).

### Example Configuration

```yaml
plugins:
  datasette-cell-template:
    # Text to display for the link
    link_text: "Open URL 🔗"
    
    # HTML attributes for the <a> tag
    link_attrs: 'target="_blank" rel="noopener noreferrer"'
    
    # Column(s) to render the link in
    # Note: The 'render_cell' hook is skipped for Primary Key columns in the default "table" view.
    # To see links in the table view, attach to a non-PK column (like "type").
    columns: ["type"]
    
    # Column used to resolve the {id} value in the URL template
    id_column: "id"
    
    # Column used to determine the template type (if using dictionary url_template)
    type_column: "type"
    
    # Restrict to specific views (optional)
    # views: ["table", "row"]
    
    # URL Templates
    # Can be a simple string or a dictionary mapping types to templates
    # url_template: "https://example.org/#{id}"
    # url_template: "/pages/example#{id}"
    url_template:
      default: "https://example.org/#{id}"
      story:   "https://example.org/#story-{id}"
      comment: "https://example.org/#comment-{id}"
```

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `link_text` | string | "Open URL" | The text content of the generated link. |
| `link_attrs` | string | `target="_blank" ...` | HTML attributes added to the link tag. |
| `columns` | list | `["id"]` | List of columns where the link should appear. |
| `id_column` | string/list | `"id"` | The column name to use as `{id}` in the URL. |
| `type_column` | string | `"type"` | The column name to check for type-based templates. |
| `url_template` | string/dict | - | A format string (e.g., `http://site/{id}`) or a dict of format strings keyed by type. |

## Usage

Once configured, navigate to your Datasette instance. The target columns in your table will now display the original value followed by the configured link.

For example, if configured for the `type` column using `id_column: "id"`, a row with `type="story"` and `id=123` will render the text "story" followed by a link to `.../#story-123`.

## Development

To set up the development environment, ensure you have `pytest` and `pytest-cov` installed.

1. **Install Dependencies**
   ```bash
   pip install pytest pytest-cov
   ```

2. **Run Tests**
   Execute the tests from the plugin directory:
   ```bash
   python -m pytest --cov=datasette_cell_template tests/
   ```

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.



## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Write tests to cover your changes.
4. Submit a pull request.
