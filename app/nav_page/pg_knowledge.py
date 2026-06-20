import streamlit as st
from streamlit import session_state as ss
from my_knowledge_source import MyKnowledgeSource
import db_utils
import os
import shutil
from pathlib import Path

class PageKnowledge:
    def __init__(self):
        self.name = "Knowledge"

    def create_knowledge_source(self):
        knowledge_source = MyKnowledgeSource()
        if 'knowledge_sources' not in ss:
            ss.knowledge_sources = []
        ss.knowledge_sources.append(knowledge_source)
        knowledge_source.edit = True
        # FIX: Pass user_id
        db_utils.save_knowledge_source(knowledge_source, ss.user_id)
        return knowledge_source

    def clear_knowledge(self):
        home_dir = Path.home()
        crewai_dir = home_dir / ".crewai"
        knowledge_dir = crewai_dir / "knowledge"
        if knowledge_dir.exists():
            shutil.rmtree(knowledge_dir)
            st.success("Knowledge stores cleared successfully!")
        else:
            st.info("No knowledge stores found to clear.")

    def draw(self):
        st.markdown(
            """
            <div style="margin-bottom: 20px;">
                <h1 style="font-size:48px; margin-bottom:6px; color:#58A6FF;">📚 Knowledge</h1>
                <p style="font-size:18px; opacity:0.75;">
                    Manage reference libraries for your agents.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("---")
        os.makedirs("knowledge", exist_ok=True)
        
        editing = False
        if 'knowledge_sources' not in ss:
            # FIX: Pass user_id
            ss.knowledge_sources = db_utils.load_knowledge_sources(ss.user_id)
            
        for knowledge_source in ss.knowledge_sources:
            knowledge_source.draw()
            if knowledge_source.edit:
                editing = True
                
        if len(ss.knowledge_sources) == 0:
            st.write("No knowledge sources defined yet.")
            
        st.button('Create Knowledge Source', on_click=self.create_knowledge_source, disabled=editing)

        st.button("Clear All Knowledge Stores", on_click=self.clear_knowledge, 
                  help="Clears cached embeddings in CrewAI home directory")