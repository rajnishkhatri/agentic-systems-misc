# Multiagent Collaboration Templates

## Template 1: Review Panel with Round-Robin Discussion

```python
"""
Review Panel Pattern
--------------------
Multiple agents with different perspectives review content collaboratively.
Uses round-robin discussion followed by synthesis.
"""

from ag2 import ConversableAgent, RoundRobinPattern, initiate_group_chat
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ReviewerConfig:
    name: str
    role: str
    system_prompt: str
    focus_areas: List[str]


# Define your review panel
REVIEWER_CONFIGS = [
    ReviewerConfig(
        name="technical_reviewer",
        role="Technical Accuracy",
        system_prompt="""You are a technical reviewer focused on accuracy and completeness.
        
Your responsibilities:
- Verify all technical claims are correct
- Check for missing important details
- Identify potential misunderstandings
- Flag outdated information

When reviewing, be specific about issues and suggest corrections.""",
        focus_areas=["accuracy", "completeness", "technical depth"]
    ),
    ReviewerConfig(
        name="clarity_reviewer",
        role="Clarity & Readability",
        system_prompt="""You are a clarity reviewer focused on readability and comprehension.

Your responsibilities:
- Ensure content is clear and well-organized
- Identify jargon that needs explanation
- Check logical flow of ideas
- Suggest simplifications where helpful

Focus on making content accessible to the target audience.""",
        focus_areas=["clarity", "organization", "accessibility"]
    ),
    ReviewerConfig(
        name="bias_reviewer",
        role="Balance & Fairness",
        system_prompt="""You are a bias reviewer focused on balanced perspectives.

Your responsibilities:
- Identify potential biases or one-sided presentations
- Check for inclusive language
- Ensure diverse perspectives are represented
- Flag assumptions that may not be universal

Promote fair and balanced content.""",
        focus_areas=["balance", "inclusivity", "fairness"]
    ),
    ReviewerConfig(
        name="secretary",
        role="Synthesis",
        system_prompt="""You are the panel secretary responsible for synthesizing feedback.

Your responsibilities:
- Listen to all reviewers' feedback
- Identify common themes and disagreements
- Prioritize actionable items
- Create a clear, consolidated list of revisions

Output format:
1. Summary of key issues
2. Prioritized list of required changes
3. Suggested improvements (optional)
4. Points of disagreement to flag for human review""",
        focus_areas=["synthesis", "prioritization", "actionable feedback"]
    ),
]


class ReviewPanel:
    def __init__(self, llm_config: dict, reviewer_configs: List[ReviewerConfig] = None):
        self.llm_config = llm_config
        self.configs = reviewer_configs or REVIEWER_CONFIGS
        self.reviewers = self._create_reviewers()
    
    def _create_reviewers(self) -> List[ConversableAgent]:
        reviewers = []
        for config in self.configs:
            agent = ConversableAgent(
                name=config.name,
                system_message=config.system_prompt,
                llm_config=self.llm_config
            )
            reviewers.append(agent)
        return reviewers
    
    async def review(
        self, 
        content: str, 
        context: str = "",
        max_discussion_rounds: int = None
    ) -> dict:
        """
        Run a collaborative review of the content.
        
        Args:
            content: The content to review
            context: Additional context (target audience, purpose, etc.)
            max_discussion_rounds: Override default (each reviewer speaks once)
            
        Returns:
            dict with 'discussion' (full transcript) and 'synthesis' (final feedback)
        """
        rounds = max_discussion_rounds or len(self.reviewers) + 1
        
        pattern = RoundRobinPattern(
            initial_agent=self.reviewers[0],
            agents=self.reviewers,
            group_manager_args={"llm_config": self.llm_config}
        )
        
        review_prompt = f"""
        You are part of a content review panel. Please review the following content
        and provide feedback from your specific perspective.
        
        ## Context
        {context}
        
        ## Content to Review
        {content}
        
        ## Instructions
        - Focus on your area of expertise
        - Be specific and constructive
        - Respond to points raised by other reviewers
        - The secretary will synthesize all feedback at the end
        """
        
        reviews, context_out, last_agent = initiate_group_chat(
            pattern=pattern,
            max_rounds=rounds,
            messages=review_prompt
        )
        
        return {
            "discussion": reviews.chat_history,
            "synthesis": reviews.chat_history[-1]["content"],
            "reviewers": [r.name for r in self.reviewers]
        }


# Usage example
async def main():
    llm_config = {
        "model": "claude-sonnet-4-20250514",
        "api_key": "your-key"
    }
    
    panel = ReviewPanel(llm_config)
    
    content = """
    Machine learning models can predict customer churn with 95% accuracy.
    Companies should implement these models immediately to reduce customer loss.
    The ROI is typically 10x within the first month.
    """
    
    result = await panel.review(
        content=content,
        context="Blog post for small business owners, non-technical audience"
    )
    
    print("=== Synthesis ===")
    print(result["synthesis"])
```

