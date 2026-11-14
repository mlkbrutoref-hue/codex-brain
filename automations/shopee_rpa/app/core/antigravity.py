"""Antigravity CLI client for headless execution, skill orchestration, and AI reasoning."""
import json
import os
import shutil
import subprocess
import time
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional
from app.core.telemetry import antigravity_operation, count


class AntigravityError(Exception):
    """Base exception for Antigravity integration."""
    pass


class AntigravityNotFoundError(AntigravityError):
    """Raised when the Antigravity (agy) executable cannot be located."""
    pass


class AntigravityTimeoutError(AntigravityError):
    """Raised when an Antigravity command execution times out."""
    pass


class AntigravityExecutionError(AntigravityError):
    """Raised when an Antigravity command fails with non-zero exit code."""
    def __init__(self, message: str, exit_code: int, stderr: str = "", stdout: str = ""):
        super().__init__(message)
        self.exit_code = exit_code
        self.stderr = stderr
        self.stdout = stdout


class AntigravityPermissionError(AntigravityError):
    """Raised when a real CLI call was not explicitly enabled by the caller."""
    pass


@dataclass
class AntigravityResult:
    """Represents the structured result of an Antigravity CLI invocation."""
    exit_code: int
    stdout: str
    stderr: str
    duration_seconds: float
    success: bool
    is_timeout: bool = False
    parsed_json: Optional[Any] = None


