"""ForgeTeam AI - Safe Test Execution Service.

Runs tests safely using Docker if available and enabled.
Falls back to static checks and syntax validation if Docker is unavailable.
"""

import ast
import logging
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Any, List

from app.core.config import settings
from app.schemas.schemas import TestResult, TesterOutput

logger = logging.getLogger(__name__)


class TestExecutionService:
    """Safe test execution service."""

    def __init__(self):
        self.docker_available = self._detect_docker()

    def _detect_docker(self) -> bool:
        if not settings.docker_enabled:
            return False
        try:
            docker_cmd = shutil.which("docker")
            if not docker_cmd:
                return False
            result = subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            return result.returncode == 0
        except Exception:
            return False

    def execute_or_validate_project(self, run_dir: Path) -> TesterOutput:
        """Execute tests in Docker if available, otherwise perform safe static checks."""
        if self.docker_available:
            return self._run_docker_tests(run_dir)
        return self._run_static_analysis(run_dir)

    def _run_docker_tests(self, run_dir: Path) -> TesterOutput:
        """Run tests inside an isolated Docker container with strict constraints."""
        results: List[TestResult] = []
        try:
            cmd = [
                "docker", "run", "--rm",
                "--network", "none",
                "--memory", "512m",
                "--cpus", "1.0",
                "--pids-limit", "64",
                "--read-only",
                "-v", f"{run_dir.resolve()}:/workspace:ro",
                "-w", "/workspace",
                "python:3.11-slim",
                "pytest", "-v", "--no-header"
            ]
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=settings.docker_timeout,
            )
            stdout = proc.stdout[:4000]
            passed = stdout.count("PASSED")
            failed = stdout.count("FAILED")

            results.append(
                TestResult(
                    test_name="docker_pytest_execution",
                    status="passed" if proc.returncode == 0 else "failed",
                    message=f"Return code {proc.returncode}. Output:\n{stdout}",
                )
            )

            return TesterOutput(
                test_results=results,
                passed=passed,
                failed=failed,
                skipped=0,
                blocked=0,
                summary=f"Docker containerized tests finished with return code {proc.returncode}.",
                execution_method="docker",
            )
        except subprocess.TimeoutExpired:
            results.append(
                TestResult(
                    test_name="docker_pytest_execution",
                    status="failed",
                    message=f"Docker test execution timed out after {settings.docker_timeout} seconds.",
                )
            )
            return TesterOutput(
                test_results=results,
                passed=0,
                failed=1,
                skipped=0,
                blocked=0,
                summary="Containerized test run timed out.",
                execution_method="docker",
            )
        except Exception as e:
            logger.error(f"Docker test execution error: {e}")
            return self._run_static_analysis(run_dir)

    def _run_static_analysis(self, run_dir: Path) -> TesterOutput:
        """Perform safe static Python syntax and structure checks when Docker is unavailable."""
        results: List[TestResult] = []
        passed = 0
        failed = 0
        skipped = 0

        py_files = list(run_dir.rglob("*.py"))
        for py_file in py_files:
            rel = str(py_file.relative_to(run_dir)).replace("\\", "/")
            try:
                content = py_file.read_text(encoding="utf-8")
                ast.parse(content)
                passed += 1
                results.append(
                    TestResult(
                        test_name=f"ast_syntax_check:{rel}",
                        status="passed",
                        message="Python AST syntax validation passed",
                        file_path=rel,
                    )
                )
            except SyntaxError as se:
                failed += 1
                results.append(
                    TestResult(
                        test_name=f"ast_syntax_check:{rel}",
                        status="failed",
                        message=f"Syntax error at line {se.lineno}: {se.msg}",
                        file_path=rel,
                    )
                )

        # Mark runtime tests as skipped with honest reporting
        test_files = [f for f in py_files if "test" in f.name.lower()]
        for tf in test_files:
            rel = str(tf.relative_to(run_dir)).replace("\\", "/")
            skipped += 1
            results.append(
                TestResult(
                    test_name=f"runtime_execution:{rel}",
                    status="skipped",
                    message="Runtime execution skipped: Docker sandbox unavailable on host.",
                    file_path=rel,
                )
            )

        summary = (
            f"Static analysis completed for {len(py_files)} files. "
            f"{passed} syntax checks passed, {failed} syntax checks failed. "
            f"{skipped} runtime test suites were safely skipped because Docker isolation is not configured or available."
        )

        return TesterOutput(
            test_results=results,
            passed=passed,
            failed=failed,
            skipped=skipped,
            blocked=0,
            summary=summary,
            execution_method="static_analysis",
        )


test_execution_service = TestExecutionService()
