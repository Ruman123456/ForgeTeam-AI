"""ForgeTeam AI - Agent implementations.

Each agent is a callable that takes the workflow state and returns updated state.
Agents use either the Ollama LLM or demo mode outputs.
"""

import json
import logging
from typing import Any

from app.agents.prompts import (
    PLANNER_SYSTEM_PROMPT,
    ARCHITECT_SYSTEM_PROMPT,
    DEVELOPER_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT,
    TESTER_SYSTEM_PROMPT,
)
from app.agents.demo_outputs import (
    get_demo_planner_output,
    get_demo_architect_output,
    get_demo_developer_output,
    get_demo_reviewer_output,
    get_demo_tester_output,
)
from app.schemas.schemas import (
    PlannerOutput,
    ArchitectOutput,
    DeveloperOutput,
    ReviewerOutput,
    TesterOutput,
)
from app.services.ollama_client import ollama_client, OllamaError
from app.services.groq_client import groq_client, GroqError

logger = logging.getLogger(__name__)


async def _generate_llm_json(
    state: dict[str, Any],
    prompt: str,
    system_prompt: str,
    temperature: float = 0.3,
) -> dict:
    """Generate structured JSON using either Groq Cloud or local Ollama."""
    engine = state.get("engine", "local")

    if engine == "groq" and groq_client.is_configured():
        logger.info(f"Using Groq Cloud inference (model: {groq_client.model})")
        return await groq_client.generate_json(
            prompt=prompt,
            system_prompt=system_prompt,
            temperature=temperature,
        )

    # Default to local Ollama
    return await ollama_client.generate_json(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=temperature,
    )


async def run_planner(state: dict[str, Any]) -> dict[str, Any]:
    """Project Planner agent - interprets requirements and creates a plan."""
    logger.info(f"[Planner] Starting for run {state.get('run_id')} (engine: {state.get('engine', 'local')})")
    user_request = state.get("user_request", "")

    if state.get("demo_mode") and state.get("engine") == "demo":
        output = get_demo_planner_output(user_request)
    else:
        try:
            prompt = f"Create a comprehensive project plan for the following software request:\n\n{user_request}"
            raw = await _generate_llm_json(
                state=state,
                prompt=prompt,
                system_prompt=PLANNER_SYSTEM_PROMPT,
                temperature=0.3,
            )
            output = PlannerOutput(**raw)
        except (OllamaError, GroqError) as e:
            logger.error(f"[Planner] LLM error: {e}")
            state["error_messages"] = state.get("error_messages", []) + [f"Planner LLM error: {e}"]
            output = PlannerOutput(
                project_summary=f"Failed to generate plan: {e}",
                requirements=["Error: LLM unavailable"],
            )
        except Exception as e:
            logger.error(f"[Planner] Unexpected error: {e}")
            output = PlannerOutput(project_summary=f"Planning error: {e}")

    state["requirements"] = output.model_dump()
    state["current_agent"] = "planner"
    state["agent_messages"] = state.get("agent_messages", []) + [
        {"agent": "planner", "type": "output", "content": output.project_summary}
    ]
    logger.info(f"[Planner] Completed. Requirements: {len(output.requirements)}, Tasks: {len(output.task_list)}")
    return state


async def run_architect(state: dict[str, Any]) -> dict[str, Any]:
    """Architecture agent - designs the system structure."""
    logger.info(f"[Architect] Starting for run {state.get('run_id')} (engine: {state.get('engine', 'local')})")
    requirements = state.get("requirements", {})

    if state.get("demo_mode") and state.get("engine") == "demo":
        output = get_demo_architect_output(requirements.get("project_summary", ""))
    else:
        try:
            prompt = (
                f"Design the architecture for this project:\n\n"
                f"Summary: {requirements.get('project_summary', '')}\n\n"
                f"Requirements:\n" + "\n".join(f"- {r}" for r in requirements.get("requirements", []))
                + f"\n\nTasks:\n" + json.dumps(requirements.get("task_list", []), indent=2)
            )
            raw = await _generate_llm_json(
                state=state,
                prompt=prompt,
                system_prompt=ARCHITECT_SYSTEM_PROMPT,
                temperature=0.3,
            )
            output = ArchitectOutput(**raw)
        except (OllamaError, GroqError) as e:
            logger.error(f"[Architect] LLM error: {e}")
            state["error_messages"] = state.get("error_messages", []) + [f"Architect LLM error: {e}"]
            output = ArchitectOutput(architecture_summary=f"Failed to design architecture: {e}")
        except Exception as e:
            logger.error(f"[Architect] Unexpected error: {e}")
            output = ArchitectOutput(architecture_summary=f"Architecture error: {e}")

    state["architecture"] = output.model_dump()
    state["task_plan"] = requirements.get("task_list", [])
    state["current_agent"] = "architect"
    state["agent_messages"] = state.get("agent_messages", []) + [
        {"agent": "architect", "type": "output", "content": output.architecture_summary}
    ]
    logger.info(f"[Architect] Completed. Files planned: {len(output.file_tree)}")
    return state