class AntigravityClient:
    """Manages discovery and safe execution of the Antigravity CLI (agy.exe)."""

    DEFAULT_PATHS = [
        os.path.expandvars(r"%LOCALAPPDATA%\agy\bin\agy.exe"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\agy\bin\agy.exe"),
        r"C:\Users\GAMER\AppData\Local\agy\bin\agy.exe",
    ]

    def __init__(
        self,
        binary_path: Optional[str] = None,
        mock_mode: bool = False,
        mock_runner: Optional[Callable[..., AntigravityResult]] = None,
        allow_real_calls: bool = False,
    ):
        self.mock_mode = mock_mode
        self.mock_runner = mock_runner
        self.allow_real_calls = allow_real_calls
        self._binary_path = binary_path or self.discover_binary()

    @classmethod
    def discover_binary(cls) -> Optional[str]:
        """Locates the agy.exe executable using environment variables, PATH, and standard directories."""
        env_override = os.environ.get("AGY_BIN_PATH") or os.environ.get("ANTIGRAVITY_BIN")
        if env_override and os.path.isfile(env_override):
            return os.path.abspath(env_override)

        which_path = shutil.which("agy") or shutil.which("agy.exe")
        if which_path and os.path.isfile(which_path):
            return os.path.abspath(which_path)

        for candidate in cls.DEFAULT_PATHS:
            if os.path.isfile(candidate):
                return os.path.abspath(candidate)

        return None

    @property
    def is_available(self) -> bool:
        """Returns True if the binary path is valid and executable or in mock mode."""
        if self.mock_mode:
            return True
        return bool(self._binary_path and os.path.isfile(self._binary_path))

    @property
    def binary_path(self) -> Optional[str]:
        """Returns the discovered or configured binary path."""
        return self._binary_path

    def get_version(self, timeout: float = 5.0) -> Optional[str]:
        """Returns the CLI version string (e.g. '1.1.28') or None."""
        if self.mock_mode:
            return "1.1.28-mock"
        if not self.is_available:
            return None

        try:
            res = self.execute(["--version"], timeout=timeout)
            if res.success:
                return res.stdout.strip()
        except Exception:
            return None
        return None

    @antigravity_operation
    def execute(
        self,
        args: List[str],
        timeout: float = 30.0,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
    ) -> AntigravityResult:
        """Executes the agy CLI with the specified arguments."""
        if self.mock_mode:
            count("antigravity_mock_calls", source="mock")
            if self.mock_runner:
                return self.mock_runner(args, timeout=timeout, cwd=cwd, env=env)
            return AntigravityResult(
                exit_code=0,
                stdout="Mock Antigravity Execution OK",
                stderr="",
                duration_seconds=0.01,
                success=True,
            )

        if not self.is_available or not self._binary_path:
            raise AntigravityNotFoundError("Antigravity CLI binary (agy.exe) not found.")
        if not self.allow_real_calls:
            raise AntigravityPermissionError(
                "Real Antigravity execution is disabled; set allow_real_calls=True only for an explicitly authorized live run."
            )

        cmd = [self._binary_path] + args
        start_time = time.time()

        # Product credentials must never be inherited by an auxiliary CLI process.
        exec_env = {
            key: value for key, value in os.environ.items()
            if not key.upper().startswith("SHOPEE_")
        }
        if env:
            exec_env.update({
                key: value for key, value in env.items()
                if not key.upper().startswith("SHOPEE_")
            })

        try:
            count("antigravity_calls" if "-p" in args or "--print" in args else "antigravity_cli_checks")
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd,
                env=exec_env,
            )
            duration = time.time() - start_time
            stdout = proc.stdout or ""
            stderr = proc.stderr or ""
            success = proc.returncode == 0

            parsed_json = None
            if "--output-format" in args:
                idx = args.index("--output-format")
                if idx + 1 < len(args) and args[idx + 1] == "json":
                    try:
                        parsed_json = json.loads(stdout)
                    except (TypeError, ValueError, json.JSONDecodeError):
                        success = False

            if not success:
                count("antigravity_failures")
            if not stdout.strip():
                count("antigravity_empty_results")
            return AntigravityResult(
                exit_code=proc.returncode,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=duration,
                success=success,
                parsed_json=parsed_json,
            )

        except subprocess.TimeoutExpired as e:
            count("antigravity_timeouts")
            count("antigravity_failures")
            duration = time.time() - start_time
            stdout = e.stdout.decode() if isinstance(e.stdout, bytes) else (e.stdout or "")
            stderr = e.stderr.decode() if isinstance(e.stderr, bytes) else (e.stderr or "")
            return AntigravityResult(
                exit_code=-1,
                stdout=stdout,
                stderr=stderr,
                duration_seconds=duration,
                success=False,
                is_timeout=True,
            )
        except Exception as e:
            count("antigravity_failures")
            duration = time.time() - start_time
            raise AntigravityError(
                f"Failed to execute Antigravity CLI ({type(e).__name__}); details omitted."
            ) from None

    def run_prompt(
        self,
        prompt: str,
        output_format: str = "text",
        json_schema: Optional[str] = None,
        timeout: float = 60.0,
        cwd: Optional[str] = None,
        workspace_dir: Optional[str] = None,
    ) -> AntigravityResult:
        """Executes a single non-interactive prompt using print mode (-p / --print).

        Args:
            workspace_dir: If provided, passes --add-dir to register the workspace
                so that .agents/skills/ and .agents/rules/ are discovered.
        """
        args = []
        if workspace_dir:
            args.extend(["--add-dir", workspace_dir])
        args.extend(["-p", prompt, "--output-format", output_format])
        if json_schema:
            args.extend(["--json-schema", json_schema])

        res = self.execute(args, timeout=timeout, cwd=cwd)
        if res.is_timeout:
            raise AntigravityTimeoutError(f"Antigravity prompt execution timed out after {timeout}s.")
        if not res.success and not self.mock_mode:
            raise AntigravityExecutionError(
                f"Antigravity returned exit code {res.exit_code}",
                exit_code=res.exit_code,
                stderr="",
                stdout="",
            )
        if output_format == "json" and res.parsed_json is None:
            raise AntigravityExecutionError(
                "Antigravity returned invalid JSON output.",
                exit_code=res.exit_code,
            )
        if json_schema and not self.mock_mode:
            envelope = res.parsed_json
            if not isinstance(envelope, dict) or not isinstance(envelope.get("structured_output"), dict):
                raise AntigravityExecutionError(
                    "Antigravity returned no structured_output object.",
                    exit_code=res.exit_code,
                )
        return res

    def get_runtime_status(self) -> Dict[str, Any]:
        """Returns a diagnostic status summary for the Antigravity integration."""
        available = self.is_available
        version = self.get_version() if available else None
        return {
            "available": available,
            "binary_path": self._binary_path,
            "version": version,
            "mock_mode": self.mock_mode,
            "allow_real_calls": self.allow_real_calls,
        }
