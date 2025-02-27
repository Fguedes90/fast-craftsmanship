"""Tests for API commands."""

import shutil

from pathlib import Path

from expression import Error, Ok, effect
from expression.collections import Map

from fcship.commands.api import (
    ApiContext,
    api,
    create_api,
    create_api_files,
    ensure_api_directories,
    notify_success,
    prepare_api_files,
    validate_api_name,
)
from fcship.utils import FileCreationTracker, FileError


def run_effect(effect_fn):
    """Helper function to run effect functions without returning Result"""
    try:
        result = None
        for step in effect_fn():
            result = step
        return result
    except Exception as e:
        raise e


def cleanup_api_files(name: str) -> None:
    """Clean up API files after test"""
    # Clean up v1 API file
    api_file = Path(f"api/v1/{name}.py")
    if api_file.exists():
        api_file.unlink()
        if not any(api_file.parent.iterdir()):
            api_file.parent.rmdir()

    # Clean up schema file
    schema_file = Path(f"api/schemas/{name}.py")
    if schema_file.exists():
        schema_file.unlink()
        if not any(schema_file.parent.iterdir()):
            schema_file.parent.rmdir()

    # Clean up test file
    test_file = Path(f"tests/api/test_{name}.py")
    if test_file.exists():
        test_file.unlink()
        if not any(test_file.parent.iterdir()):
            test_file.parent.rmdir()

    # Clean up parent directories if empty
    api_dir = Path("api")
    if api_dir.exists() and not any(api_dir.iterdir()):
        api_dir.rmdir()

    tests_dir = Path("tests/api")
    if tests_dir.exists() and not any(tests_dir.iterdir()):
        tests_dir.rmdir()


def cleanup_test_directories():
    """Clean up test directories recursively"""
    for directory in ["api", "tests/api"]:
        path = Path(directory)
        if path.exists():
            shutil.rmtree(path)


def test_create_api_success():
    """Test successful API creation"""

    @effect.result[None, str]()
    def run_test():
        result = yield from create_api("test_endpoint")
        assert result.is_ok()
        assert "Created API endpoint test_endpoint" in result.ok
        # Check if files were created
        api_file = Path("api/v1/test_endpoint.py")
        schema_file = Path("api/schemas/test_endpoint.py")
        test_file = Path("tests/api/test_test_endpoint.py")
        assert api_file.exists()
        assert schema_file.exists()
        assert test_file.exists()

    run_test()
    cleanup_api_files("test_endpoint")


def test_create_api_invalid_name():
    """Test API creation with invalid name"""

    @effect.result[None, str]()
    def test_impl():
        result = yield from create_api("")
        assert result.is_error()
        assert "Invalid API name" in result.error
        yield Ok(None)

    run_effect(test_impl)


def test_api_command_success():
    """Test API command execution success"""
    try:

        @effect.result[None, str]()
        def test_impl():
            result = yield from api("create", "test_api")
            assert result.is_ok()
            assert "Created API endpoint test_api" in result.ok
            # Check if files were created
            api_file = Path("api/v1/test_api.py")
            schema_file = Path("api/schemas/test_api.py")
            test_file = Path("tests/api/test_test_api.py")
            assert api_file.exists()
            assert schema_file.exists()
            assert test_file.exists()
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("test_api")


def test_api_command_invalid_operation():
    """Test API command with invalid operation"""

    @effect.result[None, str]()
    def test_impl():
        result = yield from api("invalid", "test_api")
        assert result.is_error()
        assert "Invalid operation" in result.error
        yield Ok(None)

    run_effect(test_impl)


def test_create_api_with_mock(mocker):
    """Test API creation with mocked dependencies"""
    try:

        @effect.result[ApiContext, str]()
        def mock_prepare_files(name: str):
            yield Ok(ApiContext(name=name, files=Map([("test.py", "content")])))

        @effect.result[FileCreationTracker, str]()
        def mock_create_files(files: Map[str, str], base_path: str):
            yield Ok(FileCreationTracker())

        mocker.patch("fcship.commands.api.prepare_api_files", mock_prepare_files)
        mocker.patch("fcship.utils.create_files", mock_create_files)

        @effect.result[None, str]()
        def test_impl():
            result = yield from create_api("test_mock")
            assert result.is_ok()
            assert "Created API endpoint test_mock" in result.ok
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("test_mock")


