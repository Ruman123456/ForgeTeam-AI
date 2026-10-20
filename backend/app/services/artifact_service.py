"""ForgeTeam AI - Artifact management service.

Handles writing generated files to disk, creating ZIP archives,
and managing artifact records in the database.
"""

import hashlib
import io
import logging
import os
import re
import zipfile
from pathlib import Path
from typing import Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


class ArtifactService:
    """Manages generated project artifacts on disk."""

    def __init__(self):
        self.base_dir = settings.generated_projects_path

    def get_run_dir(self, run_id: str) -> Path:
        """Get the directory for a specific run's artifacts."""
        # Sanitize run_id to prevent path traversal
        safe_id = re.sub(r'[^a-zA-Z0-9\-_]', '', run_id)
        if not safe_id:
            raise ValueError("Invalid run ID")
        return self.base_dir / safe_id

    def ensure_run_dir(self, run_id: str) -> Path:
        """Create and return the run directory."""
        run_dir = self.get_run_dir(run_id)
        run_dir.mkdir(parents=True, exist_ok=True)
        return run_dir

    def write_file(self, run_id: str, relative_path: str, content: str) -> Path:
        """Write a file to the run's project directory.

        Args:
            run_id: The run identifier
            relative_path: Relative path within the project
            content: File content

        Returns:
            Absolute path to the written file

        Raises:
            ValueError: If path traversal is detected or file is too large
        """
        run_dir = self.ensure_run_dir(run_id)

        # Validate relative path - prevent traversal
        normalized = os.path.normpath(relative_path)
        if normalized.startswith('..') or normalized.startswith('/') or normalized.startswith('\\'):
            raise ValueError(f"Path traversal detected: {relative_path}")
        if ':' in normalized:
            raise ValueError(f"Absolute path not allowed: {relative_path}")

        # Check file size
        content_bytes = content.encode('utf-8')
        if len(content_bytes) > settings.max_file_size_bytes:
            raise ValueError(
                f"File too large ({len(content_bytes)} bytes). "
                f"Max: {settings.max_file_size_bytes} bytes"
            )

        # Write the file
        file_path = run_dir / normalized
        file_path.parent.mkdir(parents=True, exist_ok=True)

        # Verify resolved path is within run directory
        resolved = file_path.resolve()
        if not str(resolved).startswith(str(run_dir.resolve())):
            raise ValueError(f"Path traversal detected: {relative_path}")

        file_path.write_text(content, encoding='utf-8')
        logger.info(f"Written artifact: {relative_path} for run {run_id}")
        return file_path

    def write_generated_files(self, run_id: str, files_data: dict) -> list[dict]:
        """Write all generated files from developer output to disk.

        Returns list of artifact records with paths and checksums.
        """
        artifacts = []
        files = files_data.get("files_created", [])

        for file_info in files:
            path = file_info.get("path", "")
            content = file_info.get("content", "")
            description = file_info.get("description", "")

            if not path or not content:
                continue

            try:
                self.write_file(run_id, path, content)
                checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
                artifacts.append({
                    "relative_path": path,
                    "artifact_type": self._detect_type(path),
                    "description": description,
                    "checksum": checksum,
                })
            except ValueError as e:
                logger.warning(f"Skipping file {path}: {e}")
            except Exception as e:
                logger.error(f"Error writing {path}: {e}")

        return artifacts

    def write_report(self, run_id: str, filename: str, content: str) -> Optional[dict]:
        """Write a report file (plan.json, review_report.json, etc.)."""
        try:
            self.write_file(run_id, filename, content)
            checksum = hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
            return {
                "relative_path": filename,
                "artifact_type": "report",
                "description": f"Generated report: {filename}",
                "checksum": checksum,
            }
        except Exception as e:
            logger.error(f"Error writing report {filename}: {e}")
            return None

    def read_file(self, run_id: str, relative_path: str) -> Optional[str]:
        """Read a file from the run's project directory."""
        run_dir = self.get_run_dir(run_id)
        normalized = os.path.normpath(relative_path)

        if normalized.startswith('..') or ':' in normalized:
            return None

        file_path = run_dir / normalized
        resolved = file_path.resolve()

        if not str(resolved).startswith(str(run_dir.resolve())):
            return None

        if not file_path.exists() or not file_path.is_file():
            return None

        try:
            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Error reading {relative_path}: {e}")
            return None

    def list_files(self, run_id: str) -> list[str]:
        """List all files in a run's directory."""
        run_dir = self.get_run_dir(run_id)
        if not run_dir.exists():
            return []

        files = []
        for path in run_dir.rglob('*'):
            if path.is_file():
                rel = path.relative_to(run_dir)
                files.append(str(rel).replace('\\', '/'))
        return sorted(files)

    def create_zip(self, run_id: str) -> Optional[bytes]:
        """Create a ZIP archive of the run's generated project.

        Returns ZIP file bytes or None if directory doesn't exist.
        """
        run_dir = self.get_run_dir(run_id)
        if not run_dir.exists():
            return None

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
            for file_path in run_dir.rglob('*'):
                if file_path.is_file():
                    rel_path = file_path.relative_to(run_dir)
                    # Prevent archive path traversal
                    safe_path = str(rel_path).replace('\\', '/')
                    if '..' in safe_path:
                        continue
                    zf.write(file_path, safe_path)

        return buffer.getvalue()

    def delete_run_files(self, run_id: str) -> bool:
        """Delete all files for a run."""
        import shutil
        run_dir = self.get_run_dir(run_id)
        if run_dir.exists():
            shutil.rmtree(run_dir)
            return True
        return False

    @staticmethod
    def _detect_type(path: str) -> str:
        """Detect artifact type from file extension."""
        ext = Path(path).suffix.lower()
        type_map = {
            '.py': 'source', '.js': 'source', '.ts': 'source', '.tsx': 'source',
            '.jsx': 'source', '.java': 'source', '.go': 'source', '.rs': 'source',
            '.html': 'template', '.css': 'style', '.scss': 'style',
            '.json': 'config', '.yaml': 'config', '.yml': 'config', '.toml': 'config',
            '.md': 'documentation', '.txt': 'documentation', '.rst': 'documentation',
            '.sql': 'database', '.sh': 'script', '.bat': 'script',
            '.test.py': 'test', '.spec.ts': 'test', '.test.ts': 'test',
        }
        return type_map.get(ext, 'other')


# Singleton
artifact_service = ArtifactService()
