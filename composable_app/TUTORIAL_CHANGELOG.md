# Tutorial Maintenance Changelog

This document tracks tutorial updates needed when the `composable_app/` codebase changes. It serves as a maintenance log to ensure tutorials remain accurate and up-to-date.

---

## Maintenance Schedule

- **Monthly Review** (First 6 months): Check all tutorials for accuracy
- **Quarterly Review** (After 6 months): Deep review before major releases
- **On-Demand**: When code changes affect tutorial content

---

## Current Status

**Last Full Review**: 2025-11-04
**Tutorial Version**: 1.0
**Codebase Version**: Compatible with commit `5f9c1b4` (as of 2025-11-04)

**Status Legend**:
- ✅ **Up to date** - Tutorial matches current code
- ⏳ **Pending update** - Code changed, tutorial needs revision
- ⚠️ **Breaking change** - Major refactor requires tutorial rewrite
- 🔍 **Under review** - Being checked for accuracy

---

## Tutorial Status Summary

| Tutorial | Status | Last Updated | Notes |
|----------|--------|--------------|-------|
| TUTORIAL_INDEX.md | ✅ Up to date | 2025-11-04 | Initial creation |
| multi_agent_workflow.md | ⏳ Pending | - | Not yet created |
| rag_pattern_tutorial.ipynb | ⏳ Pending | - | Not yet created |
| llm_as_judge_tutorial.ipynb | ⏳ Pending | - | Not yet created |
| reflection_pattern.md | ⏳ Pending | - | Not yet created |
| multi_agent_pattern.ipynb | ⏳ Pending | - | Not yet created |
| horizontal_services.md | ⏳ Pending | - | Not yet created |
| prompt_engineering.md | ⏳ Pending | - | Not yet created |
| evaluation_tutorial.ipynb | ⏳ Pending | - | Not yet created |
| advanced_patterns.ipynb | ⏳ Pending | - | Not yet created |
| architecture_deep_dive.md | ⏳ Pending | - | Not yet created |

---

## Change Log

### 2025-11-04: Tutorial System Created
**Status**: ✅ Initial release
**Changes**:
- Created tutorial infrastructure (directories, TUTORIAL_INDEX.md, TUTORIAL_CHANGELOG.md)
- Established maintenance schedule
- Defined tutorial structure and format

**Affected Tutorials**: None yet (baseline)

---

## Monitoring Code Changes

### Files to Watch for Changes

**Agent Files** (High Impact):
- `agents/task_assigner.py` - Affects: multi_agent_workflow.md, llm_as_judge_tutorial.ipynb
- `agents/generic_writer_agent.py` - Affects: rag_pattern_tutorial.ipynb, reflection_pattern.md, architecture_deep_dive.md
- `agents/reviewer_panel.py` - Affects: multi_agent_pattern.ipynb, prompt_engineering.md
- `agents/article.py` - Affects: All tutorials mentioning Article dataclass

**Utility Files** (Medium Impact):
- `utils/guardrails.py` - Affects: llm_as_judge_tutorial.ipynb
- `utils/prompt_service.py` - Affects: prompt_engineering.md, horizontal_services.md
- `utils/long_term_memory.py` - Affects: horizontal_services.md
- `utils/save_for_eval.py` - Affects: evaluation_tutorial.ipynb
- `utils/llms.py` - Affects: advanced_patterns.ipynb

**Prompt Files** (Low Impact):
- `prompts/*.j2` - Affects: prompt_engineering.md (examples only, not critical)

**Documentation Files** (Reference Only):
- `ARCHITECTURE.md` - Cross-reference in tutorials
- `API_REFERENCE.md` - Cross-reference in tutorials

---

## Update Procedures

### When Code Changes Occur

1. **Identify Impact**:
   - Check which tutorials reference the changed file
   - Use GitHub line references in tutorials to find affected sections
   - Example: If `agents/generic_writer_agent.py:142-165` changes, search tutorials for this reference

2. **Update Tutorials**:
   - Update code line numbers if function moved
   - Revise explanations if implementation changed
   - Update Common Pitfalls if new issues emerged
   - Re-test notebooks if API changed

3. **Mark Changes**:
   - Add entry to this changelog with date, affected files, and tutorials
   - Update "Last Updated" in Tutorial Status Summary
   - Change status from ✅ to ⏳ for tutorials needing updates

4. **Verify Updates**:
   - Execute notebooks end-to-end
   - Check GitHub line links resolve correctly
   - Verify code snippets match current implementation

### Example: Handling a Code Refactor

