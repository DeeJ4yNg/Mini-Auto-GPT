"""File operations for AutoGPT"""
from __future__ import annotations
import os
import os.path
from pathlib import Path
from typing import Generator


# Set a dedicated folder for file I/O
WORKSPACE_PATH = Path(os.getcwd()) / "auto_gpt_workspace"
# Create the directory if it doesn't exist
if not os.path.exists(WORKSPACE_PATH):
    os.makedirs(WORKSPACE_PATH)

LOG_FILE = "file_logger.txt"
LOG_FILE_PATH = WORKSPACE_PATH / LOG_FILE

def path_in_workspace(relative_path: str | Path) -> Path:
    return safe_path_join(WORKSPACE_PATH, relative_path)


def safe_path_join(base: Path, *paths: str | Path) -> Path:
    joined_path = base.joinpath(*paths).resolve()
    if not joined_path.is_relative_to(base):
        raise ValueError(f"Attempted to access path '{joined_path}' outside of working directory '{base}'.")
    return joined_path


#Main

def check_duplicate_operation(operation: str, filename: str) -> bool:
    log_content = read_file(LOG_FILE)
    log_entry = f"{operation}: {filename}\n"
    return log_entry in log_content


def log_operation(operation: str, filename: str) -> None:
    log_entry = f"{operation}: {filename}\n"
    if not os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "w", encoding="utf-8") as f:
            f.write("File Operation Logger ")
    append_to_file(LOG_FILE, log_entry, shouldLog = False)


def split_file(
    content: str, max_length: int = 4000, overlap: int = 0
) -> Generator[str, None, None]:
    start = 0
    content_length = len(content)

    while start < content_length:
        end = start + max_length
        if end + overlap < content_length:
            chunk = content[start : end + overlap]
        else:
            chunk = content[start:content_length]
        yield chunk
        start += max_length - overlap


def read_file(filename: str) -> str:
    try:
        filepath = path_in_workspace(filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error: {str(e)}"


def ingest_file(
    filename: str, memory, max_length: int = 4000, overlap: int = 200
) -> None:
    try:
        print(f"Working with file {filename}")
        content = read_file(filename)
        content_length = len(content)
        print(f"File length: {content_length} characters")

        chunks = list(split_file(content, max_length=max_length, overlap=overlap))

        num_chunks = len(chunks)
        for i, chunk in enumerate(chunks):
            print(f"Ingesting chunk {i + 1} / {num_chunks} into memory")
            memory_to_add = (
                f"Filename: {filename}\n" f"Content part#{i + 1}/{num_chunks}: {chunk}"
            )

            memory.add(memory_to_add)

        print(f"Done ingesting {num_chunks} chunks from {filename}.")
    except Exception as e:
        print(f"Error while ingesting file '{filename}': {str(e)}")


def write_to_file(filename: str, text: str) -> str:
    if check_duplicate_operation("write", filename):
        return "Error: File has already been updated."
    try:
        filepath = path_in_workspace(filename)
        directory = os.path.dirname(filepath)
        if not os.path.exists(directory):
            os.makedirs(directory)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(text)
        log_operation("write", filename)
        return "File written to successfully."
    except Exception as e:
        return f"Error: {str(e)}"


def append_to_file(filename: str, text: str, shouldLog: bool = True) -> str:
    try:
        filepath = path_in_workspace(filename)
        with open(filepath, "a") as f:
            f.write(text)

        if shouldLog:
            log_operation("append", filename)

        return "Text appended successfully."
    except Exception as e:
        return f"Error: {str(e)}"


def delete_file(filename: str) -> str:
    if check_duplicate_operation("delete", filename):
        return "Error: File has already been deleted."
    try:
        filepath = path_in_workspace(filename)
        os.remove(filepath)
        log_operation("delete", filename)
        return "File deleted successfully."
    except Exception as e:
        return f"Error: {str(e)}"


def search_files(directory: str) -> list[str]:
    found_files = []
    if directory in {"", "/"}:
        search_directory = WORKSPACE_PATH
    else:
        search_directory = path_in_workspace(directory)
    for root, _, files in os.walk(search_directory):
        for file in files:
            if file.startswith("."):
                continue
            relative_path = os.path.relpath(os.path.join(root, file), WORKSPACE_PATH)
            found_files.append(relative_path)
    return found_files
