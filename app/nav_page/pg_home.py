import streamlit as st

class PageHome:
    def __init__(self):
        self.name = "Home"

    def draw(self):
        # Big centered hero
        st.markdown(
            """
            <h1 style="text-align:center; font-size:48px; margin-bottom:0px;">
                🔥 Astrastudio
            </h1>
            <p style="text-align:center; font-size:18px; margin-top:4px; opacity:0.8;">
                Design, run, and observe autonomous AI crews that collaborate to complete complex tasks.
            </p>

            """,
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)

        # Three rounded cards
        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            self.card(
                "🤖 Agents",
                "Define intelligent agents with roles, tools, and goals. "
                "Each agent focuses on a specific responsibility."
            )

        with col2:
            self.card(
                "🧠 Tasks",
                "Break complex objectives into structured tasks "
                "that agents can execute collaboratively."
            )

        with col3:
            self.card(
                "📊 Results",
                "Review outputs, inspect failures, and understand "
                "how your crew performed during execution."
            )
        
        st.markdown("<br><br>", unsafe_allow_html=True)

        st.markdown("## How to use Astrastudio")

        steps = [
            ("🧠Crews", "A crew defines the overall objective and connects agents, tasks, and tools."),
            ("🤖Agents", "Agents are autonomous workers with a role, goal, and access to tools."),
            ("📝Tasks", "Tasks describe what needs to be done and which agent is responsible."),
            ("🛠️Tools", "Tools give agents capabilities such as APIs, search, or code execution."),
            ("🚀Kickoff!", "Starts execution and lets agents collaborate to complete the objective."),
            ("📊Results", "View outputs, intermediate steps and any errors from the run"),
        ]

        for name, desc in steps:
            st.markdown(
                f"""
                <div style="
                    padding: 10px 14px;
                    margin-bottom: 8px;
                    border-radius: 10px;
                    border: 1px solid rgba(255,255,255,0.08);
                    background: rgba(255,255,255,0.02);
                ">
                    <strong>{name}</strong> — {desc}
                </div>
                """,
                unsafe_allow_html=True,
            )


    def card(self, title: str, text: str):
        st.markdown(
            f"""
            <div style="
                border-radius: 12px;
                padding: 16px;
                border: 1px solid rgba(255,255,255,0.08);
                background: rgba(255,255,255,0.02);
                height: 100%;
            ">
                <h3 style="margin-top:0;">{title}</h3>
                <p style="opacity:0.85;">{text}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