def test_create_api_prepare_error(mocker):
    """Test API creation when prepare files fails"""
    try:

        @effect.result[ApiContext, str]()
        def mock_prepare_files_error(name: str):
            yield Error("Mock prepare error")

        mocker.patch("fcship.commands.api.prepare_api_files", mock_prepare_files_error)

        @effect.result[None, str]()
        def test_impl():
            result = yield from create_api("test_error")
            assert result.is_error()
            assert "Mock prepare error" in result.error
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("test_error")


def test_ensure_directories_error(mocker):
    """Test error handling when creating directories fails"""
    try:
        # Use a regular function since ensure_directory is now a regular function
        def mock_ensure_directory(path: Path):
            return Error(str(FileError("Failed to create directory", str(path))))

        mocker.patch("fcship.commands.api.ensure_directory", mock_ensure_directory)

        @effect.result[None, str]()
        def test_impl():
            result = yield from create_api("test_dir_error")
            assert result.is_error()
            assert "Failed to create directory" in str(result.error)
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("test_dir_error")


def test_create_files_error(mocker):
    """Test error handling when creating files fails"""
    try:

        @effect.result[FileCreationTracker, str]()
        def mock_create_single_file(tracker, path_content: tuple[Path, str]):
            yield Error(str(FileError("Failed to write file", str(path_content[0]))))

        mocker.patch("fcship.commands.api.create_single_file", mock_create_single_file)

        @effect.result[None, str]()
        def test_impl():
            result = yield from create_api("test_file_error")
            assert result.is_error()
            assert "Failed to write file" in str(result.error)
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("test_file_error")


def test_notify_success_error(mocker):
    """Test error handling when success notification fails"""
    try:

        @effect.result[None, str]()
        def mock_success_message(ctx, msg):
            yield Error("Failed to show success message")

        mocker.patch("fcship.commands.api.success_message", mock_success_message)

        @effect.result[None, str]()
        def test_impl():
            result = yield from create_api("test_notify_error")
            assert result.is_error()
            assert "Failed to show success message" in result.error
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("test_notify_error")


def test_api_unexpected_error(mocker):
    """Test handling of unexpected errors in API command"""
    try:

        def mock_validate_operation(*args):
            raise Exception("Unexpected error")

        mocker.patch("fcship.commands.api.validate_operation", mock_validate_operation)

        @effect.result[None, str]()
        def test_impl():
            result = yield from api("create", "test_error")
            assert result.is_error()
            assert "Unexpected error" in result.error
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("test_error")


def test_create_api_unexpected_error(mocker):
    """Test handling of unexpected errors in create_api"""
    try:

        def mock_validate_name(*args):
            raise Exception("Unexpected validation error")

        mocker.patch("fcship.commands.api.validate_api_name", mock_validate_name)

        @effect.result[None, str]()
        def test_impl():
            result = yield from create_api("test_error")
            assert result.is_error()
            assert "Unexpected error" in result.error
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("test_error")


def test_validate_api_name_invalid_identifier():
    """Test API name validation with invalid Python identifier"""
    try:

        @effect.result[None, str]()
        def test_impl():
            result = yield from validate_api_name("invalid-name")
            assert result.is_error()
            assert "must be a valid Python identifier" in result.error
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("invalid-name")


def test_prepare_api_files_unexpected_error(mocker):
    """Test prepare_api_files with unexpected error"""
    try:

        def mock_get_templates(*args):
            raise Exception("Unexpected template error")

        mocker.patch("fcship.commands.api.get_api_templates", mock_get_templates)

        @effect.result[None, str]()
        def test_impl():
            result = yield from prepare_api_files("test_error")
            assert result.is_error()
            assert "Failed to prepare API files" in result.error
            assert "Unexpected template error" in result.error
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("test_error")


def test_ensure_directories_unexpected_error(mocker):
    """Test ensure_api_directories with unexpected error"""
    try:
        # Use a regular function since ensure_directory is now a regular function
        def mock_ensure_directory(path: Path):
            return Error(str(FileError("Failed to create directory", str(path))))

        mocker.patch("fcship.commands.api.ensure_directory", mock_ensure_directory)

        @effect.result[None, str]()
        def test_impl():
            result = yield from ensure_api_directories()
            assert result.is_error()
            assert "Failed to create directory" in str(result.error)
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_test_directories()


