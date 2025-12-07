# Code Execution & Security Patterns

## Template 1: Sandboxed Code Execution

```python
"""
Sandboxed Code Execution Pattern
--------------------------------
Execute LLM-generated code safely with resource limits.
"""

import subprocess
import tempfile
import asyncio
from pathlib import Path
from dataclasses import dataclass
from typing import Optional, Union
from enum import Enum


class DSLType(str, Enum):
    PYTHON = "python"
    SQL = "sql"
    GRAPHVIZ = "graphviz"
    MERMAID = "mermaid"
    JAVASCRIPT = "javascript"


@dataclass
class ExecutionConfig:
    timeout_seconds: int = 30
    max_memory_mb: int = 512
    allow_network: bool = False
    allow_filesystem: bool = False


@dataclass
class ExecutionResult:
    success: bool
    output: Union[str, bytes]
    error: Optional[str] = None
    execution_time: float = 0.0


class CodeSandbox:
    """
    Secure sandbox for executing LLM-generated code.
    
    Uses Docker containers for isolation when available,
    falls back to subprocess with resource limits.
    """
    
    def __init__(self, config: ExecutionConfig = None):
        self.config = config or ExecutionConfig()
        self.docker_available = self._check_docker()
    
    def _check_docker(self) -> bool:
        try:
            subprocess.run(
                ["docker", "--version"],
                capture_output=True,
                timeout=5
            )
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False
    
    async def execute(
        self,
        code: str,
        dsl_type: DSLType,
        input_files: dict = None
    ) -> ExecutionResult:
        """
        Execute code in sandbox and return result.
        
        Args:
            code: The LLM-generated code to execute
            dsl_type: Type of code (python, sql, graphviz, etc.)
            input_files: Optional dict of {filename: content} to include
            
        Returns:
            ExecutionResult with output or error
        """
        
        # Validate code before execution (basic security check)
        validation_result = self._validate_code(code, dsl_type)
        if not validation_result["valid"]:
            return ExecutionResult(
                success=False,
                output="",
                error=f"Code validation failed: {validation_result['reason']}"
            )
        
        if self.docker_available:
            return await self._execute_docker(code, dsl_type, input_files)
        else:
            return await self._execute_subprocess(code, dsl_type, input_files)
    
    def _validate_code(self, code: str, dsl_type: DSLType) -> dict:
        """Basic security validation of code."""
        
        # Blocked patterns for different DSL types
        blocked_patterns = {
            DSLType.PYTHON: [
                "import os",
                "import subprocess",
                "import sys",
                "__import__",
                "exec(",
                "eval(",
                "open(",
                "socket",
                "requests",
                "urllib",
            ],
            DSLType.SQL: [
                "DROP",
                "DELETE FROM",
                "TRUNCATE",
                "UPDATE",
                "INSERT INTO",
                "--",  # SQL comment injection
                ";",   # Statement terminator (if not expected)
            ],
            DSLType.JAVASCRIPT: [
                "require(",
                "import ",
                "fetch(",
                "XMLHttpRequest",
                "eval(",
                "Function(",
            ]
        }
        
        patterns = blocked_patterns.get(dsl_type, [])
        
        for pattern in patterns:
            if pattern.lower() in code.lower():
                return {
                    "valid": False,
                    "reason": f"Blocked pattern detected: {pattern}"
                }
        
        return {"valid": True, "reason": None}
    
    async def _execute_docker(
        self,
        code: str,
        dsl_type: DSLType,
        input_files: dict
    ) -> ExecutionResult:
        """Execute in Docker container for maximum isolation."""
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Write code file
            code_file = self._write_code_file(tmpdir, code, dsl_type)
            
            # Write any input files
            if input_files:
                for name, content in input_files.items():
                    (tmpdir / name).write_text(content)
            
            # Build Docker command
            docker_cmd = [
                "docker", "run",
                "--rm",
                f"--memory={self.config.max_memory_mb}m",
                f"--cpus=1",
                "--network=none" if not self.config.allow_network else "",
                "-v", f"{tmpdir}:/workspace:ro",
                "-w", "/workspace",
                self._get_docker_image(dsl_type),
            ] + self._get_execution_command(dsl_type, code_file.name)
            
            # Remove empty strings
            docker_cmd = [c for c in docker_cmd if c]
            
            try:
                start_time = asyncio.get_event_loop().time()
                
                process = await asyncio.create_subprocess_exec(
                    *docker_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=self.config.timeout_seconds
                )
                
                execution_time = asyncio.get_event_loop().time() - start_time
                
                if process.returncode != 0:
                    return ExecutionResult(
                        success=False,
                        output="",
                        error=stderr.decode(),
                        execution_time=execution_time
                    )
                
                # Check for output file (for graphviz, mermaid, etc.)
                output = self._read_output(tmpdir, dsl_type, stdout)
                
                return ExecutionResult(
                    success=True,
                    output=output,
                    execution_time=execution_time
                )
                
            except asyncio.TimeoutError:
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Execution timed out after {self.config.timeout_seconds}s"
                )
    
    async def _execute_subprocess(
        self,
        code: str,
        dsl_type: DSLType,
        input_files: dict
    ) -> ExecutionResult:
        """Fallback execution via subprocess (less isolated)."""
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            code_file = self._write_code_file(tmpdir, code, dsl_type)
            
            if input_files:
                for name, content in input_files.items():
                    (tmpdir / name).write_text(content)
            
            cmd = self._get_execution_command(dsl_type, str(code_file))
            
            try:
                start_time = asyncio.get_event_loop().time()
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    timeout=self.config.timeout_seconds,
                    cwd=tmpdir
                )
                
                execution_time = asyncio.get_event_loop().time() - start_time
                
                if result.returncode != 0:
                    return ExecutionResult(
                        success=False,
                        output="",
                        error=result.stderr.decode(),
                        execution_time=execution_time
                    )
                
                output = self._read_output(tmpdir, dsl_type, result.stdout)
                
                return ExecutionResult(
                    success=True,
                    output=output,
                    execution_time=execution_time
                )
                
            except subprocess.TimeoutExpired:
                return ExecutionResult(
                    success=False,
                    output="",
                    error=f"Execution timed out after {self.config.timeout_seconds}s"
                )
    
    def _write_code_file(self, tmpdir: Path, code: str, dsl_type: DSLType) -> Path:
        extensions = {
            DSLType.PYTHON: ".py",
            DSLType.SQL: ".sql",
            DSLType.GRAPHVIZ: ".dot",
            DSLType.MERMAID: ".mmd",
            DSLType.JAVASCRIPT: ".js",
        }
        ext = extensions.get(dsl_type, ".txt")
        code_file = tmpdir / f"code{ext}"
        code_file.write_text(code)
        return code_file
    
    def _get_docker_image(self, dsl_type: DSLType) -> str:
        images = {
            DSLType.PYTHON: "python:3.11-slim",
            DSLType.GRAPHVIZ: "nshine/dot",
            DSLType.MERMAID: "minlag/mermaid-cli",
            DSLType.JAVASCRIPT: "node:20-slim",
        }
        return images.get(dsl_type, "python:3.11-slim")
    
    def _get_execution_command(self, dsl_type: DSLType, code_file: str) -> list:
        commands = {
            DSLType.PYTHON: ["python", code_file],
            DSLType.GRAPHVIZ: ["dot", "-Tpng", code_file, "-o", "output.png"],
            DSLType.MERMAID: ["mmdc", "-i", code_file, "-o", "output.png"],
            DSLType.JAVASCRIPT: ["node", code_file],
        }
        return commands.get(dsl_type, ["cat", code_file])
    
    def _read_output(
        self, 
        tmpdir: Path, 
        dsl_type: DSLType, 
        stdout: bytes
    ) -> Union[str, bytes]:
        # Check for binary output files
        output_file = tmpdir / "output.png"
        if output_file.exists():
            return output_file.read_bytes()
        
        return stdout.decode() if stdout else ""


# Prompt template for code generation
CODE_GENERATION_PROMPT = """
Generate {dsl_type} code to accomplish the following task.
Output ONLY the code with no explanation or markdown.

## Task
{task}

## Constraints
- Do not use any network operations
- Do not access the filesystem beyond the current directory
- Keep execution under 30 seconds
- Handle edge cases gracefully

## Example
Input: {example_input}
Output:
{example_output}

## Your Task
Input: {user_input}
Output:
"""


class CodeGenerationAgent:
    """Agent that generates and executes code via LLM."""
    
    def __init__(self, llm, sandbox: CodeSandbox = None):
        self.llm = llm
        self.sandbox = sandbox or CodeSandbox()
    
    async def generate_and_execute(
        self,
        task: str,
        dsl_type: DSLType,
        examples: list = None,
        max_retries: int = 3
    ) -> dict:
        """
        Generate code from natural language and execute it.
        Uses reflection to fix errors and retry.
        """
        
        # Build prompt with examples
        example_input = examples[0]["input"] if examples else ""
        example_output = examples[0]["output"] if examples else ""
        
        prompt = CODE_GENERATION_PROMPT.format(
            dsl_type=dsl_type.value,
            task=task,
            example_input=example_input,
            example_output=example_output,
            user_input=task
        )
        
        for attempt in range(max_retries):
            # Generate code
            code = await self.llm.generate(prompt)
            code = self._clean_code(code)
            
            # Execute
            result = await self.sandbox.execute(code, dsl_type)
            
            if result.success:
                return {
                    "success": True,
                    "code": code,
                    "output": result.output,
                    "attempts": attempt + 1
                }
            
            # Reflection: add error to prompt for retry
            prompt = f"""
            The previous code failed with this error:
            {result.error}
            
            Original task: {task}
            
            Previous code:
            {code}
            
            Fix the code and try again. Output ONLY the corrected code.
            """
        
        return {
            "success": False,
            "code": code,
            "error": result.error,
            "attempts": max_retries
        }
    
    def _clean_code(self, code: str) -> str:
        """Remove markdown formatting from LLM output."""
        code = code.strip()
        if code.startswith("```"):
            lines = code.split("\n")
            code = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])
        return code