async def _recover_partial_developer_output(raw_text: str) -> dict:
    """Attempt to extract as many files_created entries as possible from a truncated LLM response."""
    import re
    files_created = []
    # Try to extract individual file objects from a partial JSON array
    path_matches = list(re.finditer(r'"path"\s*:\s*"([^"]+)"', raw_text))
    for m in path_matches:
        content_match = re.search(r'"content"\s*:\s*"((?:[^"\\]|\\.)*)"', raw_text[m.start():m.start() + 100000])
        if content_match:
            path = m.group(1)
            content = content_match.group(1)
            try:
                content = content.encode('utf-8').decode('unicode_escape')
            except Exception:
                pass
            files_created.append({"path": path, "content": content, "description": f"Auto-recovered: {path}"})

    notes_match = re.search(r'"implementation_notes"\s*:\s*"([^"]*)"', raw_text)
    notes = notes_match.group(1) if notes_match else "Partially recovered due to token limit"
    return {
        "files_created": files_created,
        "implementation_notes": f"{notes} ({len(files_created)} files recovered)",
        "files_changed": [f["path"] for f in files_created],
    }


async def run_developer(state: dict[str, Any]) -> dict[str, Any]:
    """Developer agent - generates complete, enterprise-grade source files."""
    logger.info(f"[Developer] Starting for run {state.get('run_id')} (engine: {state.get('engine', 'local')})")
    architecture = state.get("architecture", {})
    review_findings = state.get("review_findings", [])
    requirements = state.get("requirements", {})

    if state.get("demo_mode") and state.get("engine") == "demo":
        output = get_demo_developer_output(architecture.get("file_tree", []))
    else:
        try:
            revision_context = ""
            existing_files = state.get("generated_files", {}).get("files_created", [])
            if review_findings:
                files_snapshot = []
                for f in existing_files[:15]:
                    # Show more content for revision context
                    files_snapshot.append(f"--- {f.get('path', 'unknown')} ---\n{f.get('content', '')[:3000]}")

                revision_context = (
                    "\n\n=== MANDATORY REVISION REQUIRED ===\n"
                    "The senior code reviewer found CRITICAL issues you MUST fix:\n"
                    + json.dumps(review_findings, indent=2)
                    + "\n\nCurrent file implementations (for context):\n"
                    + "\n\n".join(files_snapshot)
                    + "\n\n=== REVISION INSTRUCTIONS ===\n"
                    "1. Fix EVERY error-level issue listed above.\n"
                    "2. Replace sha256/md5 password hashing with bcrypt (passlib).\n"
                    "3. Add all missing imports at the top of each file.\n"
                    "4. Implement all placeholder/stub functions with real logic.\n"
                    "5. Re-generate ALL files completely — not just the changed ones.\n"
                    "6. Every file must be complete and runnable without modifications."
                )

            # Rich, detailed prompt with full architectural context
            lang = requirements.get("language_preference", "python")
            framework = requirements.get("framework_preference", "fastapi")
            file_tree_str = "\n".join(architecture.get("file_tree", []))
            components_str = json.dumps(architecture.get("component_responsibilities", []), indent=2)
            api_str = json.dumps(architecture.get("api_outline", []), indent=2)
            data_model_str = json.dumps(architecture.get("data_model", []), indent=2)
            impl_plan_str = json.dumps(architecture.get("implementation_plan", []), indent=2)

            prompt = (
                f"=== PROJECT IMPLEMENTATION REQUEST ===\n\n"
                f"Architecture Summary:\n{architecture.get('architecture_summary', '')}\n\n"
                f"Language: {lang} | Framework: {framework}\n\n"
                f"=== ALL FILES TO CREATE ===\n{file_tree_str}\n\n"
                f"=== COMPONENT RESPONSIBILITIES ===\n{components_str}\n\n"
                f"=== API ENDPOINTS (implement ALL of these) ===\n{api_str}\n\n"
                f"=== DATA MODELS (implement ALL tables/entities) ===\n{data_model_str}\n\n"
                f"=== IMPLEMENTATION PLAN ===\n{impl_plan_str}\n\n"
                f"=== SECURITY REQUIREMENTS (MANDATORY — NO EXCEPTIONS) ===\n"
                f"- Passwords: MUST use passlib with bcrypt. CryptContext(schemes=['bcrypt'], deprecated='auto')\n"
                f"- Auth: MUST implement JWT tokens using python-jose. Include create_access_token() and get_current_user().\n"
                f"- Protected routes: MUST use Depends(get_current_user) for write operations.\n"
                f"- Validation: MUST use Pydantic models with field validators for all inputs.\n"
                f"- Errors: MUST return proper HTTPException with status codes (400, 401, 403, 404, 409, 422).\n"
                + revision_context
                + "\n\n=== FINAL REMINDER ===\n"
                "Generate EVERY file with COMPLETE implementation. No stubs, no '# TODO', no '...'.\n"
                "Output ONLY the JSON: {\"files_created\": [...], \"implementation_notes\": \"...\", \"files_changed\": [...]}"
            )

            raw = await _generate_llm_json(
                state=state,
                prompt=prompt,
                system_prompt=DEVELOPER_SYSTEM_PROMPT,
                temperature=0.2,  # Lower = more deterministic, complete code
            )

            # Try to build output, recover from partial/invalid results
            if isinstance(raw, dict) and raw.get("files_created"):
                try:
                    output = DeveloperOutput(**raw)
                except Exception as schema_err:
                    logger.warning(f"[Developer] Schema validation partial failure: {schema_err}. Using raw files.")
                    output = DeveloperOutput(
                        files_created=raw.get("files_created", []),
                        implementation_notes=raw.get("implementation_notes", "Generated with schema warnings"),
                        files_changed=raw.get("files_changed", []),
                    )
            elif isinstance(raw, dict) and raw.get("raw_response"):
                # JSON parse failed completely — try regex recovery
                logger.warning("[Developer] JSON parse failed — attempting partial recovery from raw response")
                recovered = await _recover_partial_developer_output(raw["raw_response"])
                output = DeveloperOutput(**recovered)
            else:
                output = DeveloperOutput(**raw)

        except (OllamaError, GroqError) as e:
            logger.error(f"[Developer] LLM error: {e}")
            state["error_messages"] = state.get("error_messages", []) + [f"Developer LLM error: {e}"]
            output = DeveloperOutput(implementation_notes=f"Failed to generate code: {e}")
        except Exception as e:
            logger.error(f"[Developer] Unexpected error: {e}", exc_info=True)
            output = DeveloperOutput(implementation_notes=f"Development error: {e}")

    state["generated_files"] = output.model_dump()
    state["current_agent"] = "developer"
    state["agent_messages"] = state.get("agent_messages", []) + [
        {
            "agent": "developer",
            "type": "output",
            "content": f"Generated {len(output.files_created)} files. {output.implementation_notes}",
        }
    ]
    logger.info(f"[Developer] Completed. Files created: {len(output.files_created)}")
    return state