## Template 2: Hierarchical Task Decomposition

```python
"""
Hierarchical Executive-Worker Pattern
--------------------------------------
An executive agent plans and delegates to specialized workers.
"""

from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum


class TaskType(str, Enum):
    RESEARCH = "research"
    ANALYSIS = "analysis"
    WRITING = "writing"
    CODE = "code"
    REVIEW = "review"


class SubTask(BaseModel):
    id: str
    type: TaskType
    description: str
    dependencies: List[str] = Field(default_factory=list)
    priority: int = Field(ge=1, le=5)


class TaskPlan(BaseModel):
    original_task: str
    subtasks: List[SubTask]
    execution_order: List[str]
    estimated_steps: int


class ExecutiveAgent:
    """Plans and coordinates work across specialized workers."""
    
    def __init__(self, llm, workers: dict):
        self.llm = llm
        self.workers = workers
        self.completed_tasks = {}
    
    async def plan(self, task: str) -> TaskPlan:
        """Decompose a complex task into subtasks."""
        
        planning_prompt = f"""
        You are a task planning executive. Decompose this task into subtasks
        that can be handled by specialized workers.
        
        ## Available Workers
        - research: Gathers information and facts
        - analysis: Analyzes data and draws conclusions
        - writing: Creates written content
        - code: Writes and reviews code
        - review: Quality checks and validation
        
        ## Task
        {task}
        
        ## Requirements
        - Break into 3-7 subtasks
        - Identify dependencies between subtasks
        - Prioritize by importance (1=low, 5=critical)
        - Ensure logical execution order
        
        Respond with a structured task plan.
        """
        
        response = await self.llm.generate(
            prompt=planning_prompt,
            response_format=TaskPlan
        )
        
        return response
    
    async def execute(self, task: str) -> dict:
        """Plan and execute a complex task."""
        
        # Step 1: Create the plan
        plan = await self.plan(task)
        
        results = {}
        
        # Step 2: Execute subtasks in order
        for task_id in plan.execution_order:
            subtask = next(t for t in plan.subtasks if t.id == task_id)
            
            # Gather dependency results
            context = {
                dep: results[dep] 
                for dep in subtask.dependencies 
                if dep in results
            }
            
            # Delegate to appropriate worker
            worker = self.workers.get(subtask.type)
            if worker:
                result = await worker.execute(
                    task=subtask.description,
                    context=context
                )
                results[task_id] = result
            else:
                results[task_id] = {"error": f"No worker for {subtask.type}"}
        
        # Step 3: Synthesize final result
        synthesis = await self._synthesize(task, plan, results)
        
        return {
            "plan": plan,
            "subtask_results": results,
            "final_result": synthesis
        }
    
    async def _synthesize(self, original_task: str, plan: TaskPlan, results: dict) -> str:
        """Combine subtask results into final output."""
        
        synthesis_prompt = f"""
        You are synthesizing the results of a multi-step task.
        
        ## Original Task
        {original_task}
        
        ## Completed Subtasks and Results
        {self._format_results(plan, results)}
        
        ## Instructions
        Combine these results into a coherent final response that addresses
        the original task completely.
        """
        
        return await self.llm.generate(synthesis_prompt)
    
    def _format_results(self, plan: TaskPlan, results: dict) -> str:
        formatted = []
        for subtask in plan.subtasks:
            result = results.get(subtask.id, "Not completed")
            formatted.append(f"### {subtask.id}: {subtask.description}\n{result}\n")
        return "\n".join(formatted)


class SpecializedWorker:
    """Worker agent specialized in a specific task type."""
    
    def __init__(self, worker_type: TaskType, llm, tools: list = None):
        self.worker_type = worker_type
        self.llm = llm
        self.tools = tools or []
        self.system_prompt = self._get_system_prompt()
    
    def _get_system_prompt(self) -> str:
        prompts = {
            TaskType.RESEARCH: """You are a research specialist. Your job is to 
                gather relevant information, find facts, and identify sources.
                Be thorough but focused on what's relevant.""",
            
            TaskType.ANALYSIS: """You are an analysis specialist. Your job is to
                examine data, identify patterns, draw conclusions, and provide insights.
                Be rigorous and evidence-based.""",
            
            TaskType.WRITING: """You are a writing specialist. Your job is to
                create clear, engaging, well-structured content.
                Adapt your style to the target audience.""",
            
            TaskType.CODE: """You are a coding specialist. Your job is to
                write clean, efficient, well-documented code.
                Follow best practices and handle edge cases.""",
            
            TaskType.REVIEW: """You are a review specialist. Your job is to
                validate quality, check for errors, and ensure completeness.
                Be thorough but constructive."""
        }
        return prompts.get(self.worker_type, "You are a helpful assistant.")
    
    async def execute(self, task: str, context: dict = None) -> str:
        """Execute a task with optional context from dependencies."""
        
        context_str = ""
        if context:
            context_str = "\n## Context from Previous Steps\n"
            for key, value in context.items():
                context_str += f"### {key}\n{value}\n"
        
        prompt = f"""
        {self.system_prompt}
        
        {context_str}
        
        ## Your Task
        {task}
        
        Complete this task to the best of your ability.
        """
        
        return await self.llm.generate(prompt)
```