```

## Template 2: Security Patterns for Prompt Injection Defense

```python
"""
Prompt Injection Defense Patterns
---------------------------------
Implementations of the 6 security patterns from Beurer-Kellner et al. (2025)
"""

from dataclasses import dataclass
from typing import List, Callable, Any, Optional
from enum import Enum


# =============================================================================
# Pattern 1: Action-Selector
# Predefined action set, no feedback to agent
# =============================================================================

class ActionSelector:
    """
    Only allows predefined actions. Tool outputs are not fed back to agent.
    Prevents injection via third-party tool responses.
    """
    
    def __init__(self, allowed_actions: dict):
        """
        Args:
            allowed_actions: Dict of {action_name: action_function}
        """
        self.actions = allowed_actions
    
    async def execute(self, llm, user_request: str) -> dict:
        """Execute request with action selection (no feedback loop)."""
        
        # Step 1: LLM selects action (one-shot, no feedback)
        selection_prompt = f"""
        Select ONE action to perform for this request.
        
        Available actions: {list(self.actions.keys())}
        
        Request: {user_request}
        
        Respond with only the action name and parameters in this format:
        ACTION: action_name
        PARAMS: param1=value1, param2=value2
        """
        
        response = await llm.generate(selection_prompt)
        action_name, params = self._parse_response(response)
        
        # Step 2: Validate action is allowed
        if action_name not in self.actions:
            return {"error": f"Action '{action_name}' not allowed"}
        
        # Step 3: Execute action (result NOT sent back to LLM)
        action_fn = self.actions[action_name]
        result = await action_fn(**params)
        
        # Return result directly to user, bypassing LLM
        return {"action": action_name, "result": result}
    
    def _parse_response(self, response: str) -> tuple:
        # Parse ACTION: and PARAMS: from response
        action = ""
        params = {}
        for line in response.split("\n"):
            if line.startswith("ACTION:"):
                action = line.replace("ACTION:", "").strip()
            elif line.startswith("PARAMS:"):
                param_str = line.replace("PARAMS:", "").strip()
                for pair in param_str.split(","):
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        params[k.strip()] = v.strip()
        return action, params