async def run_reviewer(state: dict[str, Any]) -> dict[str, Any]:
    """Code Reviewer agent - reviews implementation quality."""
    logger.info(f"[Reviewer] Starting for run {state.get('run_id')} (engine: {state.get('engine', 'local')})")
    generated_files = state.get("generated_files", {})
    requirements = state.get("requirements", {})
    revision_count = state.get("revision_count", 0)

    if state.get("demo_mode") and state.get("engine") == "demo":
        output = get_demo_reviewer_output(
            generated_files.get("files_created", []),
            iteration=revision_count,
        )
    else:
        try:
            files_summary = []
            for f in generated_files.get("files_created", [])[:10]:
                content = f.get("content", "")[:2000]
                files_summary.append(f"--- {f.get('path', 'unknown')} ---\n{content}")

            prompt = (
                f"Review this implementation against the requirements:\n\n"
                f"Requirements:\n" + "\n".join(f"- {r}" for r in requirements.get("requirements", []))
                + f"\n\nGenerated Files (showing first 10):\n\n" + "\n\n".join(files_summary)
                + f"\n\nRevision #{revision_count}. Previous issues addressed: {revision_count > 0}"
            )
            raw = await _generate_llm_json(
                state=state,
                prompt=prompt,
                system_prompt=REVIEWER_SYSTEM_PROMPT,
                temperature=0.2,
            )
            output = ReviewerOutput(**raw)
        except (OllamaError, GroqError) as e:
            logger.error(f"[Reviewer] LLM error: {e}")
            state["error_messages"] = state.get("error_messages", []) + [f"Reviewer LLM error: {e}"]
            output = ReviewerOutput(
                approval=True,
                summary=f"Review could not be performed: {e}. Proceeding with current code.",
                recommendation="APPROVE (review unavailable)",
            )
        except Exception as e:
            logger.error(f"[Reviewer] Unexpected error: {e}")
            output = ReviewerOutput(approval=True, summary=f"Review error: {e}")

    state["review_findings"] = [f.model_dump() if hasattr(f, 'model_dump') else f for f in output.findings]
    state["review_output"] = output.model_dump()
    state["current_agent"] = "reviewer"
    state["agent_messages"] = state.get("agent_messages", []) + [
        {
            "agent": "reviewer",
            "type": "output",
            "content": f"{'APPROVED' if output.approval else 'REVISION NEEDED'}: {output.summary}",
        }
    ]
    logger.info(f"[Reviewer] Completed. Approved: {output.approval}, Findings: {len(output.findings)}")
    return state


