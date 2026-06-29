import os
import re
from datetime import datetime
from html import escape

import streamlit as st
from dotenv import load_dotenv


load_dotenv()


EXAMPLE_TOPICS = [
    "AI agents in software engineering",
    "Climate risk modeling for cities",
    "Quantum-safe cryptography adoption",
]


def has_env(name: str) -> bool:
    return bool(os.getenv(name))


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text or ""))


def count_urls(text: str) -> int:
    return len(re.findall(r"https?://\S+", text or ""))


def format_num(value: int) -> str:
    return f"{value / 1000:.1f}k" if value >= 1000 else str(value)


def inject_styles() -> None:
    st.markdown(
        """
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700;900&display=swap" rel="stylesheet">
        <style>
          :root {
            --black: #000000;
            --white: #ffffff;
            --muted: #f2f2f2;
            --red: #ff3000;
            --green: #22c55e;
            --border: 2px solid #000000;
            --font: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
          }

          html, body, [class*="css"] { font-family: var(--font) !important; }
          body {
            background-color: var(--white);
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24'%3E%3Cpath d='M24 0H0M0 24V0' stroke='%23000' stroke-width='0.4' opacity='0.03'/%3E%3C/svg%3E");
          }

          .stApp { background: transparent; color: var(--black); }
          .block-container { padding: 0 2.25rem 2rem; max-width: 1280px; }
          header[data-testid="stHeader"] { background: transparent; }

          section[data-testid="stSidebar"] {
            background: var(--black);
            border-right: var(--border);
          }
          section[data-testid="stSidebar"] * { color: var(--white); }
          section[data-testid="stSidebar"] .stButton button {
            background: rgba(255,255,255,0.05);
            color: rgba(255,255,255,0.72);
            border: 1px solid rgba(255,255,255,0.16);
          }

          .sidebar-logo {
            border-bottom: 1px solid rgba(255,255,255,0.12);
            padding: 0.75rem 0 1.25rem;
            margin-bottom: 1.5rem;
          }
          .logo-mark { display: flex; align-items: center; gap: 10px; margin-bottom: 0.5rem; }
          .logo-square { width: 28px; height: 28px; background: var(--red); }
          .logo-text {
            font-size: 0.78rem;
            font-weight: 900;
            letter-spacing: 0.18em;
            line-height: 1.05;
            text-transform: uppercase;
          }
          .logo-sub {
            font-size: 0.65rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: rgba(255,255,255,0.4) !important;
          }
          .side-label {
            font-size: 0.6rem;
            font-weight: 700;
            letter-spacing: 0.2em;
            text-transform: uppercase;
            color: rgba(255,255,255,0.35) !important;
            margin: 1.2rem 0 0.8rem;
          }
          .env-row, .pipeline-step { display: flex; align-items: flex-start; gap: 10px; }
          .env-row { align-items: center; margin-bottom: 0.65rem; }
          .env-dot { width: 7px; height: 7px; flex: 0 0 auto; margin-top: 1px; }
          .env-dot.ok { background: var(--green); }
          .env-dot.warn { background: var(--red); }
          .env-key { font-family: 'Courier New', monospace; font-size: 0.72rem; color: rgba(255,255,255,0.7) !important; }
          .env-badge { margin-left: auto; font-size: 0.6rem; font-weight: 900; letter-spacing: 0.1em; text-transform: uppercase; padding: 2px 6px; }
          .env-badge.ok { background: rgba(34,197,94,0.15); color: var(--green) !important; }
          .env-badge.warn { background: rgba(255,48,0,0.2); color: var(--red) !important; }
          .pipeline-step { border-bottom: 1px solid rgba(255,255,255,0.06); padding: 0.75rem 0; }
          .step-num { min-width: 22px; font-size: 0.62rem; font-weight: 900; letter-spacing: 0.1em; color: var(--red) !important; }
          .step-name { font-size: 0.75rem; font-weight: 800; letter-spacing: 0.06em; text-transform: uppercase; }
          .step-desc { font-size: 0.68rem; line-height: 1.4; color: rgba(255,255,255,0.38) !important; }
          .run-cmd { display: block; font-family: 'Courier New', monospace; font-size: 0.65rem; color: rgba(255,255,255,0.35) !important; background: rgba(255,255,255,0.06); padding: 8px 12px; }

          .hero {
            display: grid;
            grid-template-columns: 1fr 320px;
            border: var(--border);
            margin-top: 1.5rem;
            min-height: 260px;
            background: var(--white);
          }
          .hero-content { padding: 3.5rem 3rem 3rem; }
          .eyebrow {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 1rem;
            color: var(--red);
            font-size: 0.65rem;
            font-weight: 800;
            letter-spacing: 0.22em;
            text-transform: uppercase;
          }
          .eyebrow:before { content: ''; width: 20px; height: 2px; background: var(--red); display: inline-block; }
          .hero h1 {
            color: var(--black);
            font-size: clamp(2.8rem, 5vw, 5.5rem);
            font-weight: 900;
            letter-spacing: -0.04em;
            line-height: 0.9;
            text-transform: uppercase;
            margin: 0 0 1.5rem;
          }
          .hero-sub { color: #555; max-width: 440px; font-size: 0.9rem; line-height: 1.6; }
          .hero-art {
            border-left: var(--border);
            position: relative;
            background: var(--muted);
            overflow: hidden;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16'%3E%3Ccircle cx='8' cy='8' r='1' fill='%23000' opacity='0.06'/%3E%3C/svg%3E");
          }
          .hero-art .circle { position: absolute; width: 180px; height: 180px; border: 3px solid var(--black); border-radius: 50%; top: 50%; left: 50%; transform: translate(-50%, -50%); }
          .hero-art .red { position: absolute; width: 100px; height: 100px; background: var(--red); top: 20px; right: 20px; }
          .hero-art .box { position: absolute; width: 70px; height: 70px; border: 3px solid var(--black); bottom: 30px; left: 25px; }
          .hero-art .line { position: absolute; height: 3px; width: 60%; left: 20%; bottom: 90px; background: var(--black); }
          .hero-art .label { position: absolute; right: 16px; bottom: 16px; font-size: 0.55rem; font-weight: 800; letter-spacing: 0.15em; text-transform: uppercase; color: rgba(0,0,0,0.3); }

          .section-card {
            border-left: var(--border);
            border-right: var(--border);
            border-bottom: var(--border);
            background: rgba(255,255,255,0.92);
            padding: 2rem 2.5rem;
          }
          .section-header { display: flex; gap: 1rem; align-items: baseline; margin-bottom: 1.2rem; }
          .section-num { color: var(--red); font-size: 0.6rem; font-weight: 900; letter-spacing: 0.18em; text-transform: uppercase; }
          .section-title { color: var(--black); font-size: 0.72rem; font-weight: 800; letter-spacing: 0.16em; text-transform: uppercase; }

          div[data-testid="stTextArea"] textarea {
            border: var(--border);
            border-radius: 0;
            min-height: 132px;
            color: var(--black);
            background: var(--white);
            font-size: 1rem;
            line-height: 1.6;
          }
          div[data-testid="stTextArea"] label p {
            color: var(--black);
            font-size: 0.65rem;
            font-weight: 800;
            letter-spacing: 0.14em;
            text-transform: uppercase;
          }
          .stButton button, .stDownloadButton button {
            width: 100%;
            border: var(--border);
            border-radius: 0;
            background: var(--black);
            color: var(--white);
            font-weight: 900;
            letter-spacing: 0.14em;
            text-transform: uppercase;
            padding: 0.9rem 1.2rem;
            transition: all 150ms ease;
          }
          .stButton button:hover, .stDownloadButton button:hover { background: var(--red); color: var(--white); border-color: var(--red); }

          .metrics-strip { display: grid; grid-template-columns: repeat(4, 1fr); border: var(--border); border-top: 0; }
          .metric { padding: 1.55rem 1.6rem; border-right: var(--border); background: var(--white); position: relative; }
          .metric:last-child { border-right: 0; }
          .metric:after { content: ''; position: absolute; left: 0; bottom: 0; width: 100%; height: 3px; background: var(--red); }
          .metric-label { font-size: 0.6rem; font-weight: 800; letter-spacing: 0.18em; text-transform: uppercase; color: #888; margin-bottom: 0.5rem; }
          .metric-value { font-size: 2.8rem; font-weight: 900; letter-spacing: -0.04em; line-height: 1; color: var(--black); }
          .metric-note { font-size: 0.65rem; color: #aaa; letter-spacing: 0.08em; text-transform: uppercase; margin-top: 0.35rem; }

          .empty-state { display: flex; gap: 2.5rem; align-items: flex-start; padding: 3rem 1rem; }
          .empty-comp { width: 140px; height: 140px; flex: 0 0 auto; border: 3px solid var(--black); box-shadow: 20px 20px 0 var(--red); background: linear-gradient(135deg, var(--white) 0 18%, var(--muted) 18% 82%, var(--white) 82%); }
          .empty-eyebrow { color: var(--red); font-size: 0.6rem; font-weight: 800; letter-spacing: 0.2em; text-transform: uppercase; margin-bottom: 0.75rem; }
          .empty-heading { font-size: 2rem; font-weight: 900; letter-spacing: -0.03em; text-transform: uppercase; line-height: 0.95; margin-bottom: 1rem; }
          .empty-body { color: #666; max-width: 36ch; line-height: 1.65; font-size: 0.87rem; }

          .stTabs [data-baseweb="tab-list"] { gap: 0; border: var(--border); border-bottom: 0; background: var(--muted); }
          .stTabs [data-baseweb="tab"] { border-right: 1px solid var(--black); border-radius: 0; padding: 1rem 1.5rem; }
          .stTabs [data-baseweb="tab"] p { font-size: 0.65rem; font-weight: 800; letter-spacing: 0.14em; text-transform: uppercase; }
          .stTabs [aria-selected="true"] { background: var(--white); }
          .stTabs [data-testid="stMarkdownContainer"] { max-width: 76ch; }

          .footer { display: flex; justify-content: space-between; gap: 1rem; border: var(--border); border-top: 0; background: var(--muted); padding: 1.25rem 1.5rem; }
          .footer p { margin: 0; color: #888; font-size: 0.62rem; letter-spacing: 0.08em; text-transform: uppercase; }
          .footer p:last-child { color: #bbb; }

          @media (max-width: 900px) {
            .block-container { padding-left: 1rem; padding-right: 1rem; }
            .hero { grid-template-columns: 1fr; }
            .hero-art { display: none; }
            .hero-content, .section-card { padding: 2rem 1.5rem; }
            .metrics-strip { grid-template-columns: repeat(2, 1fr); }
            .metric { border-bottom: var(--border); }
            .empty-state { flex-direction: column; }
            .footer { flex-direction: column; }
          }
          @media (max-width: 520px) {
            .hero h1 { font-size: 2.5rem; }
            .metrics-strip { grid-template-columns: 1fr; }
            .metric { border-right: 0; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar() -> None:
    groq_ok = has_env("GROQ_API_KEY")
    tavily_ok = has_env("TAVILY_API_KEY")

    st.sidebar.markdown(
        """
        <div class="sidebar-logo">
          <div class="logo-mark">
            <div class="logo-square"></div>
            <div class="logo-text">Research<br>Center</div>
          </div>
          <div class="logo-sub">Multi-agent pipeline</div>
        </div>
        <div class="side-label">Runtime</div>
        """,
        unsafe_allow_html=True,
    )

    for key, ok in [("GROQ_API_KEY", groq_ok), ("TAVILY_API_KEY", tavily_ok)]:
        status = "Set" if ok else "Missing"
        cls = "ok" if ok else "warn"
        st.sidebar.markdown(
            f"""
            <div class="env-row">
              <div class="env-dot {cls}"></div>
              <span class="env-key">{key}</span>
              <span class="env-badge {cls}">{status}</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.markdown('<div class="side-label">Pipeline stages</div>', unsafe_allow_html=True)
    stages = [
        ("01", "Search Agent", "Finds recent, reliable sources and URLs"),
        ("02", "Reader Agent", "Scrapes the strongest source for deeper context"),
        ("03", "Writer", "Synthesizes findings into a structured report"),
        ("04", "Critic", "Reviews the report and returns quality feedback"),
    ]
    for number, name, desc in stages:
        st.sidebar.markdown(
            f"""
            <div class="pipeline-step">
              <span class="step-num">{number}</span>
              <div>
                <div class="step-name">{name}</div>
                <div class="step-desc">{desc}</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.sidebar.markdown(
        """
        <div class="side-label">Local run</div>
        <code class="run-cmd">streamlit run app.py</code>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <section class="hero">
          <div class="hero-content">
            <p class="eyebrow">Multi-agent research pipeline</p>
            <h1>Research<br>Command<br>Center</h1>
            <p class="hero-sub">Launch web search, source reading, report writing, and critic review from one focused operations dashboard.</p>
          </div>
          <div class="hero-art" aria-hidden="true">
            <div class="circle"></div>
            <div class="red"></div>
            <div class="box"></div>
            <div class="line"></div>
            <div class="label">v2.0</div>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_metrics(result: dict | None) -> None:
    if result:
        search_txt = result.get("search_results", "")
        scrape_txt = result.get("scraped_content", "")
        report_txt = result.get("report", "")
        feedback_txt = result.get("feedback", "")
        values = [
            format_num(count_urls(search_txt)),
            format_num(count_words(scrape_txt)),
            format_num(count_words(report_txt)),
            format_num(count_words(feedback_txt)),
        ]
    else:
        values = ["-", "-", "-", "-"]

    labels = ["URLs found", "Scraped words", "Report words", "Feedback words"]
    notes = ["From search output", "Reader context", "Final draft", "Critic review"]
    cards = "".join(
        f"""
        <div class="metric">
          <div class="metric-label">{label}</div>
          <div class="metric-value">{value}</div>
          <div class="metric-note">{note}</div>
        </div>
        """
        for label, value, note in zip(labels, values, notes)
    )
    st.markdown(f'<section class="metrics-strip">{cards}</section>', unsafe_allow_html=True)


def render_empty_state() -> None:
    st.markdown(
        """
        <div class="empty-state">
          <div class="empty-comp"></div>
          <div>
            <div class="empty-eyebrow">Standing by</div>
            <div class="empty-heading">No run<br>yet</div>
            <p class="empty-body">Run the pipeline to inspect search results, scraped source context, the generated report, and critic feedback.</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def set_topic(topic: str) -> None:
    st.session_state.topic = topic


def run_pipeline(topic: str) -> None:
    from pipeline import run_research_pipeline

    with st.status("Running multi-agent pipeline", expanded=True) as status:
        st.write("Search Agent: finding recent sources and URLs")
        st.write("Reader Agent: selecting and scraping the strongest source")
        st.write("Writer: synthesizing the final report")
        st.write("Critic: reviewing report quality")
        result = run_research_pipeline(topic)
        status.update(label="Pipeline completed", state="complete", expanded=False)

    st.session_state.result = result
    st.session_state.last_topic = topic
    st.session_state.last_run = datetime.now().strftime("%d %b %Y, %H:%M")


def main() -> None:
    st.set_page_config(page_title="Research Command Center", page_icon="R", layout="wide")
    inject_styles()
    render_sidebar()
    render_hero()

    st.markdown(
        """
        <section class="section-card">
          <div class="section-header">
            <span class="section-num">01.</span>
            <span class="section-title">Configure run</span>
          </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([3, 1.25], gap="large")
    with left:
        topic = st.text_area(
            "Research topic",
            key="topic",
            placeholder="Example: Recent advances in retrieval augmented generation evaluation",
        )
        run_clicked = st.button("Run research pipeline ->", type="primary")

    with right:
        st.markdown(
            '<div class="section-title" style="margin-bottom: .65rem; color:#777;">Example topics</div>',
            unsafe_allow_html=True,
        )
        for example in EXAMPLE_TOPICS:
            st.button(example, key=f"example-{example}", on_click=set_topic, args=(example,))

    st.markdown("</section>", unsafe_allow_html=True)

    if run_clicked:
        clean_topic = topic.strip()
        if not clean_topic:
            st.error("Enter a research topic before running the pipeline.")
        else:
            try:
                run_pipeline(clean_topic)
            except Exception as exc:
                st.error(f"Pipeline failed: {exc}")

    result = st.session_state.get("result")
    render_metrics(result)

    tabs = st.tabs(["Search results", "Scraped content", "Final report", "Critic feedback"])
    if result:
        with tabs[0]:
            st.markdown(result.get("search_results") or "No search output returned.")
        with tabs[1]:
            st.markdown(result.get("scraped_content") or "No scraped content returned.")
        with tabs[2]:
            report = result.get("report") or "No report generated."
            st.markdown(report)
            st.download_button(
                "Download report",
                data=report,
                file_name="research_report.md",
                mime="text/markdown",
            )
        with tabs[3]:
            st.markdown(result.get("feedback") or "No feedback returned.")
    else:
        with tabs[0]:
            render_empty_state()
        with tabs[1]:
            st.info("Scraped content will appear after a run.")
        with tabs[2]:
            st.info("Final report will appear after a run.")
        with tabs[3]:
            st.info("Critic feedback will appear after a run.")

    if result:
        meta = f'Last run: "{escape(st.session_state.last_topic)}" - Completed {st.session_state.last_run}'
    else:
        meta = "Live search and scraping depend on API availability and network access."

    st.markdown(
        f"""
        <footer class="footer">
          <p>{meta}</p>
          <p>Swiss Research Dashboard</p>
        </footer>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