# =============================================================================
# Pattern 2: Plan-Then-Execute
# Fixed plan created upfront, executed without deviation
# =============================================================================

@dataclass
class PlanStep:
    action: str
    params: dict
    description: str


class PlanThenExecute:
    """
    Creates an immutable plan before execution.
    Tool feedback cannot modify the plan.
    """
    
    def __init__(self, tools: dict):
        self.tools = tools
    
    async def execute(self, llm, user_request: str) -> dict:
        """Create fixed plan, then execute without LLM re-evaluation."""
        
        # Phase 1: Create immutable plan
        plan = await self._create_plan(llm, user_request)
        
        # Phase 2: Execute plan steps sequentially
        results = []
        context = {}
        
        for step in plan:
            if step.action not in self.tools:
                results.append({"step": step.action, "error": "Unknown action"})
                continue
            
            tool = self.tools[step.action]
            
            # Execute step (NO LLM involvement)
            try:
                result = await tool(**step.params, context=context)
                results.append({"step": step.action, "result": result})
                context[step.action] = result
            except Exception as e:
                results.append({"step": step.action, "error": str(e)})
        
        return {"plan": [s.description for s in plan], "results": results}
    
    async def _create_plan(self, llm, request: str) -> List[PlanStep]:
        """Create plan (only LLM involvement in entire flow)."""
        
        plan_prompt = f"""
        Create a step-by-step plan to complete this request.
        This plan CANNOT be modified once created.
        
        Available tools: {list(self.tools.keys())}
        
        Request: {request}
        
        Output format (one per line):
        STEP: tool_name | param1=value1, param2=value2 | description
        """
        
        response = await llm.generate(plan_prompt)
        
        steps = []
        for line in response.split("\n"):
            if line.startswith("STEP:"):
                parts = line.replace("STEP:", "").split("|")
                if len(parts) >= 3:
                    action = parts[0].strip()
                    params = self._parse_params(parts[1])
                    desc = parts[2].strip()
                    steps.append(PlanStep(action, params, desc))
        
        return steps
    
    def _parse_params(self, param_str: str) -> dict:
        params = {}
        for pair in param_str.split(","):
            if "=" in pair:
                k, v = pair.split("=", 1)
                params[k.strip()] = v.strip()
        return params


