"""_summary_
"""

import datetime
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from st_pages import add_page_title
from streamlit_calendar import calendar
from yaml.loader import SafeLoader

from src.adapters import Controller
from src.core.notebook import Notebook

st.set_page_config(layout='wide')

placehold_container_msg = st.container()
placehold_container_msg.empty()

add_page_title(layout="wide")  # Optional method to add title and icon to current page

config_file = Path(__file__).parent / 'config.yaml'
with config_file.open('rb') as file:
    config = yaml.load(file, Loader=SafeLoader)

credentials = {'usernames': {}}
config['credentials'] = credentials

authenticator = stauth.Authenticate(
    config['credentials'],              # credentials:      Dict['usernames', Dict['<alias>', Dict['email | name | password', str]]]
    config['cookie']['name'],           # cookie:           str
    config['cookie']['key'],            # cookie:           str
    config['cookie']['expiry_days'],    # cookie:           str
    config['preauthorized'],            # preauthorized:    List[str]
)

st.session_state['username'] = st.session_state['username']
if st.session_state.username:
    # ---- SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")
    
    controller = Controller()

    
    def get_pagesection_by_notebook(notebook: Notebook):
        request = {
            'resource': '/pagesection/find_by_field_clean',
            'pagesection_notebook': notebook.to_dict_with_prefix(),
        }
        resp = controller(request=request)
        messages = resp['messages']
        entities = resp['entities']
        if 'error' in messages:
            for msg in messages['error']:
                placehold_container_msg.error(msg, icon='🚨')
        if 'info' in messages:
            placehold_container_msg.info('\n  - '.join(messages['info']), icon='⚠️')
        if 'warning' in messages:
            placehold_container_msg.warning('\n  - '.join(messages['warning']), icon='ℹ️')
        if 'success' in messages:
            placehold_container_msg.success('\n  - '.join(messages['success']), icon='✅')
        return entities

    
    #############################################################
    # REQUEST USER FIND  BY FIELD
    #############################################################
    request = {
        'resource': '/notebook',
    }
    resp = controller(request=request)
    messages = resp['messages']
    entities = resp['entities']
    notebook_list = entities
    # RESPONSE MESSAGES##########################################        
    if 'error' in messages:
        for msg in messages['error']:
            placehold_container_msg.error(msg, icon='🚨')
    if 'info' in messages:
        placehold_container_msg.info('\n  - '.join(messages['info']), icon='⚠️')
    if 'warning' in messages:
        placehold_container_msg.warning('\n  - '.join(messages['warning']), icon='ℹ️')
    if 'success' in messages:
        placehold_container_msg.success('\n  - '.join(messages['success']), icon='✅')
    #############################################################
    #############################################################

    if 'flag_alter_calendar' not in st.session_state:
        st.session_state.flag_alter_calendar = True
    
    if 'flag_events' not in st.session_state:
        st.session_state.flag_events = True
    
    if 'events' not in st.session_state:
        st.session_state.events = []
   

    def on_change_notebook():
        st.session_state.flag_alter_calendar = not st.session_state.flag_alter_calendar
        st.session_state.flag_events = True

    notebook_dict = {n.name: n for n in notebook_list}
    if len(notebook_list) > 0:
        selected_notebook = st.sidebar.selectbox('**NOTEBOOK:**', 
                                                [n.name for n in notebook_list],
                                                on_change=on_change_notebook,
                                                key='select_notebook')

        notebook: Notebook = notebook_dict.get(selected_notebook)

        st.subheader(f'{notebook.name.upper()} NOTEBOOK')

        col_group_1, col_group_2, col_group_3, col_group_4 = st.sidebar.columns(4)

        # st.sidebar.markdown("[Add New Headlist](Add%20HeadList)")
        # st.sidebar.markdown("[Distillation](Distillation)")
        # st.sidebar.divider()
        calendar_resources = [
            {"id": "a", "building": "Building A", "title": "Group A"},
            {"id": "b", "building": "Building A", "title": "Group B"},
            {"id": "c", "building": "Building B", "title": "Group C"},
            {"id": "d", "building": "Building B", "title": "Group D"},
        ]

        calendar_options = {
            "editable": "true",
            "navLinks": "true",
            "resources": calendar_resources,
        }

        calendar_options = {
            **calendar_options,
            "headerToolbar": {
                "left": "today prev,next",
                "center": "title",
                "right": "dayGridDay,dayGridWeek,dayGridMonth,multiMonthYear",
            },
            "initialDate": f"{datetime.datetime.now().date()}",
            "initialView": "dayGridMonth",
        }
            
        mode = 'daygrid'

        if st.session_state.flag_events:
            st.session_state.events = [ps.get_distillation_event() for ps in get_pagesection_by_notebook(notebook)]
            st.session_state.flag_events = False

        if st.session_state.flag_alter_calendar:
            state = calendar(
                events=st.session_state.events,
                options=calendar_options,
                key=mode+'1',
            )
        else:     
            state = calendar(
                events=st.session_state.events,
                options=calendar_options,
                key=mode+'2',
            )

        # TODO: find param to set calendar initialDate
        st.button('UPDATE CALENDAR', 
                use_container_width=True,
                on_click=on_change_notebook, 
                type='primary')
        
    else:
        st.warning('⚠️Attention! There are no notebooks registred!')
        st.markdown('[Create a Notebook](Add%20Notebook)')
else:
    st.warning("Please access **[main page](/)** and enter your username and password.")