**Scenario**: `agents/generic_writer_agent.py` refactored, GenAIWriter moved to separate file

**Steps**:
1. Identify affected tutorials:
   - `rag_pattern_tutorial.ipynb` (heavily references GenAIWriter)
   - `architecture_deep_dive.md` (mentions WriterFactory)

2. Update changelog:
   ```markdown
   ### 2025-11-15: GenAIWriter Refactored
   **Status**: ⚠️ Breaking change
   **Files Changed**: `agents/generic_writer_agent.py` → `agents/genai_writer.py`
   **Affected Tutorials**:
   - rag_pattern_tutorial.ipynb - Update imports and line references
   - architecture_deep_dive.md - Update WriterFactory section
   ```

3. Update tutorials:
   - Change imports from `from agents.generic_writer_agent import GenAIWriter`
   - Update line references: `agents/genai_writer.py:1-50` (new location)
   - Test notebook execution

4. Mark complete:
   - Change status back to ✅
   - Update "Last Updated" dates

---

## Tutorial Dependencies

### Tutorial → Code File Mapping

**rag_pattern_tutorial.ipynb**:
- `agents/generic_writer_agent.py` (lines 142-165)
- `utils/llms.py` (embedding configuration)
- `data/create_index.py` (vector store setup)

**llm_as_judge_tutorial.ipynb**:
- `agents/task_assigner.py` (lines 31-33, 65-67)
- `utils/guardrails.py` (lines 14-43)

**multi_agent_pattern.ipynb**:
- `agents/reviewer_panel.py` (entire file)
- `agents/generic_writer_agent.py` (AbstractWriter interface)

**reflection_pattern.md**:
- `agents/generic_writer_agent.py` (lines 74-89)

**horizontal_services.md**:
- `utils/prompt_service.py` (lines 14-27)
- `utils/guardrails.py` (entire file)
- `utils/long_term_memory.py` (entire file)
- `utils/save_for_eval.py` (entire file)

**prompt_engineering.md**:
- `utils/prompt_service.py` (lines 14-27)
- `prompts/*.j2` (all template files)

**evaluation_tutorial.ipynb**:
- `evals/evaluate_keywords.py` (entire file)
- `utils/save_for_eval.py` (logging format)

**advanced_patterns.ipynb**:
- `utils/llms.py` (entire file)

**architecture_deep_dive.md**:
- `agents/generic_writer_agent.py` (lines 38-58, 167-179)
- Entire codebase (architectural overview)

---

## GitHub Issue Template

Use this template when creating issues for tutorial updates:

```markdown
## Tutorial Update Needed

**Tutorial**: [Name of tutorial file]
**Reason**: [Code change / Bug / Clarification request]
**Priority**: [High / Medium / Low]

### Changes Needed
- [ ] Update code line references
- [ ] Revise explanations
- [ ] Update Common Pitfalls
- [ ] Re-test notebook execution
- [ ] Verify GitHub links

### Files Affected
- `path/to/file.py` (lines X-Y)

### Additional Context
[Any other relevant information]
```

---

## Maintenance Guidelines

### Before Making Code Changes

1. **Check tutorial dependencies**: See "Tutorial → Code File Mapping" above
2. **Consider impact**: Will this break existing tutorials?
3. **Plan tutorial updates**: Schedule tutorial revisions alongside code changes

### After Making Code Changes

1. **Update this changelog**: Add entry with date, files, affected tutorials
2. **Create GitHub issues**: One issue per tutorial needing updates
3. **Assign priority**:
   - High: Tutorial execution fails or produces wrong results
   - Medium: Code references outdated but examples still work
   - Low: Minor clarifications or optimization tips

### Tutorial Review Checklist

Use this when reviewing tutorials for accuracy:

- [ ] All code line references resolve correctly on GitHub
- [ ] Notebooks execute end-to-end without errors
- [ ] API costs estimates are accurate
- [ ] Common Pitfalls reflect current issues
- [ ] Book chapter references are correct
- [ ] Diagrams match current architecture
- [ ] Links to other tutorials work
- [ ] Prerequisites are up to date

---

## Contact & Support

**Maintainer**: AI Design Patterns Tutorial Team
**Report Issues**: [GitHub Issues](https://github.com/lakshmanok/generative-ai-design-patterns/issues)
**Tutorial Questions**: See [TUTORIAL_INDEX.md](TUTORIAL_INDEX.md#troubleshooting)

---

**Last Updated**: 2025-11-04
**Changelog Version**: 1.0
