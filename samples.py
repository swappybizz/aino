
import streamlit as st
import random

@st.dialog(title="AINO Effort Multiplier", width="large")
def run_sample_EM():
    with st.status("Fetching an Expert for you",expanded=True):

        col1, col2 = st.columns([1, 2])

        with col1:
            st.write("""
            ## USERNAME
            ### :blue[Seeds] :gray[20]
            ### :blue[Active Listners] :gray[20]
            ### :blue[Skills and Expertise] :
            """)

            for i in range(0, 5, 2):  # Iterate with a step of 2 to handle pairs of columns
                skill_col1, skill_col2 = st.columns(2)
                
                with skill_col1:
                    with st.container(border=True):
                        st.write(f"Skill {i}")
                
                if i + 1 < 5:  # Check to avoid index out of range
                    with skill_col2:
                        with st.container(border=True):
                            st.write(f"Skill {i + 1}")
                            
                            
            st.write("""
                     :gray[Review 🧑‍🏫|🤖] :
                     ### ⭐ ⭐ ⭐ ⭐ ⚫
                     """)
            st.button("Sign in to discover", key="request_expert", use_container_width=True)
            
            
            
        with col2:
            with st.container(height=500):
                roles = ["ai","user"]
                for i in range(1):
                    role = random.choice(roles)
                    with st.chat_message(role):
                        st.write(f"Start Message from {role}")
                        
                        
            st.chat_input("Type your message here")
            
            
@st.dialog(title = "AINO A-Ro Report", width="large")
def run_sample_aro():
    with st.status("Fetching an Expert for you",expanded=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write("## Expert Details about Active Listners, Skills and Expertise, rating matrix ")
            
            
            
        with col2:
            with st.container(height=500):
                roles = ["ai","user"]
                for i in range(5):
                    role = random.choice(roles)
                    with st.chat_message(role):
                        st.write(f"Message from {role}")
                        
                        
            st.chat_input("Type your message here")
      
@st.dialog(title = "AINO ExpertSolve System", width="large")      
def run_sample_expert():
    with st.status("Fetching an Expert for you",expanded=True):
        col1, col2 = st.columns([1, 2])
        with col1:
            st.write("## Expert Details about Active Listners, Skills and Expertise, rating matrix ")
            
            
            
        with col2:
            with st.container(height=500):
                roles = ["ai","user"]
                for i in range(5):
                    role = random.choice(roles)
                    with st.chat_message(role):
                        st.write(f"Message from {role}")
                        
                        
            st.chat_input("Type your message here")