# =============================================================================
# Pattern 3: Dual-LLM Architecture
# Privileged LLM plans, sandboxed LLM processes untrusted data
# =============================================================================

class DualLLM:
    """
    Separates privileged (tool access) and sandboxed (no tools) LLMs.
    Untrusted data is only processed by sandboxed LLM.
    """
    
    def __init__(self, privileged_llm, sandboxed_llm, tools: dict):
        self.privileged = privileged_llm
        self.sandboxed = sandboxed_llm
        self.tools = tools
    
    async def execute(
        self, 
        user_request: str, 
        untrusted_data: str = None
    ) -> dict:
        """Process request with security separation."""
        
        # Step 1: Sandboxed LLM extracts info from untrusted data
        extracted_info = None
        if untrusted_data:
            extracted_info = await self._sandboxed_extract(untrusted_data)
        
        # Step 2: Privileged LLM plans with sanitized data
        plan = await self._privileged_plan(user_request, extracted_info)
        
        # Step 3: Execute plan (privileged LLM orchestrates)
        results = await self._privileged_execute(plan)
        
        return {"extracted_info": extracted_info, "plan": plan, "results": results}
    
    async def _sandboxed_extract(self, data: str) -> dict:
        """Extract structured info using sandboxed (no tools) LLM."""
        
        prompt = f"""
        Extract structured information from this data.
        Output as key: value pairs, one per line.
        
        Data:
        {data}
        """
        
        # Sandboxed LLM has NO tool access
        response = await self.sandboxed.generate(prompt, tools=[])
        
        # Parse response into safe structure
        info = {}
        for line in response.split("\n"):
            if ":" in line:
                k, v = line.split(":", 1)
                # Sanitize extracted values
                info[k.strip()] = self._sanitize(v.strip())
        
        return info
    
    async def _privileged_plan(
        self, 
        request: str, 
        extracted_info: dict
    ) -> List[dict]:
        """Create execution plan using privileged LLM."""
        
        prompt = f"""
        Create a plan to complete this request.
        
        Request: {request}
        
        Available context (pre-validated):
        {extracted_info or 'None'}
        
        Available tools: {list(self.tools.keys())}
        """
        
        return await self.privileged.generate(prompt)
    
    async def _privileged_execute(self, plan: List[dict]) -> List[dict]:
        """Execute plan steps using privileged LLM."""
        # Implementation of plan execution
        pass
    
    def _sanitize(self, value: str) -> str:
        """Remove potentially dangerous content from extracted values."""
        # Remove common injection patterns
        dangerous = [
            "ignore previous",
            "disregard",
            "new instructions",
            "system:",
            "<|",
            "|>"
        ]
        clean = value
        for pattern in dangerous:
            clean = clean.replace(pattern.lower(), "[REMOVED]")
        return clean


