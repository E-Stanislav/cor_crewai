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


def scan_project_structure(project_path: str, max_depth: int = 2, max_files: int = 50) -> str:
    """Сканирует структуру проекта и возвращает текстовое представление.

    Args:
        project_path: Путь к проекту.
        max_depth: Максимальная глубина сканирования.
        max_files: Максимальное количество файлов для отображения.

    Returns:
        Текстовое представление структуры проекта.
    """
    if not is_path_valid(project_path):
        return "Путь не существует"
    
    ignored_dirs = {
        ".git", "venv", ".venv", "__pycache__", ".pytest_cache", 
        ".mypy_cache", ".ruff_cache", ".idea", ".vscode", "node_modules",
        ".tox", ".eggs", "*.egg-info", "dist", "build", ".cache"
    }
    ignored_files = {".DS_Store", "Thumbs.db", ".gitignore"}
    
    lines = []
    file_count = 0
    
    def walk(path: str, prefix: str = "", depth: int = 0):
        nonlocal file_count
        if depth > max_depth or file_count >= max_files:
            return
        
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return
        
        dirs = []
        files = []
        
        for entry in entries:
            if entry in ignored_dirs or entry in ignored_files:
                continue
            full_path = os.path.join(path, entry)
            if os.path.isdir(full_path):
                dirs.append(entry)
            else:
                files.append(entry)
        
        for f in files:
            if file_count >= max_files:
                lines.append(f"{prefix}... (ещё файлы)")
                return
            lines.append(f"{prefix}{f}")
            file_count += 1
        
        for i, d in enumerate(dirs):
            if file_count >= max_files:
                return
            is_last = (i == len(dirs) - 1)
            lines.append(f"{prefix}{d}/")
            new_prefix = prefix + ("    " if is_last else "│   ")
            walk(os.path.join(path, d), new_prefix, depth + 1)
    
    walk(project_path)
    return "\n".join(lines) if lines else "(пусто)"


def find_key_files(project_path: str, max_files: int = 15) -> List[str]:
    """Автоматически определяет ключевые файлы проекта.

    Ищет типичные важные файлы: README, конфиги, точки входа, тесты.

    Args:
        project_path: Путь к проекту.
        max_files: Максимальное количество файлов.

    Returns:
        Список путей к ключевым файлам.
    """
    if not is_path_valid(project_path):
        return []
    
    key_files = []
    
    # Приоритетные паттерны (в порядке важности)
    priority_patterns = [
        # Документация
        ("README*", 1),
        ("CHANGELOG*", 2),
        ("docs/*.md", 3),
        # Конфигурация проекта
        ("pyproject.toml", 1),
        ("setup.py", 1),
        ("setup.cfg", 2),
        ("package.json", 1),
        ("Cargo.toml", 1),
        ("go.mod", 1),
        ("pom.xml", 1),
        ("build.gradle", 1),
        # Конфиги приложения
        ("config.yaml", 1),
        ("config.yml", 1),
        ("config.json", 1),
        ("*.config.js", 2),
        ("*.config.ts", 2),
        (".env.example", 2),
        ("settings.py", 2),
        ("conf/*.yaml", 3),
        ("conf/*.yml", 3),
        # Зависимости
        ("requirements.txt", 1),
        ("requirements*.txt", 2),
        ("Pipfile", 2),
        ("poetry.lock", 3),
        # Точки входа
        ("main.py", 1),
        ("app.py", 1),
        ("__main__.py", 1),
        ("index.js", 1),
        ("index.ts", 1),
        ("src/main.*", 2),
        ("src/index.*", 2),
        ("src/app.*", 2),
        # CI/CD
        (".github/workflows/*.yml", 3),
        (".gitlab-ci.yml", 3),
        ("Dockerfile", 2),
        ("docker-compose.yml", 2),
        ("Makefile", 2),
        # Тесты
        ("tests/test_*.py", 3),
        ("test_*.py", 3),
        ("*_test.py", 3),
    ]
    
    from fnmatch import fnmatch
    
    found = {}  # path -> priority
    
    ignored_dirs = {
        ".git", "venv", ".venv", "__pycache__", ".pytest_cache", 
        ".mypy_cache", ".ruff_cache", ".idea", ".vscode", "node_modules",
        ".tox", ".eggs", "dist", "build", ".cache"
    }
    
    for root, dirs, files in os.walk(project_path):
        # Пропускаем игнорируемые директории
        dirs[:] = [d for d in dirs if d not in ignored_dirs]
        
        rel_root = os.path.relpath(root, project_path)
        if rel_root == ".":
            rel_root = ""
        
        for filename in files:
            if rel_root:
                rel_path = f"{rel_root}/{filename}"
            else:
                rel_path = filename
            
            full_path = os.path.join(root, filename)
            
            for pattern, priority in priority_patterns:
                if fnmatch(rel_path, pattern) or fnmatch(filename, pattern):
                    if full_path not in found or found[full_path] > priority:
                        found[full_path] = priority
                    break
    
    # Сортируем по приоритету и берём top N
    sorted_files = sorted(found.items(), key=lambda x: x[1])
    key_files = [path for path, _ in sorted_files[:max_files]]
    
    return key_files