## Template 3: Market-Based Task Auction

```python
"""
Market-Based Auction Pattern
----------------------------
Agents bid on tasks based on their capability and resources.
Best for dynamic workload distribution.
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import asyncio


@dataclass
class Bid:
    agent_name: str
    bid_value: float
    confidence: float
    estimated_time: float
    reasoning: str


@dataclass
class AuctionResult:
    task: str
    winner: str
    winning_bid: Bid
    all_bids: List[Bid]
    execution_result: Any


class BiddingAgent:
    """Agent that can bid on and execute tasks."""
    
    def __init__(
        self, 
        name: str, 
        specialties: List[str], 
        llm,
        max_concurrent_tasks: int = 3
    ):
        self.name = name
        self.specialties = specialties
        self.llm = llm
        self.max_concurrent = max_concurrent_tasks
        self.current_tasks = 0
    
    async def evaluate_and_bid(self, task_description: str) -> Optional[Bid]:
        """Evaluate a task and submit a bid."""
        
        if self.current_tasks >= self.max_concurrent:
            return None  # Too busy to bid
        
        bid_prompt = f"""
        You are {self.name}, an agent specializing in: {', '.join(self.specialties)}
        
        ## Task for Auction
        {task_description}
        
        ## Your Current Load
        Active tasks: {self.current_tasks}/{self.max_concurrent}
        
        ## Instructions
        Evaluate this task and decide whether to bid.
        Consider:
        1. Does this match your specialties?
        2. How confident are you in delivering quality?
        3. How long will this take?
        
        If you want to bid, provide:
        - bid_value: 1-100 (higher = more confident/capable)
        - confidence: 0.0-1.0 (probability of success)
        - estimated_time: hours to complete
        - reasoning: why you should win this task
        
        If you don't want to bid, respond with "PASS"
        """
        
        response = await self.llm.generate(bid_prompt)
        
        if "PASS" in response.upper():
            return None
        
        # Parse bid (in production, use structured output)
        return Bid(
            agent_name=self.name,
            bid_value=self._extract_bid_value(response),
            confidence=self._extract_confidence(response),
            estimated_time=self._extract_time(response),
            reasoning=response
        )
    
    async def execute_task(self, task: str, context: dict = None) -> str:
        """Execute a won task."""
        self.current_tasks += 1
        try:
            result = await self.llm.generate(
                f"Complete this task: {task}\nContext: {context or 'None'}"
            )
            return result
        finally:
            self.current_tasks -= 1
    
    def _extract_bid_value(self, response: str) -> float:
        # Simplified extraction - use structured output in production
        import re
        match = re.search(r'bid_value[:\s]+(\d+)', response, re.IGNORECASE)
        return float(match.group(1)) if match else 50.0
    
    def _extract_confidence(self, response: str) -> float:
        import re
        match = re.search(r'confidence[:\s]+([\d.]+)', response, re.IGNORECASE)
        return float(match.group(1)) if match else 0.5
    
    def _extract_time(self, response: str) -> float:
        import re
        match = re.search(r'estimated_time[:\s]+([\d.]+)', response, re.IGNORECASE)
        return float(match.group(1)) if match else 1.0


class TaskAuctioneer:
    """Manages task auctions among bidding agents."""
    
    def __init__(self, agents: List[BiddingAgent]):
        self.agents = agents
    
    async def run_sealed_bid_auction(self, task: str) -> AuctionResult:
        """
        Run a sealed-bid auction where all bids are submitted simultaneously.
        Winner is the highest bidder.
        """
        # Collect bids in parallel
        bid_tasks = [agent.evaluate_and_bid(task) for agent in self.agents]
        bids = await asyncio.gather(*bid_tasks)
        
        # Filter out non-bidders
        valid_bids = [b for b in bids if b is not None]
        
        if not valid_bids:
            raise ValueError("No agents bid on this task")
        
        # Select winner (highest bid)
        winner_bid = max(valid_bids, key=lambda b: b.bid_value)
        winner_agent = next(a for a in self.agents if a.name == winner_bid.agent_name)
        
        # Execute the task
        result = await winner_agent.execute_task(task)
        
        return AuctionResult(
            task=task,
            winner=winner_bid.agent_name,
            winning_bid=winner_bid,
            all_bids=valid_bids,
            execution_result=result
        )
    
    async def run_english_auction(
        self, 
        task: str, 
        starting_bid: float = 10,
        increment: float = 5,
        max_rounds: int = 10
    ) -> AuctionResult:
        """
        Run an English auction with ascending bids.
        Agents drop out when they can't bid higher.
        """
        current_bid = starting_bid
        active_agents = list(self.agents)
        highest_bidder = None
        all_bids = []
        
        for round_num in range(max_rounds):
            if len(active_agents) <= 1:
                break
            
            round_bids = []
            agents_to_remove = []
            
            for agent in active_agents:
                bid_prompt = f"""
                Round {round_num + 1} of auction.
                Current bid: {current_bid}
                Minimum next bid: {current_bid + increment}
                
                Task: {task}
                
                Will you bid higher? Respond with your bid amount or "PASS"
                """
                
                response = await agent.llm.generate(bid_prompt)
                
                if "PASS" in response.upper():
                    agents_to_remove.append(agent)
                else:
                    try:
                        new_bid = float(response.strip())
                        if new_bid >= current_bid + increment:
                            round_bids.append(Bid(
                                agent_name=agent.name,
                                bid_value=new_bid,
                                confidence=0.0,
                                estimated_time=0.0,
                                reasoning=f"Round {round_num + 1}"
                            ))
                    except ValueError:
                        agents_to_remove.append(agent)
            
            # Remove agents who passed
            for agent in agents_to_remove:
                active_agents.remove(agent)
            
            # Update current bid
            if round_bids:
                highest_round_bid = max(round_bids, key=lambda b: b.bid_value)
                current_bid = highest_round_bid.bid_value
                highest_bidder = highest_round_bid.agent_name
                all_bids.append(highest_round_bid)
        
        if not highest_bidder:
            raise ValueError("No winner - all agents passed")
        
        winner_agent = next(a for a in self.agents if a.name == highest_bidder)
        result = await winner_agent.execute_task(task)
        
        return AuctionResult(
            task=task,
            winner=highest_bidder,
            winning_bid=all_bids[-1] if all_bids else None,
            all_bids=all_bids,
            execution_result=result
        )


# Usage example
async def main():
    # Create specialized agents
    agents = [
        BiddingAgent("DataAnalyst", ["analysis", "statistics", "visualization"], llm),
        BiddingAgent("Writer", ["writing", "editing", "summarization"], llm),
        BiddingAgent("Researcher", ["research", "fact-checking", "sourcing"], llm),
        BiddingAgent("Coder", ["code", "debugging", "optimization"], llm),
    ]
    
    auctioneer = TaskAuctioneer(agents)
    
    # Run an auction
    result = await auctioneer.run_sealed_bid_auction(
        "Analyze customer feedback data and write a summary report"
    )
    
    print(f"Winner: {result.winner}")
    print(f"Bid: {result.winning_bid.bid_value}")
    print(f"Result: {result.execution_result}")
```