# =============================================================================
# Pattern 4: Context Minimization
# Remove unnecessary context in subsequent steps
# =============================================================================

class ContextMinimizer:
    """
    Reduces context passed between steps to minimize injection surface.
    """
    
    def __init__(self, llm, tools: dict):
        self.llm = llm
        self.tools = tools
    
    async def execute_steps(
        self, 
        steps: List[dict], 
        initial_context: dict
    ) -> List[dict]:
        """Execute steps with minimal context passing."""
        
        results = []
        
        for i, step in enumerate(steps):
            # Minimize context for this step
            step_context = self._minimize_context(
                step_number=i,
                step_type=step.get("type"),
                full_context=initial_context,
                previous_results=results
            )
            
            # Execute step with minimized context
            result = await self._execute_step(step, step_context)
            results.append(result)
        
        return results
    
    def _minimize_context(
        self,
        step_number: int,
        step_type: str,
        full_context: dict,
        previous_results: List[dict]
    ) -> dict:
        """
        Return only the context necessary for this step.
        Key insight: Remove original user prompt after step 0.
        """
        
        minimal = {}
        
        # Step 0 needs original request
        if step_number == 0:
            minimal["user_request"] = full_context.get("user_request")
        
        # Only include relevant previous results
        relevant_keys = self._get_relevant_keys(step_type)
        for key in relevant_keys:
            if key in full_context:
                minimal[key] = full_context[key]
        
        # Include only immediately previous result
        if previous_results:
            minimal["previous_result"] = previous_results[-1].get("output")
        
        return minimal
    
    def _get_relevant_keys(self, step_type: str) -> List[str]:
        """Define which context keys are relevant for each step type."""
        relevance_map = {
            "search": ["query_terms"],
            "analyze": ["data_format", "analysis_type"],
            "write": ["style", "length"],
            "review": ["criteria"],
        }
        return relevance_map.get(step_type, [])
    
    async def _execute_step(self, step: dict, context: dict) -> dict:
        """Execute a single step with minimal context."""
        tool = self.tools.get(step["type"])
        if tool:
            return await tool(**step.get("params", {}), context=context)
        return {"error": f"Unknown step type: {step['type']}"}


# =============================================================================
# Pattern 5: Map-Reduce for Untrusted Data
# Isolated processing of untrusted chunks
# =============================================================================

