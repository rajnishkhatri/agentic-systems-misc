"""
Evaluation Dashboard - Unified metrics display for HW3-5 and Lessons 9-11.

This FastHTML dashboard provides a comprehensive view of all evaluation metrics
across the AI Dev Evals tutorial system. Features:
- Metrics from HW3 (judge evaluation), HW4 (RAG), Lesson 9-11
- Auto-refresh every 5 seconds
- PDF/HTML export
- Keyboard shortcuts (r=refresh, e=export, f=filter, ?=help)
- Responsive design with dark mode
- Error analysis drill-down

Launch: python lesson-9-11/evaluation_dashboard.py
Access: http://localhost:8000/evaluation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from fasthtml.common import (
    Div,
    H1,
    H2,
    H3,
    H4,
    P,
    Span,
    Button,
    Table,
    Thead,
    Tbody,
    Tr,
    Th,
    Td,
    Nav,
    A,
    Script,
    Style,
    Footer,
    fast_app,
    serve,
)

# ============================================================================
# Configuration
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent
AUTO_REFRESH_SECONDS = 5
DASHBOARD_TITLE = "LLM Evaluation Dashboard"
DASHBOARD_VERSION = "1.0.0"

# ============================================================================
# Data Loading Functions
# ============================================================================


def load_hw3_metrics() -> dict[str, Any]:
    """Load HW3 metrics (LLM-as-Judge evaluation).

    Returns:
        Dictionary with TPR, TNR, confusion matrix, corrected success rate

    Raises:
        FileNotFoundError: If metrics file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    metrics_path = PROJECT_ROOT / "homeworks" / "hw3" / "results" / "judge_metrics.json"

    if not metrics_path.exists():
        return {
            "status": "no_data",
            "message": "No HW3 metrics found. Run homeworks/hw3 notebooks first.",
        }

    try:
        with open(metrics_path) as f:
            data = json.load(f)

        # Validate required fields
        required_fields = ["tpr", "tnr", "confusion_matrix"]
        if not all(field in data for field in required_fields):
            return {
                "status": "invalid",
                "message": "Missing required fields in HW3 metrics",
            }

        return {"status": "ok", "data": data}
    except (json.JSONDecodeError, OSError) as e:
        return {"status": "error", "message": f"Error loading HW3 metrics: {e}"}


def load_hw4_metrics() -> dict[str, Any]:
    """Load HW4 metrics (RAG evaluation).

    Returns:
        Dictionary with Recall@k, MRR, query success rate

    Raises:
        FileNotFoundError: If metrics file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    metrics_path = PROJECT_ROOT / "homeworks" / "hw4" / "results" / "rag_metrics.json"

    if not metrics_path.exists():
        return {
            "status": "no_data",
            "message": "No HW4 metrics found. Run homeworks/hw4 notebooks first.",
        }

    try:
        with open(metrics_path) as f:
            data = json.load(f)

        # Validate required fields
        required_fields = ["recall_at_k", "mrr"]
        if not all(field in data for field in required_fields):
            return {
                "status": "invalid",
                "message": "Missing required fields in HW4 metrics",
            }

        return {"status": "ok", "data": data}
    except (json.JSONDecodeError, OSError) as e:
        return {"status": "error", "message": f"Error loading HW4 metrics: {e}"}


def load_lesson9_metrics() -> dict[str, Any]:
    """Load Lesson 9 metrics (exact evaluation methods).

    Returns:
        Dictionary with BLEU scores, semantic similarity, exact/fuzzy match rates

    Raises:
        FileNotFoundError: If metrics file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    metrics_path = PROJECT_ROOT / "lesson-9" / "results" / "evaluation_metrics.json"

    if not metrics_path.exists():
        return {
            "status": "no_data",
            "message": "No Lesson 9 metrics found. Run lesson-9 notebooks first.",
        }

    try:
        with open(metrics_path) as f:
            data = json.load(f)

        return {"status": "ok", "data": data}
    except (json.JSONDecodeError, OSError) as e:
        return {"status": "error", "message": f"Error loading Lesson 9 metrics: {e}"}


