import os
import re
from datetime import datetime
from typing import Any

import streamlit as st


st.set_page_config(
    page_title="Research Command Center",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        :root {
            --panel: rgba(15, 23, 42, 0.76);
            --panel-strong: rgba(8, 13, 26, 0.92);
            --border: rgba(125, 211, 252, 0.18);
            --accent: #22d3ee;
            --accent-soft: rgba(34, 211, 238, 0.12);
            --text-muted: #94a3b8;
        }

        .stApp {
            background:
                radial-gradient(circle at 18% 12%, rgba(34, 211, 238, 0.14), transparent 26rem),
                radial-gradient(circle at 88% 18%, rgba(59, 130, 246, 0.12), transparent 26rem),
                linear-gradient(135deg, #050816 0%, #0b1020 48%, #111827 100%);
            color: #f8fafc;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, rgba(2, 6, 23, 0.96), rgba(15, 23, 42, 0.94));
            border-right: 1px solid var(--border);
        }

        [data-testid="stHeader"] {
            background: rgba(5, 8, 22, 0);
        }

        .hero, .input-card, .result-card, .metric-card, .stage-strip {
            border: 1px solid var(--border);
            background: var(--panel);
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.28);
            border-radius: 24px;
        }

        .hero {
            padding: 2rem 2.2rem;
            margin-bottom: 1.2rem;
        }

        .eyebrow {
            color: var(--accent);
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            text-transform: uppercase;
        }

        .hero h1 {
            color: #f8fafc;
            font-size: clamp(2.1rem, 5vw, 4rem);
            line-height: 0.95;
            margin: 0.45rem 0 0.75rem;
        }

        .hero p, .muted {
            color: var(--text-muted);
        }

        .input-card, .result-card {
            padding: 1.35rem;
            margin: 1rem 0;
        }

        .stage-strip {
            display: grid;
            gap: 0.75rem;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            padding: 0.85rem;
            margin: 0.9rem 0 1.2rem;
        }

        .stage {
            background: linear-gradient(180deg, rgba(34, 211, 238, 0.12), rgba(15, 23, 42, 0.22));
            border: 1px solid rgba(34, 211, 238, 0.18);
            border-radius: 18px;
            padding: 0.9rem;
            min-height: 7.2rem;
        }

        .stage-number {
            width: 1.8rem;
            height: 1.8rem;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 99px;
            background: var(--accent-soft);
            color: var(--accent);
            font-weight: 800;
            margin-bottom: 0.55rem;
        }

        .stage-title {
            color: #f8fafc;
            font-weight: 800;
            margin-bottom: 0.18rem;
        }

        .stage-copy {
            color: var(--text-muted);
            font-size: 0.86rem;
            line-height: 1.35;
        }

        .metric-card {
            padding: 1rem;
        }

        .metric-label {
            color: var(--text-muted);
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
        }

        .metric-value {
            color: #f8fafc;
            font-size: 1.65rem;
            font-weight: 850;
            margin-top: 0.2rem;
        }

        .metric-note {
            color: #67e8f9;
            font-size: 0.78rem;
            margin-top: 0.2rem;
        }

        .stButton > button {
            border-radius: 14px;
            border: 1px solid rgba(34, 211, 238, 0.38);
            background: linear-gradient(135deg, #0891b2, #2563eb);
            color: white;
            font-weight: 800;
            min-height: 3rem;
        }

        .stDownloadButton > button {
            border-radius: 14px;
            border: 1px solid rgba(34, 211, 238, 0.38);
        }

        div[data-testid="stTextArea"] textarea {
            border-radius: 16px;
        }

        div[data-testid="stTabs"] button {
            font-weight: 700;
        }

        @media (max-width: 900px) {
            .stage-strip {
                grid-template-columns: 1fr;
            }

            .hero {
                padding: 1.35rem;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_pipeline_map() -> None:
    stages = [
        ("01", "Search Agent", "Finds recent, reliable sources and URLs."),
        ("02", "Reader Agent", "Scrapes the strongest source for deeper context."),
        ("03", "Writer", "Synthesizes findings into a structured report."),
        ("04", "Critic", "Reviews the report and returns quality feedback."),
    ]
    stage_html = "".join(
        f"""
        <div class="stage">
            <div class="stage-number">{number}</div>
            <div class="stage-title">{title}</div>
            <div class="stage-copy">{copy}</div>
        </div>
        """
        for number, title, copy in stages
    )
    st.markdown(f'<div class="stage-strip">{stage_html}</div>', unsafe_allow_html=True)


def as_text(value: Any) -> str:
    if value is None:
        return "No output returned."
    if isinstance(value, str):
        return value.strip() or "No output returned."
    return str(value)


def word_count(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def count_urls(text: str) -> int:
    return len(re.findall(r"https?://\S+", text))


def run_pipeline(topic: str) -> dict[str, Any]:
    from pipeline import run_research_pipeline

    return run_research_pipeline(topic)


def explain_exception(exc: Exception) -> None:
    message = str(exc)
    st.error("The research pipeline could not complete.")
    st.caption(message or exc.__class__.__name__)

    lower_message = message.lower()
    if any(term in lower_message for term in ["api key", "groq", "tavily", "authentication", "unauthorized"]):
        st.info(
            "Check that `GROQ_API_KEY` and `TAVILY_API_KEY` are set in your environment "
            "or `.env` file, then restart Streamlit."
        )
    elif any(term in lower_message for term in ["no module named", "modulenotfounderror", "importerror"]):
        st.info("Install dependencies with `pip install -r requirements.txt`, then rerun the app.")
    else:
        st.info("Confirm your network connection, API quotas, and dependency installation before retrying.")


def render_env_status() -> None:
    st.sidebar.subheader("Runtime Checklist")
    for key in ["GROQ_API_KEY", "TAVILY_API_KEY"]:
        if os.getenv(key):
            st.sidebar.success(f"{key} detected")
        else:
            st.sidebar.warning(f"{key} not detected")

    st.sidebar.markdown(
        """
        **Run locally**

        `streamlit run app.py`

        The pipeline uses live web search and scraping, so runs can take a minute or more.
        """
    )


def render_results(result: dict[str, Any]) -> None:
    search_results = as_text(result.get("search_results"))
    scraped_content = as_text(result.get("scraped_content"))
    report = as_text(result.get("report"))
    feedback = as_text(result.get("feedback"))

    st.markdown("### Mission Output")
    cols = st.columns(4)
    metrics = [
        ("URLs Found", count_urls(search_results), "from search output"),
        ("Scraped Words", word_count(scraped_content), "reader context"),
        ("Report Words", word_count(report), "final draft"),
        ("Feedback Words", word_count(feedback), "critic review"),
    ]
    for col, (label, value, note) in zip(cols, metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">{label}</div>
                    <div class="metric-value">{value}</div>
                    <div class="metric-note">{note}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    tabs = st.tabs(["Search Results", "Scraped Content", "Final Report", "Critic Feedback"])
    with tabs[0]:
        st.markdown(search_results)
    with tabs[1]:
        st.markdown(scraped_content)
    with tabs[2]:
        st.markdown(report)
        st.download_button(
            "Download final report",
            data=report,
            file_name="research_report.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with tabs[3]:
        st.markdown(feedback)


def main() -> None:
    inject_styles()
    render_env_status()

    st.markdown(
        """
        <section class="hero">
            <div class="eyebrow">Multi-agent research pipeline</div>
            <h1>Research Command Center</h1>
            <p>Launch web search, source reading, report writing, and critic review from one focused operations dashboard.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )
    render_pipeline_map()

    if "research_result" not in st.session_state:
        st.session_state.research_result = None
    if "last_topic" not in st.session_state:
        st.session_state.last_topic = ""

    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    st.subheader("New Research Run")
    topic = st.text_area(
        "Research topic",
        placeholder="Example: Recent advances in retrieval augmented generation evaluation",
        height=110,
        help="Use a specific question or theme for better source selection and synthesis.",
    )

    example_choice = st.selectbox(
        "Example topics",
        [
            "Select an example topic...",
            "AI agents in software engineering",
            "Climate risk modeling for cities",
            "Quantum-safe cryptography adoption",
        ],
    )
    if example_choice != "Select an example topic..." and not topic.strip():
        topic = example_choice

    submitted = st.button("Run research pipeline", type="primary", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if submitted:
        clean_topic = topic.strip()
        if not clean_topic:
            st.warning("Enter a research topic before starting the pipeline.")
        else:
            st.session_state.last_topic = clean_topic
            try:
                with st.status("Running multi-agent pipeline...", expanded=True) as status:
                    st.write("Search Agent: collecting reliable recent sources.")
                    st.write("Reader Agent: selecting and scraping source material.")
                    st.write("Writer: drafting the final report.")
                    st.write("Critic: reviewing output quality.")
                    result = run_pipeline(clean_topic)
                    st.session_state.research_result = result
                    st.session_state.completed_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    status.update(label="Research pipeline complete", state="complete", expanded=False)
            except Exception as exc:  # Streamlit should stay usable when setup or API calls fail.
                st.session_state.research_result = None
                explain_exception(exc)

    if st.session_state.research_result:
        st.markdown('<div class="result-card">', unsafe_allow_html=True)
        st.caption(
            f"Last run: {st.session_state.last_topic} | Completed: "
            f"{st.session_state.get('completed_at', 'unknown')}"
        )
        render_results(st.session_state.research_result)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            """
            <div class="result-card">
                <div class="eyebrow">Standing by</div>
                <p class="muted">Run the pipeline to inspect search results, scraped source context, the generated report, and critic feedback.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption("Note: live search and scraping depend on API availability, network access, and source response times.")


if __name__ == "__main__":
    main()
