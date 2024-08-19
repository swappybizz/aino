import streamlit as st
from pymongo import MongoClient
from helpers import  authenticate, create_user
# from tutorials import show_tutorials
from samples import run_sample_EM, run_sample_aro, run_sample_expert
# MongoDB setup
MONGO_URI = st.secrets["mongo_uri"]
SECRET_PHRASE = st.secrets["secret_phrase"]

client = MongoClient(MONGO_URI)
db = client["aino_db"]
users_collection = db["users"]
LOGO_URL_SMALL = "aino.png"
st.set_page_config(page_title="ExpertLine", page_icon="🧠", layout="wide")
st.logo(image="aino.png",icon_image=LOGO_URL_SMALL)
# Function to hash passwords





def show_tutorials():
    st.write(    """
    ### :gray[How ExpertLine Works]
    ## :blue[ExpertLine] does two things
    """
    )
    with st.container(border=True):
        """

    - #### Helps subject matter Experts cater to multiple clients simultaneously.
    
        """
    with st.container(border=True):
        """
    - #### Helps Individuals, small teams , professionals and organisations access expertese on demand.
    
        """
    """
    We also plan to implement conditional royalty payments for the experts.
    Organisations can purchase, access, request or demand human-backed expertese data for various purposes.
        """
        
    "### :blue[Tutorials]"
    with st.expander(":red[Tutorial]- How to use ExpertLine for distributing expertese"):
    
        """

        # You can share and distribute your expertese with ease
            
        - ### With :blue[ExpertLine] you get access to a aommunication & distribution bot that represents you and sources its words :red[only from you].
        - ### :blue[ExpertLine] never ❌ Assumes or hallucinates, if it's in any doubt, it just :blue[asks you for the infor].
            
        You can create Agents to represent any activity that consists of a digital input and output. We currently support pdf, docx, and text based conversations.
        We slowly include support for other types of files.
        
        ## To create an agent:
        - ### 1.Click on < sidebar button to reveal the options.
        - ### 2. Select Smei ( Smithy in Norwegian) to enter the workspace. This Workplace is Where you create, modify, retire and manage your agents.
        - ### 3. You must fill the details requested to define various characteristics of the agent.
                - #### a. Name: The name of the agent.
                - #### b. Title to the user :  This is like the Agents life AIM.
                - #### c. Instructions: A brief description of the agent's purpose, how should it communicate? should it act like an enterviewer or a teacher, or guide, or sureveyor.
                            #### In case of quitionaers, specialised enquiries etc, a detailed set of instructions including contingency plans for the agent, must be included in the instructions.
                            #### In most cases its also recommended to give the agent a set of documents as knowledge base to refer to. but is optional. The same information can be added in instructions as well, but the file upload is just for your convenience.
                - #### d. Input type: The type of input the agent will accept. Will it just chat? or accept documents as well? Define what the input must consist of?
                - #### e. Output type: The type of output the agent will provide. Will it just chat? or provide documents and /or files as well?
                
        - Once the agent is live you can see it in the active agents list, and control or modify
        
        ### What happends when the agent can not answer the client's query?
        - ### The agent will ask you for the answer, and you can provide the answer dieectly to the client, add to client-bot chat, as well as make it public knowledge (at clients permission ofcourse) to demonstrate your speciality.
        - ### You can optionally add the query and answer to the agents knowledge base for future reference. So you :red[Never have to answer the same thing twice].
        """
        


# Initialize session state for authentication
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if st.session_state.logged_in:
    st.sidebar.write(f"Welcome, {st.session_state.username}!")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()
else:
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    login_signup_button = st.sidebar.button("Login/Signup", use_container_width=True)

    if login_signup_button:
        if users_collection.find_one({"username": username}):
            if authenticate(username, password, users_collection, SECRET_PHRASE):
                st.session_state.logged_in = True
                st.session_state.username = username
                st.sidebar.success(f"Welcome {username}")
                st.rerun()
            else:
                st.sidebar.error("Invalid username or password")
        else:
            create_user(username, password, users_collection, SECRET_PHRASE)
            st.sidebar.success("Account created successfully! Please log in.")
            st.rerun()

if st.session_state.logged_in:
    st.write(f"Welcome, {st.session_state.username}!")
    show_tutorials()
    
    
    
else:
    """### :blue[Expertline]"""
    """
    ## :orange[Expert] Pipelines for :orange[Expertise] Distribution
    """
    col1,col2,col3 = st.columns(3)
    with col1:
        with st.container(border=True,height=300):
            """
            ##### Truth receptors for effort multipliers.
            ## :gray[Attend multiple data clients at the same time. Persist new data & ownership for expanding knowledge base.]
            """
        # run_expert_button = st.button(":blue[Run Multiplier]",use_container_width=True)
        # if run_expert_button:
        #     run_sample_EM()
    with col2:
        with st.container(border=True,height=300):
            """
            ##### Accountability & Royalty pipeline for decision critical data.
            ## :gray[Track data requests and their sources. Monitor & Monitise data usage and access.]
            """
        # text_accountability_pipeline = st.button(":blue[Simulate A-Ro Report] ",
        #                                          use_container_width=True)
        # if text_accountability_pipeline:
        #     run_sample_aro()
    with col3:
        with st.container(border=True,height=300):
            """
            ##### Storage & Source for the truth of the matter.
            ## :gray[Expertise data store for tailored requests. Exclusivity as Service. ]
            """
        # data_store_button = st.button(":blue[Run ExpertSolve System]",use_container_width=True)
        # if data_store_button:
        #     run_sample_expert()
    """
    #### Recent Updates
    """
    with st.container(border=True):
        """- ExpertLine Begining its Beta testing phase. Sign up now to participate."""


    with st.container(border=False):
        """""" 
        midcol1,midcol2 = st.columns([1,2])
        with midcol1:
            st.image("multiply.png")
            
        with midcol2:
            """
            # Attend to multiple clients
            - ### :blue[ExpertLine] :gray[provides LLM supported distribution of your expertese to cater to multiple clients simultaneously.]
            - ### :gray[Never assumes or hallucinates, it just requests you to provide the truth.]
            - ### :gray[Remembers, what you provide. So you only have to teach it once.]
            """
            # if st.button("Run Effort Multiplier",use_container_width=True, key="Effort Multiplier"):
            #     run_sample_EM()
    st.divider()       
    with st.container(border=False):
        """""" 
        midcol1,midcol2 = st.columns([2,1])
        with midcol2:
            st.image("Account.png", use_column_width=True)
            
        with midcol1:
            """
            # Accountability & Royalty pipeline
            - ### :blue[ExpertLine] :gray[ provides a pipeline to track data requests and their sources.]
            - ###  :gray[Monitors and monetises data usage and access.]
            - ###  :gray[Provides a way to track royalties for creator benefits.]
            - ###  :gray[Provides a pipeline to track accountability for clients' benefit.]
            """
            # if st.button("Run A-Ro Pipeline",use_container_width=True, key="A-Ro Pipeline"):
            #     run_sample_aro()
    st.divider()
    with st.container(border=False):
        """""" 
        midcol1,midcol2 = st.columns([1,2])
        with midcol1:
            st.image("store.svg")
            
        with midcol2:
            """
            # ExpertSolve System
            - ### :blue[ExpertLine] :gray[is one stop solution for varied expert-backed truth of the matter.]
            - ### :gray[Never be limited by the lack of expertise.]
            - ### :gray[Exclusive access on demand.]
            """
            # if st.button("Run ExpertSolve System",use_container_width=True, key="ExpertSolve System"):
            #     run_sample_expert()
