from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from dotenv import load_dotenv
from st_pages import Page, Section, add_page_title, show_pages
from yaml.loader import SafeLoader

from src.adapters.controller import Controller


def streamlit_auth(placeholder_msg):    
    config_file = Path(__file__).parent / 'config.yaml'
    with config_file.open('rb') as file:
        config = yaml.load(file, Loader=SafeLoader)

    if 'entities' not in st.session_state:
        #############################################################
        ### GET ALL USERS ###
        #############################################################
        controller = Controller()
        request    = {'resource': '/user'}
        resp       = controller(request=request)
        #############################################################
        messages = resp['messages']
        entities = resp['entities']
        st.session_state.entities = entities
        st.session_state.messages = messages
        #############################################################

    credentials = {'usernames': {}}
    if not st.session_state.messages:
        for user in st.session_state.entities:        
            credentials['usernames'].setdefault(user.username, {})
            credentials['usernames'][user.username]['id'] = user.name
            credentials['usernames'][user.username]['name'] = user.name
            credentials['usernames'][user.username]['email'] = user.email
            credentials['usernames'][user.username]['password'] = user.password
            credentials['usernames'][user.username]['user'] = user
    else:
        placeholder_msg.warning('\n\n'.join(st.session_state.messages))

    if 'credentials' not in st.session_state:
        st.session_state.credentials = credentials

    if 'config' not in st.session_state:
        st.session_state.config = config
        st.session_state.config['credentials'] = st.session_state.credentials    

    config = st.session_state.config

    authenticator = stauth.Authenticate(
        config['credentials'],              # credentials:      Dict['usernames', Dict['<alias>', Dict['email | name | password', str]]]
        config['cookie']['name'],           # cookie:           str
        config['cookie']['key'],            # cookie:           str
        config['cookie']['expiry_days'],    # cookie:           str
        config['preauthorized'],            # preauthorized:    List[str]
    )

    if 'authenticator' not in st.session_state:
        st.session_state.authenticator = authenticator

    name, authentication_status, username = authenticator.login("Login", "sidebar")

    if authentication_status == False:
        st.sidebar.error("Username/password is incorrect")

    if authentication_status == None:
        st.sidebar.warning("Please enter your username and password to access application")

    if authentication_status:
        
        if username == 'admin':
            show_pages(
                [   Page("streamlit_app.py", "HOME", "🪙"),
                    Page("src/external/app_pages/calendar.py", "Calendar", "🗓️"),
                    # Page("src/external/app_pages/maps.py", "Folium", "🗺️"),
                    Page("src/external/app_pages/headlist.py", "HeadList", "📃"),
                    Page("src/external/app_pages/distillation.py", "Distillation", "🧠"),
                    # Section(name="Notebooks", icon=":books:"),
                    # Section(name="NOTEBOOKS"),
                    # # Can use :<icon-name>: or the actual icon 
                    Page("src/external/app_pages/notebook.py", "Add Notebook", "📖"),
                    # Section(name="ADMIN", icon="⚙️"),
                    # Section(name="LOGIN ADMIN"),
                    Page("src/external/app_pages/user_update.py", "User update", "🔄️"),
                    # Page("src/external/app_pages/signup.py", "Sign up", "🔑"),
                ]
            )
        else:
            show_pages(
                [   Page("streamlit_app.py", "GOLD LIST METHOD", "🪙"),
                    Page("src/external/app_pages/calendar.py", "Calendar", "🗓️"),
                    # Section(name="Notebooks", icon=":books:"),
                    # # Can use :<icon-name>: or the actual icon 
                    Page("src/external/app_pages/headlist.py", "HeadList", "📃"),
                    Page("src/external/app_pages/distillation.py", "Distillation", "🧠"),
                    # Page("src/external/app_pages/notebook.py", "Notebook", "📖"),
                ]
            )
            
    else:
        show_pages(
            [Page("streamlit_app.py", "GOLD LIST METHOD", "🪙"),]
        )
    
    # return name, authentication_status, username, authenticator, credentials, user_dict
