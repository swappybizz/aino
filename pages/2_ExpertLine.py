import streamlit as st
from pymongo import MongoClient
import fitz  # PyMuPDF
import base64, random
import docx
from openai import OpenAI
from datetime import datetime
import json
from fuzzywuzzy import process
MONGO_URI = st.secrets["mongo_uri"]
client = MongoClient(MONGO_URI)
db = client["aino_db"]
agent_collection = db["agents"]
agent_client_session = db["client_sessions"]


st.logo("experline.png")
st.set_page_config(
    page_title="ExpertLine",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "loaded_agent" not in st.session_state:
    st.session_state.loaded_agent = None

if "loaded_session" not in st.session_state:
    st.session_state.loaded_session = None

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

def fetch_agent_response(user_query, agent, session):
    print(f"user_query: {prompt}")
    print(f" AIM: {agent['agent_userTitle']}")
    print(f"Instructions: {agent['agent_instructions']}")
    print(f"Agent Experience_knowledge_base: {str(agent['Experience_knowledge_base'])}")
    # print(f"Document: {agent['docs_store'][0]['content'][:25]}")
    print(f"Session: {session}")
    print(f"SessionAIM: {session['client_goal']}")
    print(f"Outputs: {str(session['outputs'])}")
    
    
    
    all_doc_string = ""
    for doc in agent["docs_store"]:
        all_doc_string += doc["content"]
        all_doc_string += " "
        all_doc_string += "\n"
        
    client_ai_chat = ""
    for chat in session["client_AI_chat"]:
        for key, value in chat.items():
            client_ai_chat += value
            client_ai_chat += " "
            client_ai_chat += "\n"
            
    appended_knowledge = str(agent["Experience_knowledge_base"]) 
        
    print(f"all_doc_string: {all_doc_string[:25]}")
    print(f"client_ai_chat: {client_ai_chat}")
    print(f"appended_knowledge: {appended_knowledge[:25]}")
    
    system_prompt = f"""
    You are a efficient helper, specilaising in {agent['agent_userTitle']} 
    An expert has assigned you to help a client with a project.
    You facilitate the communication between the client and the expert.
    You are tasked with helping the client achieve the following session goal: {session['client_goal']}.
    The client expects outputs of follwing types: {str(session['outputs'])}
    
    You have a knowledeg base to help you with this task.
    In case these are not enough, you can ask the expert directly for help.
    You respond in a valid JSON format.    
    """
    
    user_prompt =f"""
    You have been instructed to: {agent['agent_instructions']}
    
    You are having a conversation with a client, whose conversation history is provided to you.
    You will carry forward the conversation to achieve the session goal.
    You will follow the instructions while responding to the client.
    Your response should include one or more of the following:
    - An Acknowledgement of client query, in form of affirmation, question, argument etc.
    - A response containing information from the knowledge base, if present, else coveying that the information is not available. Even minutely relevant associations can be regarded as present.
    - Refrences in knowledge base, if present, should be used to provide information.
    Always end your response will be a Question.
    Your Questions should direct the conversation towards successful completion of the session goal and outputs.
    
    Here is the conversation history with the client:
    ###
    {client_ai_chat}
    ###
    Here is the knowledge base:
    ###
    {all_doc_string}
    More info
    {appended_knowledge}
    ###
    
    REMEBER: DO NOT USE KNOWLEGE OUTSIDE THE KNOWLEDGE BASE.
    In case of unavailable knowldge, doubt, too much complexity, dillema, or any other issue, you can ask the expert for help.
    You will use the following JSON format to respond to the client:
    ***
    {{
        "client_response": "Your Response to {prompt}". This will be a contain a confirmation and/or notification, directed at clients when contacting the experteg. eg - '... I must contact the Expert for this...'",
        "expert_response": null or "Your Question to the expert Explainig the issue"
    }}
    ***
    Do not add any other inforamtion other than the JSON in your response. THIS IS EXTREMELY IMPORTANT.
    """
    model = "gpt-4o"
    client = OpenAI(api_key=st.secrets["openai_api_key"])
    completion = client.chat.completions.create(
        model="gpt-4o",
        response_format = {"type": "json_object"},
        messages=[
                    {
                        "role":"system",
                        "content": system_prompt
                    },
                    {
                        "role":"user",
                        "content": user_prompt
                    },
                ]
    )
    res = completion.choices[0].message.content
    response = json.loads(res)
    # print(f"Response: {response}")
    if response:
        user_response = response["client_response"]
        expert_response = response["expert_response"]
        # print(f"User Response: {user_response}")
        # print(f"Expert Response: {expert_response}")
    return user_response, expert_response



def start_new_session(agent, username):
    agent_session = {
        "agent_id": agent["_id"],
        "agent_name": agent["agent_name"],
        "agent_userTitle": agent["agent_userTitle"],
        "agent_instructions": agent["agent_instructions"],
        "inputs": agent["inputs"],
        "deliverables": agent["deliverables"],
        "opening_statement_client_expectation": agent[
            "opening_statement_client_expectation" 
        ],
        "allow_personal": agent["allow_personal"],
        "parent": agent["parent"],
        "session_start": datetime.now(),
        "session_end": None,
        "client": username,
        "client_goal": "",
        "outputs": [],
        "client_AI_chat": [],
        "client_DM": [],
        "files": [],
        "session_deliverables": [],
        "session_status": "active",
        "session_rating": None,
        "session_feedback": None,
    }
    agent_client_session.insert_one(agent_session)
    # load this session into the session state
    st.session_state.loaded_session = agent_session


def get_deliverables():
    deliverable = {}
    interaction_types = [
        "Agent Chat Only",
        "Agent Chat and ExpertDM with File delivery",
        "Agent Chat and File Delivery",
    ]
    type = {"type": random.choice(interaction_types)}
    deliverable.update(type)
    return deliverable


def search_agents(search_query, field):
    # Fetch all agents
    agents = list(agent_collection.find())
    # Extract the specified field
    field_values = [agent[field] for agent in agents]
    # Perform fuzzy search
    results = process.extract(search_query, field_values, limit=5)
    # Get the corresponding agent documents
    matched_agents = [
        agents[i] for i in range(len(agents)) if field_values[i] in dict(results).keys()
    ]
    return matched_agents


@st.dialog(title="Expertline", width="large")
def run_search_starter(search_query):
    st.title("Search Results")
    agent_name_results = search_agents(search_query, "agent_name")
    instructions_results = search_agents(search_query, "agent_instructions")
    opening_statement_results = search_agents(
        search_query, "opening_statement_client_expectation"
    )

    # Combine results and remove duplicates
    combined_results = (
        agent_name_results + instructions_results + opening_statement_results
    )
    unique_results = {agent["_id"]: agent for agent in combined_results}.values()

    # Display top 5 results
    for i, agent in enumerate(list(unique_results)[:5]):
        with st.form(f"Select_agent_form_{i+1}"):
            st.write(f"### :gray[{agent['agent_name']}]")
            st.write(f"## {agent['opening_statement_client_expectation']}")
            f"""
            This agent Expects the following :
            - inputs: :red[{agent['inputs']}]
            ### :gray[Promises to deliver the following:]
            - deliverables: :red[{agent['deliverables']}]
            ### :gray[The over all Goal of This bot is to] :blue[{agent['agent_userTitle']}]
            """
            load_agent = st.form_submit_button("Load Agent", use_container_width=True)
            if load_agent:
                st.session_state.loaded_agent = agent
                start_new_session(agent, st.session_state.username)
                st.rerun()


@st.dialog(title="Experstline", width="large")
def run_project_starter(search_query):
    for i in range(5):
        with st.form(key=f"agent__{i+1}"):
            st.write(f"Agent {i+1}")
            st.write(f"Expertise: {search_query}")
            st.write(f"Agent ID: {i+1}")
            st.write(f"Agent Name: {search_query} Agent {i+1}")
            st.write(f"Agent Email:")
            load_agent = st.form_submit_button("Load Agent")
            if load_agent:
                pass
                st.rerun()


st.logo("aino.png")


if st.session_state.logged_in:
    tab1, tab2 = st.tabs(["AgentVerksted", "Socials"])
    with st.sidebar:
        with st.form(key="query_form"):

            query = st.text_input(
                "Look up Expertise",
                placeholder="Try using keywords like 'ISO 9001', 'GDPR' etc.",
            )
            if st.form_submit_button("Search", use_container_width=True):
                search_query = query.lower()
                # if emplty or less than 5 characters throw error
                if len(search_query) < 3:
                    st.error("Please enter a valid search query")
                else:
                    run_search_starter(search_query)

        file_upload = st.file_uploader(
            "Upload a file for Agent",
            type=["pdf", "docx"],
            disabled=True,
            help="Disabled if the agent does'nt allow fil",
        )

        with st.container(height=350):
            for i in range(3):
                with st.container(border=True):
                    col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                    with col1:
                        st.write(f"File {i+1}")
                    with col2:
                        download = st.button(
                            ":blue[⬇]",
                            help="Download the file",
                            key=f"download____{i+1}",
                        )
                    with col3:
                        view = st.button("↗", key=f"view_{i+1}", help="View the file")
                    with col4:
                        delete = st.button(
                            ":red[❌]", key=f"delete_{i+1}", help="Delete the file"
                        )
    with tab1:
        tab1col1, tab1col2 = st.columns([1, 2])
        with tab1col1:
            with st.expander("Agent Sessions History"):
                "get sessions for this user"
                user_sessions = list(
                    agent_client_session.find({"client": st.session_state.username})
                )
                if user_sessions:
                    for i, session in enumerate(user_sessions):
                        with st.container(border=True):
                            bbcol1, bbcol2 = st.columns([1, 1])
                            with bbcol1:
                                f"""
                                ###### :blue[{session['agent_name']}]
                                by: :gray[{session['parent']}]
                                """
                            with bbcol2:
                                f"""
                                :orange[{session['session_start']}]
                                

                                """

                                if st.button("Load Session", key=f"load_{i+1}",use_container_width=True):   
                                    st.session_state.loaded_session = session
                                    st.session_state.loaded_agent = (
                                        agent_collection.find_one(
                                            {"_id": session["agent_id"]}
                                        )
                                    )
                                    st.rerun()
                                

                else:
                    "No Session Stsarted Yet"

                pass

                # for i in range(3):
                #     with st.form( key = f"history_agent___{i}",border=True):
                #         "Chat with Agent"
                #         load_in = st.form_submit_button(f"Load Chat {i+1}",use_container_width=True)
                #         if load_in:
                #             pass
                #             st.rerun()

            with st.expander("Agent Parameters"):
                if st.session_state.loaded_agent:
                    f"""
                            ### :blue[{st.session_state.loaded_agent['agent_name']}]
                            by: :gray[{st.session_state.loaded_agent['parent']}]
                            #### :gray[Agent Behaviour :]
                            #### :blue[{st.session_state.loaded_agent['agent_userTitle']}]
                            :gray[Instructions provided:]
                            - {st.session_state.loaded_agent['agent_instructions']}
                            
                            ##### Allows Personal Communication: 
                            - :red[{st.session_state.loaded_agent['allow_personal']}]
                            ### Output Type: :blue[{st.session_state.loaded_agent['deliverables']}]
                            """
                else:
                    "No Agent Loaded"
            with st.expander(
                f":blue[Set Outputs Expectationa and Goals for this Agents Session]"
            ):

                with st.form(border=False, key="agent_params"):
                    # check if the loaded session already has a goal
                    if st.session_state.loaded_session:
                        present_aim = st.session_state.loaded_session.get("client_goal")
                        if present_aim:

                            disabled = True

                        else:
                            disabled = False
                            present_aim = ""

                        describe_aim = st.text_area(
                            "Describe your goal",
                            height=100,
                            placeholder="What info can you provide and what do you expect, timeframes, etc.",
                            value=present_aim,
                            disabled=disabled,
                        )

                        present_output_types = st.session_state.loaded_session.get(
                            "outputs"
                        )
                        if present_output_types:
                            disabled = True
                        else:
                            disabled = False

                        # only allow user to select from the available aoutput types for the agent: deliverables
                        available_outputs = st.session_state.loaded_agent[
                            "deliverables"
                        ]
                        type_output = st.multiselect(
                            label="Select Output Types",
                            options=available_outputs,
                            disabled=disabled,
                        )
                        if st.form_submit_button(
                            "Assign Task", use_container_width=True, disabled=disabled
                        ):
                            aim = describe_aim
                            outputs = type_output
                            st.session_state.loaded_session["client_goal"] = aim
                            st.session_state.loaded_session["outputs"] = outputs
                            # set in the database
                            agent_client_session.update_one(
                                {"_id": st.session_state.loaded_session["_id"]},
                                {"$set": {"client_goal": aim, "outputs": outputs}},
                            )
                            st.rerun()

            st.button("See Agent Profile", use_container_width=True)
            if st.session_state.loaded_agent:
                f":blue[Loaded Agent] : :red[{st.session_state.loaded_agent['agent_name']}]"
            else:
                f":red[No Agent Loaded]"
                
            if st.button(":green[Refresh]", use_container_width=True):
                # get session again and set it to session state
                new_session = agent_client_session.find_one(
                    {"_id": st.session_state.loaded_session["_id"]}
                )
                st.session_state.loaded_session = new_session
                st.rerun()

        with tab1col2:
            midtab, midtab2 = st.tabs(["AgentChat", "DM Expert"])
            with midtab:
                with st.container(height=650, border=True):
                    if st.session_state.loaded_session:
                        if len(st.session_state.loaded_session["client_AI_chat"]) == 0:
                            # add opening_statement to the chat 
                            opening_statement = st.session_state.loaded_agent[
                                "opening_statement_client_expectation"
                            ]
                            st.session_state.loaded_session["client_AI_chat"].append(
                                {"ai": opening_statement}
                            )
                            # add the db too
                            agent_client_session.update_one(
                                {"_id": st.session_state.loaded_session["_id"]},
                                {
                                    "$push": {
                                        "client_AI_chat": {"ai": opening_statement}
                                    }
                                },
                            )

                        for chat in st.session_state.loaded_session["client_AI_chat"]:
                            for key, value in chat.items():
                                if key == "ai":
                                    with st.chat_message("ai"):
                                        value
                                else:
                                    with st.chat_message("user"):
                                        value
                        
                    else:
                        "No Session Loaded"     
                if prompt := st.chat_input("What is up?"):
                    # if goal and Outputs are not set, do not allow user to chat
                    if not st.session_state.loaded_session.get("client_goal"):
                        st.error(
                            "Please set your goal and expected outputs before chatting"
                        )
                    else:
                    
                    # add to session state and db
                        st.session_state.loaded_session["client_AI_chat"].append(
                            {"user": prompt}
                        )
                        agent_client_session.update_one(
                            {"_id": st.session_state.loaded_session["_id"]},
                            {"$push": {"client_AI_chat": {"user": prompt}}},
                        )
                        agent_response, expert_response= fetch_agent_response(prompt, st.session_state.loaded_agent, st.session_state.loaded_session)
                        # add to session state and db
                        st.session_state.loaded_session["client_AI_chat"].append(
                            {"ai": agent_response}
                        )
                        agent_client_session.update_one(
                            {"_id": st.session_state.loaded_session["_id"]},
                            {"$push": {"client_AI_chat": {"ai": agent_response}}},
                        )
                        #process expert response (if any)
                        if expert_response:
                            query = expert_response
                            st.session_state.loaded_session["client_DM"].append(
                                {"user": query}
                            )
                            
                            agent_client_session.update_one(
                                {"_id": st.session_state.loaded_session["_id"]},
                                {"$push": {"client_DM": {"ai": expert_response}}},
                            )
                            
                            pass
                        
                        st.rerun()

            with midtab2:
                # check if allow_personal = True
                allwP = st.session_state.loaded_agent["allow_personal"]

                with st.container(height=650, border=True):
                    if allwP == "yes":
                        # show the Expert DMs
                        
                        for chat in st.session_state.loaded_session["client_DM"]:
                            for key, value in chat.items():
                                if key == "ai":
                                    with st.chat_message("ai"):
                                        value
                                elif key == "user":
                                    with st.chat_message("user"):
                                        value
                                else:
                                    with st.chat_message("Expert"):
                                        value
                                
                        
                        
                        # with st.chat_message("ai"):
                        #     "Hello, I am AINO, your Expert. How can I help you today?"
                if clinet_entry_forPvtDM := st.chat_input("Type a message...", key="dm_input"):
                    
                    # add the response with [Client Prefix]
                    # update the session and db
                    st.session_state.loaded_session["client_DM"].append(
                        {"client": clinet_entry_forPvtDM}
                        
                    )
                    agent_client_session.update_one(
                        {"_id": st.session_state.loaded_session["_id"]},
                        {"$push": {"client_DM": {"client": f"[CLIENT]:{clinet_entry_forPvtDM}"}},}
                    )
                    # check if allow_personal = True
                    
                    st.rerun()
                        
                else:
                        "Sorry, this agent does not allow personal communication"
                        st.chat_input("Personal communication is disabled for this agent.",
                                    #   placeholder="This agent does not allow personal communication.",
                                      disabled=True, key="dm_input_disabled")

        with st.expander("Project Deliverables", expanded=False):
            if not st.session_state.loaded_session:
                "No Session Loaded"
            else:
                delicol1, delicol2 = st.columns([1, 1])

                with delicol1:
                    f":gray[Aim of the Project] : :blue[{st.session_state.loaded_session['client_goal']}]"
                    f" Agent Behaviour : :blue[{st.session_state.loaded_agent['agent_userTitle']}]"
                    "Your Deliverables are as follows:"
                    f"""
                    - :blue[{st.session_state.loaded_session['outputs']}]
                    """
                    with st.form(border=True, key="feedback_form"):
                        ":gray[user Feedback and Review]"
                        rating = st.slider(
                            label="Rate the agent",
                            min_value=1,
                            max_value=5,
                            step=1,
                            value=3,
                        )
                        st.text_area("Feedback", height=100, disabled=False)
                        if st.form_submit_button(
                            "End Project", use_container_width=True
                        ):
                            pass
                            st.rerun()

                with delicol2:
                    with st.container(height=300):
                        "Deliverables"


    with tab2:
            search_skills = st.text_input(
                "Search for Skills", placeholder="Search for skills, expertise, etc.")
            space_for_socials = st.empty()

            "Featured Agents: Coming Soon"
            # acol1, acol2, acol3, acol4 = st.columns(4)
            # with acol1:
                # with st.container(border=True, height=250):
                #     "Agent 1"
                #     load_agent = st.button(
                #         "Load Agent 1", use_container_width=True, key=f"load___1"
                #     )
            # with acol2:
            #     with st.container(border=True, height=250):
            #         "Agent 2"
            #         load_agent = st.button(
            #             "Load Agent 2", use_container_width=True, key=f"load___2"
            #         )

            # with acol3:
            #     with st.container(border=True, height=250):
            #         "Agent 3"
            #         load_agent = st.button(
            #             "Load Agent 3", use_container_width=True, key=f"__load_3"
            #         )
            # with acol4:
            #     with st.container(border=True, height=250):
            #         "Agent 4"
            #         load_agent = st.button(
            #             "Load Agent 4", use_container_width=True, key=f"__load_4_"
            #         )
                    
                    
            # "Recommended Agents"
            # col1, col2, col3, col4 = st.columns(4)
            # with col1:
            #     with st.container(border=True, height=250):
            #         "Agent 1"
            #         load_agent = st.button(
            #             "Load Agent 1", use_container_width=True, key=f"load_1__"
            #         )
            # with col2:
            #     with st.container(border=True, height=250):
            #         "Agent 2"
            #         load_agent = st.button(
            #             "Load Agent 2", use_container_width=True, key=f"load_2__"
            #         )

            # with col3:
            #     with st.container(border=True, height=250):
            #         "Agent 3"
            #         load_agent = st.button(
            #             "Load Agent 3", use_container_width=True, key=f"load_3__"
            #         )
            # with col4:
            #     with st.container(border=True, height=250):
            #         "Agent 4"
            #         load_agent = st.button(
            #             "Load Agent 4", use_container_width=True, key=f"load_4__"
            #         )

else:
    "Please login to access this page"
