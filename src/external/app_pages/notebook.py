import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from st_pages import add_page_title
from yaml.loader import SafeLoader

from src.adapters import Controller

controller = Controller()

st.set_page_config(layout='wide')

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
placehold_msg = st.empty()

with placehold_msg:
    placehold_msg_container = st.container()

add_page_title(layout="wide")
 
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

    with st.form("my_form"):   
        st.write("Create Notebook")
        notebook_name = st.text_input('Notebook name')
        col1, col2 = st.columns(2)
        foreign_idiom = col1.text_input('Foreign idiom')
        mother_idiom = col2.text_input('Mother idiom')
        col1, col2 = st.columns(2)
        list_size = col1.slider("List size", min_value=10, max_value=25, value=20)
        days_period = col2.slider("Days period", min_value=5, max_value=20, value=15)

        # Every form must have a submit button.
        submitted = st.form_submit_button("ADD NEW NOTEBOOK", type="primary", use_container_width=True)

    if submitted:
        ######################################################
        # FIND BY FIELD - USER
        ######################################################
        request = {
            'resource': '/user/find_by_field',
            'user_username': st.session_state.username
        }
        resp = controller(request=request)
        messages = resp['messages']
        entities = resp['entities']

        if 'error' in messages:
            for msg in messages['error']:
                placehold_msg_container.error(msg, icon='🚨')
            user_id = None
        else:
            user_id = entities[-1].id
        if 'info' in messages:
            placehold_msg_container.info('\n  - '.join(messages['info']), icon='ℹ️')
        if 'warning' in messages:
            placehold_msg_container.warning('\n  - '.join(messages['warning']), icon='⚠️')
        if 'success' in messages:
            placehold_msg_container.success('\n  - '.join(messages['success']), icon='✅')
        ######################################################

        ######################################################
        # REGISTRY NOTEBOOK
        ######################################################
        request = {
            'resource': '/notebook/registry',
            'notebook_name': notebook_name,
            'notebook_sentence_list_size': list_size,
            'notebook_days_period': days_period,
            'notebook_foreign_idiom': foreign_idiom,
            'notebook_mother_idiom': mother_idiom,
            'notebook_user': {'user_id_': user_id},
        }

        resp = controller(request=request)

        messages = resp.get('messages')
        
        if 'error' in messages:
            for msg in messages['error']:
                placehold_msg_container.error(str(msg), icon="🚨")
            else:
                st.toast('Something went wrong!')
        else:
            new_notebook = resp.get('entities', [None])[-1]
            placehold_msg_container.success(f'{new_notebook} was inserted successfully!')
            st.toast('Notebook was inserted successfully.')
        ######################################################

    ######################################################
    # FIND BY FIELD - USER
    ######################################################
    request = {
        'resource': '/user/find_by_field',
        'user_username': st.session_state.username
    }
    resp = controller(request=request)
    messages = resp['messages']
    entities = resp['entities']

    if 'error' in messages:
        for msg in messages['error']:
            placehold_msg_container.error(msg, icon='🚨')
        user_id = None
    else:
        user_id = entities[-1].id
    if 'info' in messages:
        placehold_msg_container.info('\n  - '.join(messages['info']), icon='ℹ️')
    if 'warning' in messages:
        placehold_msg_container.warning('\n  - '.join(messages['warning']), icon='⚠️')
    if 'success' in messages:
        placehold_msg_container.success('\n  - '.join(messages['success']), icon='✅')
    ######################################################
    
    ######################################################
    # FIND BY FIELD - NOTEBOOK
    ######################################################
    request = {
        'resource': '/notebook/find_by_field',
        'notebook_user': {'user_id_': user_id}
    }
    resp = controller(request)

    messages = resp['messages']
    entities = resp['entities']

    if 'error' in messages:
        for msg in messages['error']:
            placehold_msg_container.error(msg, icon='🚨')
        user_id = None
    if 'info' in messages:
        placehold_msg_container.info('\n  - '.join(messages['info']), icon='ℹ️')
    if 'warning' in messages:
        placehold_msg_container.warning('\n  - '.join(messages['warning']), icon='⚠️')
    if 'success' in messages:
        placehold_msg_container.success('\n  - '.join(messages['success']), icon='✅')
    ######################################################

    st.divider()

    notebook_list = resp.get('entities')
    if notebook_list:
        df_list = (pd.DataFrame(n.data_to_dataframe()) for n in notebook_list)
        df = pd.concat(df_list, ignore_index=True)
        st.markdown('#### Last Resgistred Notebooks')
        st.dataframe(df.iloc[:, 1:], hide_index=True, use_container_width=True)
        st.markdown(f'Lines total: {df.shape[0]}')
    else:
        st.subheader('Notebooks')
        st.markdown(':red[Atteption! There are no registred notebooks.]')
else:
    st.warning("Please access **[main page](/)** and enter your username and password.")