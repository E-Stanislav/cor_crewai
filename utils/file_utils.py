import os
import yaml
from typing import Dict, List, Optional
from pathlib import Path


def load_config(config_path: str = "config.yaml") -> Dict:
    """Загружает конфигурацию из YAML файла.

    Args:
        config_path: Путь к конфигурационному файлу.

    Returns:
        Словарь с конфигурацией.

    Raises:
        FileNotFoundError: Если файл конфигурации не найден.
        yaml.YAMLError: Если файл содержит ошибки YAML.
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Конфигурационный файл не найден: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    return config


def get_project_list(config_path: str = "config.yaml") -> List[str]:
    """Возвращает список названий всех проектов из конфигурации.

    Args:
        config_path: Путь к конфигурационному файлу.

    Returns:
        Список названий проектов.
    """
    config = load_config(config_path)
    return [project["name"] for project in config.get("projects", [])]


def get_project_info(project_name: str, config_path: str = "config.yaml") -> Optional[Dict]:
    """Возвращает информацию о конкретном проекте.

    Args:
        project_name: Название проекта.
        config_path: Путь к конфигурационному файлу.

    Returns:
        Словарь с информацией о проекте или None, если проект не найден.
    """
    config = load_config(config_path)
    
    for project in config.get("projects", []):
        if project["name"] == project_name:
            return project
    
    return None


def project_exists(project_name: str, config_path: str = "config.yaml") -> bool:
    """Проверяет, существует ли проект в конфигурации.

    Args:
        project_name: Название проекта.
        config_path: Путь к конфигурационному файлу.

    Returns:
        True, если проект существует, иначе False.
    """
    return get_project_info(project_name, config_path) is not None


def is_path_valid(path: str) -> bool:
    """Проверяет, существует ли путь в файловой системе.

    Args:
        path: Путь к директории.

    Returns:
        True, если путь существует и является директорией, иначе False.
    """
    return os.path.exists(path) and os.path.isdir(path)


def get_project_files(project_path: str, extensions: Optional[List[str]] = None) -> List[str]:
    """Возвращает список файлов проекта с указанными расширениями.

    Args:
        project_path: Путь к проекту.
        extensions: Список расширений файлов (например, [".py", ".sql"]). 
                   Если None, возвращает все файлы.

    Returns:
        Список путей к файлам.
    """
    if not is_path_valid(project_path):
        raise ValueError(f"Путь не существует или не является директорией: {project_path}")
    
    files = []
    
    for root, _, filenames in os.walk(project_path):
        for filename in filenames:
            if extensions is None or any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    
    return files


def get_file_content(file_path: str, max_lines: int = 1000) -> str:
    """Возвращает содержимое файла.

    Args:
        file_path: Путь к файлу.
        max_lines: Максимальное количество строк для чтения.

    Returns:
        Содержимое файла в виде строки.

    Raises:
        FileNotFoundError: Если файл не найден.
        UnicodeDecodeError: Если файл не может быть прочитан как текст.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл не найден: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = []
            for i, line in enumerate(f):
                if i >= max_lines:
                    break
                lines.append(line)
            return "".join(lines)
    except UnicodeDecodeError:
        raise ValueError(f"Не удалось прочитать файл как текст: {file_path}")


def get_project_structure(project_path: str, max_depth: int = 3) -> Dict:
    """Возвращает структуру проекта в виде древовидной структуры.

    Args:
        project_path: Путь к проекту.
        max_depth: Максимальная глубина просмотра.

    Returns:
        Словарь с древовидной структурой проекта.
    """
    if not is_path_valid(project_path):
        raise ValueError(f"Путь не существует или не является директорией: {project_path}")
    
    def build_tree(path: str, depth: int) -> Dict:
        if depth > max_depth:
            return {}
        
        result: Dict = {"name": os.path.basename(path), "type": "dir" if os.path.isdir(path) else "file"}
        
        if os.path.isdir(path):
            children = []
            try:
                for item in sorted(os.listdir(path)):
                    item_path = os.path.join(path, item)
                    children.append(build_tree(item_path, depth + 1))
            except PermissionError:
                children = [{"name": "Access denied", "type": "error"}]
            result["children"] = children
        
        return result
    
    return build_tree(project_path, 0)


def find_files_by_pattern(project_path: str, pattern: str) -> List[str]:
    """Ищет файлы по шаблону имени.

    Args:
        project_path: Путь к проекту.
        pattern: Шаблон для поиска (используется fnmatch).

    Returns:
        Список путей к файлам, соответствующим шаблону.
    """
    from fnmatch import fnmatch
    
    if not is_path_valid(project_path):
        raise ValueError(f"Путь не существует или не является директорией: {project_path}")
    
    matches = []
    
    for root, _, filenames in os.walk(project_path):
        for filename in filenames:
            if fnmatch(filename, pattern):
                matches.append(os.path.join(root, filename))
    
    return matches