class MapReduceProcessor:
    """
    Process untrusted data in isolated chunks.
    Each chunk processed by sandboxed agent, then aggregated safely.
    """
    
    def __init__(self, sandboxed_llm, aggregator_llm):
        self.sandboxed = sandboxed_llm
        self.aggregator = aggregator_llm
    
    async def process(
        self,
        data_chunks: List[str],
        map_instruction: str,
        reduce_instruction: str
    ) -> dict:
        """
        Map: Process each chunk in isolation with sandboxed LLM.
        Reduce: Aggregate results with limited LLM (no arbitrary actions).
        """
        
        # Map phase: Process chunks in parallel, isolated
        import asyncio
        map_tasks = [
            self._map_chunk(chunk, map_instruction)
            for chunk in data_chunks
        ]
        mapped_results = await asyncio.gather(*map_tasks)
        
        # Filter out any potentially injected content
        safe_results = [self._sanitize_result(r) for r in mapped_results]
        
        # Reduce phase: Aggregate with constrained LLM
        final_result = await self._reduce(safe_results, reduce_instruction)
        
        return {
            "mapped_count": len(safe_results),
            "result": final_result
        }
    
    async def _map_chunk(self, chunk: str, instruction: str) -> str:
        """Process single chunk with sandboxed LLM (no tools)."""
        
        prompt = f"""
        {instruction}
        
        Data:
        {chunk}
        
        Output only the extracted/processed result, nothing else.
        """
        
        return await self.sandboxed.generate(prompt, tools=[])
    
    async def _reduce(self, results: List[str], instruction: str) -> str:
        """Aggregate results using constrained Action-Selector style."""
        
        # Format results without original data
        formatted = "\n".join(f"Result {i+1}: {r}" for i, r in enumerate(results))
        
        prompt = f"""
        {instruction}
        
        Individual results:
        {formatted}
        
        Provide a single aggregated result.
        """
        
        return await self.aggregator.generate(prompt)
    
    def _sanitize_result(self, result: str) -> str:
        """Remove potential injection attempts from mapped results."""
        # Limit length to prevent context overflow attacks
        max_length = 1000
        result = result[:max_length]
        
        # Remove suspicious patterns
        suspicious = ["SYSTEM:", "USER:", "ASSISTANT:", "<|", "|>"]
        for pattern in suspicious:
            result = result.replace(pattern, "")
        
        return result


# =============================================================================
# Combined Security Wrapper
# =============================================================================

class SecureAgentWrapper:
    """
    Wraps any agent with security patterns.
    Choose patterns based on threat model.
    """
    
    def __init__(
        self,
        agent,
        pattern: str = "dual_llm",  # action_selector, plan_execute, dual_llm, etc.
        config: dict = None
    ):
        self.agent = agent
        self.pattern = pattern
        self.config = config or {}
    
    async def execute(self, request: str, **kwargs) -> dict:
        """Execute request with security pattern applied."""
        
        if self.pattern == "action_selector":
            return await self._action_selector_execute(request, **kwargs)
        elif self.pattern == "plan_execute":
            return await self._plan_execute(request, **kwargs)
        elif self.pattern == "dual_llm":
            return await self._dual_llm_execute(request, **kwargs)
        elif self.pattern == "context_min":
            return await self._context_min_execute(request, **kwargs)
        else:
            # Default: pass through with basic sanitization
            sanitized = self._sanitize_input(request)
            return await self.agent.execute(sanitized, **kwargs)
    
    def _sanitize_input(self, text: str) -> str:
        """Basic input sanitization."""
        # Remove common injection patterns
        patterns = [
            "ignore all previous instructions",
            "disregard your instructions",
            "you are now",
            "new system prompt",
            "```system",
        ]
        clean = text
        for p in patterns:
            if p.lower() in clean.lower():
                clean = clean.lower().replace(p.lower(), "[FILTERED]")
        return clean
```