def test_create_files_unexpected_error(mocker):
    """Test create_api_files with unexpected error"""

    # Use a regular function for ensure_directory now
    def mock_ensure_directory(path: Path):
        return Ok(None)

    @effect.result[FileCreationTracker, str]()
    def mock_create_single_file(tracker, path_content: tuple[Path, str]):
        yield Error(str(FileError("Failed to write file", str(path_content[0]))))

    mocker.patch("fcship.commands.api.ensure_directory", mock_ensure_directory)
    mocker.patch("fcship.commands.api.create_single_file", mock_create_single_file)

    @effect.result[None, str]()
    def test_impl():
        files = Map.of_seq([("test.py", "content")])
        result = yield from create_api_files(ApiContext(name="test", files=files))
        assert result.is_error()
        assert "Failed to write file" in str(result.error)
        yield Ok(None)

    run_effect(test_impl)


def test_notify_success_unexpected_error(mocker):
    """Test notify_success with unexpected error"""

    def mock_success_message(*args):
        raise Exception("Unexpected notification error")

    mocker.patch("fcship.commands.api.success_message", mock_success_message)

    @effect.result[None, str]()
    def test_impl():
        result = yield from notify_success(
            ApiContext(name="test", files=Map()), FileCreationTracker()
        )
        assert result.is_error()
        assert "Failed to show success message" in result.error
        assert "Unexpected notification error" in result.error
        yield Ok(None)

    run_effect(test_impl)


def test_api_unexpected_error_in_create(mocker):
    """Test api function with unexpected error in create_api"""

    def mock_create_api(*args):
        raise Exception("Unexpected create error")

    mocker.patch("fcship.commands.api.create_api", mock_create_api)

    @effect.result[None, str]()
    def test_impl():
        result = yield from api("create", "test_error")
        assert result.is_error()
        assert "Unexpected error" in result.error
        assert "Unexpected create error" in result.error
        yield Ok(None)

    run_effect(test_impl)


def test_ensure_directories_general_error(mocker):
    """Test ensure_api_directories with a general exception"""
    try:
        # Use a regular function since ensure_directory is now a regular function
        def mock_ensure_directory(path: Path):
            if str(path) == "api/v1":  # Trigger error on specific directory
                return Error("General directory error")
            return Ok(None)

        mocker.patch("fcship.commands.api.ensure_directory", mock_ensure_directory)

        @effect.result[None, str]()
        def test_impl():
            result = yield from ensure_api_directories()
            assert result.is_error()
            assert "Failed to create API directories" in result.error
            assert "General directory error" in result.error
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_test_directories()


def test_create_files_general_error(mocker):
    """Test create_api_files with a general exception"""
    try:
        # Use a regular function for ensure_directory now
        def mock_ensure_directory(path: Path):
            return Ok(None)

        @effect.result[FileCreationTracker, str]()
        def mock_create_single_file(tracker, path_content: tuple[Path, str]):
            raise RuntimeError("General file error")

        mocker.patch("fcship.commands.api.ensure_directory", mock_ensure_directory)
        mocker.patch("fcship.commands.api.create_single_file", mock_create_single_file)

        @effect.result[None, str]()
        def test_impl():
            files = Map.of_seq([("test.py", "content")])
            result = yield from create_api_files(ApiContext(name="test", files=files))
            assert result.is_error()
            assert "Failed to create API files" in result.error
            assert "General file error" in result.error
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("test")


def test_api_general_error(mocker):
    """Test api function with a general exception"""
    try:

        @effect.result[tuple[str, str], str]()
        def mock_validate_operation(operation: str, name: str):
            yield Ok((operation, name))

        @effect.result[str, str]()
        def mock_create_api(name: str):
            raise RuntimeError("General API error")

        mocker.patch("fcship.commands.api.validate_operation", mock_validate_operation)
        mocker.patch("fcship.commands.api.create_api", mock_create_api)

        @effect.result[None, str]()
        def test_impl():
            result = yield from api("create", "test_error")
            assert result.is_error()
            assert "Unexpected error" in result.error
            assert "General API error" in result.error
            yield Ok(None)

        run_effect(test_impl)
    finally:
        cleanup_api_files("test_error")
