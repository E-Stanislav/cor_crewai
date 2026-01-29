# Utils Module

File system utilities & configuration loading for DWH projects.

## OVERVIEW
Provides config.yaml loading, project validation, and file operations.

## WHERE TO LOOK
| Function | Purpose |
|-----------|---------|
| load_config() | Load config.yaml with error handling |
| get_project_list() | Return all project names |
| get_project_info() | Get project metadata by name |
| project_exists() | Check if project in config |
| is_path_valid() | Verify directory exists |
| get_project_files() | List files by extension |
| get_file_content() | Read file content |
| get_project_structure() | Get project tree structure |
| find_files_by_pattern() | Find files matching pattern |

## CONVENTIONS
- Use yaml.safe_load() for parsing
- Raise ValueError for invalid config
- FileNotFoundError for missing files