## Template 4: Human-in-the-Loop Escalation

```python
"""
Human-in-the-Loop Pattern
-------------------------
Agents can escalate to humans when confidence is low or stakes are high.
"""

from enum import Enum
from dataclasses import dataclass
from typing import Callable, Optional, Any


class EscalationReason(str, Enum):
    LOW_CONFIDENCE = "low_confidence"
    HIGH_STAKES = "high_stakes"
    CONFLICTING_INFO = "conflicting_information"
    POLICY_DECISION = "policy_decision"
    ERROR_RECOVERY = "error_recovery"
    EXPLICIT_REQUEST = "user_requested"


@dataclass
class EscalationRequest:
    reason: EscalationReason
    context: str
    options: list
    agent_recommendation: Optional[str]
    urgency: str  # low, medium, high


class HumanProxy:
    """Handles escalation to human decision makers."""
    
    def __init__(
        self, 
        escalation_handler: Callable[[EscalationRequest], str],
        auto_approve_threshold: float = 0.9
    ):
        self.handler = escalation_handler
        self.threshold = auto_approve_threshold
        self.escalation_log = []
    
    async def check_and_escalate(
        self,
        action: str,
        confidence: float,
        stakes: str = "normal",
        context: str = ""
    ) -> tuple[bool, str]:
        """
        Check if action should be escalated to human.
        
        Returns:
            (approved: bool, decision: str)
        """
        
        # Auto-approve high-confidence, low-stakes actions
        if confidence >= self.threshold and stakes == "low":
            return True, action
        
        # Determine escalation reason
        if confidence < 0.5:
            reason = EscalationReason.LOW_CONFIDENCE
        elif stakes == "high":
            reason = EscalationReason.HIGH_STAKES
        else:
            reason = EscalationReason.POLICY_DECISION
        
        # Create escalation request
        request = EscalationRequest(
            reason=reason,
            context=f"Action: {action}\nConfidence: {confidence}\nContext: {context}",
            options=["approve", "modify", "reject"],
            agent_recommendation=action if confidence > 0.5 else None,
            urgency="high" if stakes == "high" else "medium"
        )
        
        # Escalate to human
        decision = await self.handler(request)
        self.escalation_log.append((request, decision))
        
        return decision != "reject", decision
    
    async def resolve_conflict(
        self,
        agent_opinions: dict,
        context: str
    ) -> str:
        """Escalate conflicting agent opinions to human."""
        
        request = EscalationRequest(
            reason=EscalationReason.CONFLICTING_INFO,
            context=f"Agents disagree:\n{self._format_opinions(agent_opinions)}\n\nContext: {context}",
            options=list(agent_opinions.keys()) + ["custom"],
            agent_recommendation=None,
            urgency="medium"
        )
        
        return await self.handler(request)
    
    def _format_opinions(self, opinions: dict) -> str:
        return "\n".join(f"- {agent}: {opinion}" for agent, opinion in opinions.items())


# Example escalation handler (would connect to UI in production)
async def console_escalation_handler(request: EscalationRequest) -> str:
    """Simple console-based escalation for development."""
    
    print("\n" + "="*50)
    print(f"🚨 ESCALATION: {request.reason.value.upper()}")
    print("="*50)
    print(f"\nContext:\n{request.context}")
    print(f"\nOptions: {request.options}")
    if request.agent_recommendation:
        print(f"Agent recommends: {request.agent_recommendation}")
    print(f"Urgency: {request.urgency}")
    
    decision = input("\nYour decision: ").strip()
    return decision if decision in request.options else request.options[0]


# Integration with agent workflow
class EscalationAwareAgent:
    """Agent that knows when to escalate to humans."""
    
    def __init__(self, llm, human_proxy: HumanProxy):
        self.llm = llm
        self.human = human_proxy
    
    async def execute_with_oversight(
        self,
        task: str,
        stakes: str = "normal"
    ) -> dict:
        """Execute task with human oversight for critical decisions."""
        
        # Step 1: Agent proposes action
        proposal = await self.llm.generate(f"""
        Task: {task}
        
        Propose an action to complete this task.
        Also rate your confidence (0.0-1.0) in this action.
        
        Format:
        ACTION: <your proposed action>
        CONFIDENCE: <0.0-1.0>
        REASONING: <why this action>
        """)
        
        action = self._extract_action(proposal)
        confidence = self._extract_confidence(proposal)
        
        # Step 2: Check if escalation needed
        approved, decision = await self.human.check_and_escalate(
            action=action,
            confidence=confidence,
            stakes=stakes,
            context=task
        )
        
        if not approved:
            return {
                "status": "rejected",
                "reason": decision,
                "proposed_action": action
            }
        
        # Step 3: Execute (potentially modified) action
        final_action = decision if decision != "approve" else action
        result = await self._execute_action(final_action)
        
        return {
            "status": "completed",
            "action": final_action,
            "result": result,
            "was_escalated": decision != action
        }
```