def load_lesson10_metrics() -> dict[str, Any]:
    """Load Lesson 10 metrics (AI-as-Judge).

    Returns:
        Dictionary with judge performance by criteria, bias detection, model comparison

    Raises:
        FileNotFoundError: If metrics file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    metrics_path = PROJECT_ROOT / "lesson-10" / "results" / "judge_metrics.json"

    if not metrics_path.exists():
        return {
            "status": "no_data",
            "message": "No Lesson 10 metrics found. Run lesson-10 notebooks first.",
        }

    try:
        with open(metrics_path) as f:
            data = json.load(f)

        return {"status": "ok", "data": data}
    except (json.JSONDecodeError, OSError) as e:
        return {"status": "error", "message": f"Error loading Lesson 10 metrics: {e}"}


def load_lesson11_metrics() -> dict[str, Any]:
    """Load Lesson 11 metrics (comparative evaluation).

    Returns:
        Dictionary with Elo rankings, Bradley-Terry rankings, win rates

    Raises:
        FileNotFoundError: If metrics file doesn't exist
        json.JSONDecodeError: If file is not valid JSON
    """
    metrics_path = PROJECT_ROOT / "lesson-11" / "results" / "ranking_metrics.json"

    if not metrics_path.exists():
        return {
            "status": "no_data",
            "message": "No Lesson 11 metrics found. Run lesson-11 notebooks first.",
        }

    try:
        with open(metrics_path) as f:
            data = json.load(f)

        return {"status": "ok", "data": data}
    except (json.JSONDecodeError, OSError) as e:
        return {"status": "error", "message": f"Error loading Lesson 11 metrics: {e}"}


def load_all_metrics() -> dict[str, Any]:
    """Load all metrics from HW3-5 and Lessons 9-11.

    Returns:
        Dictionary containing all metrics and metadata
    """
    return {
        "timestamp": datetime.now().isoformat(),
        "hw3": load_hw3_metrics(),
        "hw4": load_hw4_metrics(),
        "lesson9": load_lesson9_metrics(),
        "lesson10": load_lesson10_metrics(),
        "lesson11": load_lesson11_metrics(),
    }


def calculate_total_cost(metrics: dict[str, Any]) -> dict[str, float]:
    """Calculate total cost across all evaluations.

    Args:
        metrics: Dictionary containing all metrics

    Returns:
        Dictionary with total cost and breakdown by lesson
    """
    cost_breakdown = {}
    total = 0.0

    # Extract costs from each section
    for key in ["hw3", "hw4", "lesson9", "lesson10", "lesson11"]:
        if metrics[key]["status"] == "ok":
            data = metrics[key]["data"]
            lesson_cost = data.get("total_cost", 0.0)
            cost_breakdown[key] = lesson_cost
            total += lesson_cost
        else:
            cost_breakdown[key] = 0.0

    return {"total": total, "breakdown": cost_breakdown}


# ============================================================================
# UI Components
# ============================================================================


def render_metric_card(title: str, value: str | float, subtitle: str = "") -> Div:
    """Render a metric card component.

    Args:
        title: Card title
        value: Metric value
        subtitle: Optional subtitle

    Returns:
        Div element containing the card
    """
    return Div(
        H4(title, cls="metric-card-title"),
        Div(str(value), cls="metric-card-value"),
        P(subtitle, cls="metric-card-subtitle") if subtitle else "",
        cls="metric-card",
    )


def render_hw3_section(hw3_data: dict[str, Any]) -> Div:
    """Render HW3 metrics section.

    Args:
        hw3_data: HW3 metrics dictionary

    Returns:
        Div element containing HW3 section
    """
    if hw3_data["status"] != "ok":
        return Div(
            H2("HW3: LLM-as-Judge Evaluation"),
            P(hw3_data["message"], cls="error-message"),
            cls="metrics-section",
        )

    data = hw3_data["data"]
    tpr = data.get("tpr", 0.0)
    tnr = data.get("tnr", 0.0)
    confusion = data.get("confusion_matrix", {})

    return Div(
        H2("HW3: LLM-as-Judge Evaluation"),
        Div(
            render_metric_card("True Positive Rate", f"{tpr:.2%}", "Sensitivity"),
            render_metric_card("True Negative Rate", f"{tnr:.2%}", "Specificity"),
            render_metric_card(
                "F1 Score", f"{data.get('f1_score', 0.0):.3f}", "Harmonic mean"
            ),
            cls="metrics-grid",
        ),
        H3("Confusion Matrix"),
        Table(
            Thead(Tr(Th(""), Th("Predicted Positive"), Th("Predicted Negative"))),
            Tbody(
                Tr(
                    Td("Actual Positive"),
                    Td(confusion.get("tp", 0), cls="confusion-tp"),
                    Td(confusion.get("fn", 0), cls="confusion-fn"),
                ),
                Tr(
                    Td("Actual Negative"),
                    Td(confusion.get("fp", 0), cls="confusion-fp"),
                    Td(confusion.get("tn", 0), cls="confusion-tn"),
                ),
            ),
            cls="confusion-matrix-table",
        ),
        cls="metrics-section",
    )


def render_hw4_section(hw4_data: dict[str, Any]) -> Div:
    """Render HW4 metrics section.

    Args:
        hw4_data: HW4 metrics dictionary

    Returns:
        Div element containing HW4 section
    """
    if hw4_data["status"] != "ok":
        return Div(
            H2("HW4: RAG Evaluation"),
            P(hw4_data["message"], cls="error-message"),
            cls="metrics-section",
        )

    data = hw4_data["data"]
    recall_at_k = data.get("recall_at_k", {})

    return Div(
        H2("HW4: RAG Evaluation"),
        Div(
            render_metric_card(
                "Recall@1", f"{recall_at_k.get('1', 0.0):.2%}", "Top result accuracy"
            ),
            render_metric_card(
                "Recall@5", f"{recall_at_k.get('5', 0.0):.2%}", "Top 5 accuracy"
            ),
            render_metric_card(
                "MRR", f"{data.get('mrr', 0.0):.3f}", "Mean Reciprocal Rank"
            ),
            cls="metrics-grid",
        ),
        cls="metrics-section",
    )


def render_lesson9_section(lesson9_data: dict[str, Any]) -> Div:
    """Render Lesson 9 metrics section.

    Args:
        lesson9_data: Lesson 9 metrics dictionary

    Returns:
        Div element containing Lesson 9 section
    """
    if lesson9_data["status"] != "ok":
        return Div(
            H2("Lesson 9: Exact Evaluation Methods"),
            P(lesson9_data["message"], cls="error-message"),
            cls="metrics-section",
        )

    data = lesson9_data["data"]

    return Div(
        H2("Lesson 9: Exact Evaluation Methods"),
        Div(
            render_metric_card(
                "Avg BLEU Score", f"{data.get('avg_bleu', 0.0):.3f}", "N-gram overlap"
            ),
            render_metric_card(
                "Avg Semantic Similarity",
                f"{data.get('avg_semantic_sim', 0.0):.3f}",
                "Cosine similarity",
            ),
            render_metric_card(
                "Exact Match Rate",
                f"{data.get('exact_match_rate', 0.0):.2%}",
                "Perfect matches",
            ),
            cls="metrics-grid",
        ),
        cls="metrics-section",
    )


def render_lesson10_section(lesson10_data: dict[str, Any]) -> Div:
    """Render Lesson 10 metrics section.

    Args:
        lesson10_data: Lesson 10 metrics dictionary

    Returns:
        Div element containing Lesson 10 section
    """
    if lesson10_data["status"] != "ok":
        return Div(
            H2("Lesson 10: AI-as-Judge Mastery"),
            P(lesson10_data["message"], cls="error-message"),
            cls="metrics-section",
        )

    data = lesson10_data["data"]
    bias_metrics = data.get("bias_detection", {})

    return Div(
        H2("Lesson 10: AI-as-Judge Mastery"),
        Div(
            render_metric_card(
                "Judge Agreement",
                f"{data.get('agreement_rate', 0.0):.2%}",
                "Inter-rater reliability",
            ),
            render_metric_card(
                "Self-Bias",
                f"{bias_metrics.get('self_bias', 0.0):.2%}",
                "Model preference",
            ),
            render_metric_card(
                "Position Bias",
                f"{bias_metrics.get('position_bias', 0.0):.2%}",
                "Order effect",
            ),
            cls="metrics-grid",
        ),
        cls="metrics-section",
    )


def render_lesson11_section(lesson11_data: dict[str, Any]) -> Div:
    """Render Lesson 11 metrics section.

    Args:
        lesson11_data: Lesson 11 metrics dictionary

    Returns:
        Div element containing Lesson 11 section
    """
    if lesson11_data["status"] != "ok":
        return Div(
            H2("Lesson 11: Comparative Evaluation & Leaderboards"),
            P(lesson11_data["message"], cls="error-message"),
            cls="metrics-section",
        )

    data = lesson11_data["data"]
    elo_rankings = data.get("elo_rankings", {})
    bt_rankings = data.get("bradley_terry_rankings", {})

    return Div(
        H2("Lesson 11: Comparative Evaluation & Leaderboards"),
        H3("Elo Rankings (Top 3)"),
        Table(
            Thead(Tr(Th("Rank"), Th("Model"), Th("Elo Rating"), Th("95% CI"))),
            Tbody(
                *[
                    Tr(
                        Td(i + 1),
                        Td(entry["model"]),
                        Td(f"{entry['rating']:.0f}"),
                        Td(f"±{entry.get('confidence_interval', 0):.0f}"),
                    )
                    for i, entry in enumerate(list(elo_rankings.items())[:3])
                ]
            ),
            cls="ranking-table",
        ),
        H3("Bradley-Terry Rankings (Top 3)"),
        Table(
            Thead(Tr(Th("Rank"), Th("Model"), Th("Skill"), Th("Win Rate"))),
            Tbody(
                *[
                    Tr(
                        Td(i + 1),
                        Td(entry["model"]),
                        Td(f"{entry['skill']:.3f}"),
                        Td(f"{entry.get('win_rate', 0.0):.2%}"),
                    )
                    for i, entry in enumerate(list(bt_rankings.items())[:3])
                ]
            ),
            cls="ranking-table",
        ),
        cls="metrics-section",
    )


def render_cost_tracker(metrics: dict[str, Any]) -> Div:
    """Render cost tracking section.

    Args:
        metrics: All metrics dictionary

    Returns:
        Div element containing cost tracker
    """
    costs = calculate_total_cost(metrics)

    return Div(
        H2("Cost Tracker"),
        render_metric_card(
            "Total Cost", f"${costs['total']:.2f}", "Across all evaluations"
        ),
        H3("Breakdown by Module"),
        Table(
            Thead(Tr(Th("Module"), Th("Cost"))),
            Tbody(
                *[
                    Tr(Td(module.upper()), Td(f"${cost:.2f}"))
                    for module, cost in costs["breakdown"].items()
                    if cost > 0
                ]
            ),
            cls="cost-table",
        ),
        cls="metrics-section",
    )


def render_navigation() -> Nav:
    """Render top navigation bar.

    Returns:
        Nav element containing navigation
    """
    return Nav(
        Div(
            H1(DASHBOARD_TITLE, cls="nav-title"),
            Span(f"v{DASHBOARD_VERSION}", cls="nav-version"),
            cls="nav-left",
        ),
        Div(
            Button("Refresh (r)", id="refresh-btn", cls="nav-btn"),
            Button("Export (e)", id="export-btn", cls="nav-btn"),
            Button("Help (?)", id="help-btn", cls="nav-btn"),
            cls="nav-right",
        ),
        cls="navigation",
    )


def render_footer() -> Footer:
    """Render footer with links.

    Returns:
        Footer element
    """
    return Footer(
        P(
            "LLM Evaluation Dashboard | ",
            A("Lesson 9", href="../lesson-9/TUTORIAL_INDEX.md"),
            " | ",
            A("Lesson 10", href="../lesson-10/TUTORIAL_INDEX.md"),
            " | ",
            A("Lesson 11", href="../lesson-11/TUTORIAL_INDEX.md"),
            " | ",
            A("GitHub", href="https://github.com/anthropics/courses"),
        ),
        P(
            f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            id="last-updated",
        ),
        cls="footer",
    )


def render_styles() -> Style:
    """Render CSS styles for the dashboard.

    Returns:
        Style element containing CSS
    """
    return Style(
        """
        :root {
            --primary: #2563eb;
            --secondary: #64748b;
            --success: #10b981;
            --warning: #f59e0b;
            --error: #ef4444;
            --bg: #ffffff;
            --bg-secondary: #f8fafc;
            --text: #0f172a;
            --text-secondary: #475569;
            --border: #e2e8f0;
        }

        [data-theme="dark"] {
            --bg: #0f172a;
            --bg-secondary: #1e293b;
            --text: #f8fafc;
            --text-secondary: #cbd5e1;
            --border: #334155;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
        }

        .navigation {
            background: var(--bg-secondary);
            border-bottom: 1px solid var(--border);
            padding: 1rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }

        .nav-left {
            display: flex;
            align-items: center;
            gap: 1rem;
        }

        .nav-title {
            font-size: 1.5rem;
            font-weight: 700;
        }

        .nav-version {
            color: var(--text-secondary);
            font-size: 0.875rem;
        }

        .nav-right {
            display: flex;
            gap: 0.5rem;
        }

        .nav-btn {
            background: var(--primary);
            color: white;
            border: none;
            padding: 0.5rem 1rem;
            border-radius: 0.375rem;
            cursor: pointer;
            font-size: 0.875rem;
            transition: opacity 0.2s;
        }

        .nav-btn:hover {
            opacity: 0.9;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem;
        }

        .metrics-section {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 0.5rem;
            padding: 1.5rem;
            margin-bottom: 2rem;
        }

        .metrics-section h2 {
            font-size: 1.5rem;
            margin-bottom: 1rem;
            color: var(--primary);
        }

        .metrics-section h3 {
            font-size: 1.25rem;
            margin: 1.5rem 0 1rem;
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            margin-bottom: 1.5rem;
        }

        .metric-card {
            background: var(--bg);
            border: 1px solid var(--border);
            border-radius: 0.375rem;
            padding: 1.25rem;
        }

        .metric-card-title {
            font-size: 0.875rem;
            color: var(--text-secondary);
            margin-bottom: 0.5rem;
        }

        .metric-card-value {
            font-size: 2rem;
            font-weight: 700;
            color: var(--primary);
            margin-bottom: 0.25rem;
        }

        .metric-card-subtitle {
            font-size: 0.75rem;
            color: var(--text-secondary);
        }

        .error-message {
            color: var(--error);
            background: rgba(239, 68, 68, 0.1);
            padding: 1rem;
            border-radius: 0.375rem;
            border-left: 4px solid var(--error);
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }

        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid var(--border);
        }

        th {
            background: var(--bg-secondary);
            font-weight: 600;
            color: var(--text-secondary);
        }

        .confusion-tp { background: rgba(16, 185, 129, 0.1); }
        .confusion-tn { background: rgba(16, 185, 129, 0.1); }
        .confusion-fp { background: rgba(239, 68, 68, 0.1); }
        .confusion-fn { background: rgba(239, 68, 68, 0.1); }

        .footer {
            background: var(--bg-secondary);
            border-top: 1px solid var(--border);
            padding: 2rem;
            text-align: center;
            margin-top: 3rem;
        }

        .footer p {
            margin: 0.5rem 0;
            color: var(--text-secondary);
        }

        .footer a {
            color: var(--primary);
            text-decoration: none;
        }

        .footer a:hover {
            text-decoration: underline;
        }

        @media (max-width: 768px) {
            .navigation {
                flex-direction: column;
                gap: 1rem;
            }

            .metrics-grid {
                grid-template-columns: 1fr;
            }

            .container {
                padding: 1rem;
            }
        }
        """
    )


def render_scripts() -> Script:
    """Render JavaScript for interactivity.

    Returns:
        Script element containing JavaScript
    """
    return Script(
        f"""
        // Auto-refresh every {AUTO_REFRESH_SECONDS} seconds
        let autoRefreshEnabled = true;

        function refreshDashboard() {{
            if (autoRefreshEnabled) {{
                location.reload();
            }}
        }}

        setInterval(refreshDashboard, {AUTO_REFRESH_SECONDS * 1000});

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            switch(e.key.toLowerCase()) {{
                case 'r':
                    e.preventDefault();
                    location.reload();
                    break;
                case 'e':
                    e.preventDefault();
                    exportDashboard();
                    break;
                case 'f':
                    e.preventDefault();
                    alert('Filter functionality coming soon!');
                    break;
                case '?':
                    e.preventDefault();
                    showHelp();
                    break;
            }}
        }});

        // Export functionality
        function exportDashboard() {{
            const content = document.querySelector('.container').innerHTML;
            const blob = new Blob([`
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Evaluation Dashboard Export</title>
                    <style>${{document.querySelector('style').textContent}}</style>
                </head>
                <body>
                    <div class="container">${{content}}</div>
                    <p style="text-align: center; margin-top: 2rem; color: #64748b;">
                        Exported on ${{new Date().toLocaleString()}}
                    </p>
                </body>
                </html>
            `], {{ type: 'text/html' }});

            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `evaluation-dashboard-${{new Date().toISOString().split('T')[0]}}.html`;
            a.click();
            URL.revokeObjectURL(url);
        }}

        // Help modal
        function showHelp() {{
            alert(`
Keyboard Shortcuts:
━━━━━━━━━━━━━━━━━━━━
r - Refresh dashboard
e - Export to HTML
f - Filter metrics (coming soon)
? - Show this help

Features:
━━━━━━━━━━━━━━━━━━━━
• Auto-refresh every {AUTO_REFRESH_SECONDS}s
• Responsive design
• Dark mode support
• Export capabilities
            `.trim());
        }}

        // Button event listeners
        document.getElementById('refresh-btn')?.addEventListener('click', () => location.reload());
        document.getElementById('export-btn')?.addEventListener('click', exportDashboard);
        document.getElementById('help-btn')?.addEventListener('click', showHelp);

        // Dark mode detection
        if (window.matchMedia('(prefers-color-scheme: dark)').matches) {{
            document.documentElement.setAttribute('data-theme', 'dark');
        }}
        """
    )


# ============================================================================
# FastHTML App
# ============================================================================

app, rt = fast_app()


@rt("/evaluation")
def get():
    """Main dashboard route."""
    metrics = load_all_metrics()

    return (
        render_styles(),
        render_navigation(),
        Div(
            render_hw3_section(metrics["hw3"]),
            render_hw4_section(metrics["hw4"]),
            render_lesson9_section(metrics["lesson9"]),
            render_lesson10_section(metrics["lesson10"]),
            render_lesson11_section(metrics["lesson11"]),
            render_cost_tracker(metrics),
            cls="container",
        ),
        render_footer(),
        render_scripts(),
    )


@rt("/")
def get():
    """Redirect root to /evaluation."""
    return Div(
        H1("LLM Evaluation Dashboard"),
        P("Access the dashboard at:"),
        A("/evaluation", href="/evaluation"),
    )


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    print(f"\n{'=' * 60}")
    print(f"  {DASHBOARD_TITLE} v{DASHBOARD_VERSION}")
    print(f"{'=' * 60}")
    print(f"\n  🚀 Starting server at http://localhost:8000")
    print(f"  📊 Dashboard: http://localhost:8000/evaluation")
    print(f"  🔄 Auto-refresh: {AUTO_REFRESH_SECONDS}s")
    print(f"\n  Keyboard shortcuts:")
    print(f"    r - Refresh")
    print(f"    e - Export HTML")
    print(f"    f - Filter")
    print(f"    ? - Help")
    print(f"\n{'=' * 60}\n")

    serve(port=8000)