async def run_tester(state: dict[str, Any]) -> dict[str, Any]:
    """Testing agent - generates and evaluates tests."""
    logger.info(f"[Tester] Starting for run {state.get('run_id')} (engine: {state.get('engine', 'local')})")
    generated_files = state.get("generated_files", {})

    if state.get("demo_mode") and state.get("engine") == "demo":
        output = get_demo_tester_output(generated_files.get("files_created", []))
    else:
        try:
            files_summary = []
            for f in generated_files.get("files_created", [])[:10]:
                content = f.get("content", "")[:1500]
                files_summary.append(f"--- {f.get('path', 'unknown')} ---\n{content}")

            prompt = (
                f"Generate tests and verify the following implementation:\n\n"
                f"Files:\n\n" + "\n\n".join(files_summary)
                + f"\n\nNote: Docker sandbox is not available. "
                f"Perform static analysis and generate test files. "
                f"Mark tests as 'skipped' if they cannot be executed safely."
            )
            raw = await _generate_llm_json(
                state=state,
                prompt=prompt,
                system_prompt=TESTER_SYSTEM_PROMPT,
                temperature=0.2,
            )
            output = TesterOutput(**raw)
        except (OllamaError, GroqError) as e:
            logger.error(f"[Tester] LLM error: {e}")
            state["error_messages"] = state.get("error_messages", []) + [f"Tester LLM error: {e}"]
            output = TesterOutput(
                summary=f"Testing could not be performed: {e}",
                execution_method="unavailable",
            )
        except Exception as e:
            logger.error(f"[Tester] Unexpected error: {e}")
            output = TesterOutput(summary=f"Testing error: {e}")

    state["test_results"] = output.model_dump()
    state["current_agent"] = "tester"
    state["agent_messages"] = state.get("agent_messages", []) + [
        {
            "agent": "tester",
            "type": "output",
            "content": (
                f"Tests: {output.passed} passed, {output.failed} failed, "
                f"{output.skipped} skipped, {output.blocked} blocked. {output.summary}"
            ),
        }
    ]
    logger.info(
        f"[Tester] Completed. P:{output.passed} F:{output.failed} S:{output.skipped} B:{output.blocked}"
    )
    return state
