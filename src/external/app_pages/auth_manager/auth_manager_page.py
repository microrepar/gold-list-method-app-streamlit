"""Auth Manager main page
"""
import streamlit as st
from st_pages import add_page_title

from src.core.user import User

st.set_page_config(layout='wide')
add_page_title(layout='wide')

placeholder_msg = st.empty()


def on_click_btn_pages(*args, **kwargs):
    if kwargs.get('btn') == 'signup':
        st.session_state.btn_signup_page = True
        st.session_state.btn_reset_password_page = False

    elif kwargs.get('btn') == 'reset_password':
        st.session_state.btn_reset_password_page = True
        st.session_state.btn_signup_page = False
    else:
        st.session_state.btn_reset_password_page = False
        st.session_state.btn_signup_page = False


if st.session_state.get('username'):
    username = st.session_state['username']
    credentials = st.session_state['credentials']
    user: User = credentials['usernames'][username]['user']    
    authenticator = st.session_state.authenticator

    # ---- LOGOUT SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")

    if 'btn_signup_page' not in st.session_state:
        if username == 'admin':
            st.session_state.btn_signup_page = True
        else:
            st.session_state.btn_signup_page = False

    if 'btn_reset_password_page' not in st.session_state:
        if username == 'admin':
            st.session_state.btn_reset_password_page = False
        else:
            st.session_state.btn_reset_password_page = True

    # ----------Sidebar Buttons----------
    if username == 'admin':        
        st.sidebar.button('Reset Password', 
                        type='primary' if st.session_state.btn_reset_password_page else 'secondary', 
                        on_click=on_click_btn_pages,
                        kwargs={'btn': 'reset_password'},
                        use_container_width=True)
        
        st.sidebar.button('Sign Up', 
                        type='primary' if st.session_state.btn_signup_page else 'secondary', 
                        on_click=on_click_btn_pages,
                        kwargs={'btn': 'signup'},
                        use_container_width=True)
    else:
        st.sidebar.button('Reset Password', 
                        type='primary' if st.session_state.btn_reset_password_page else 'secondary', 
                        on_click=on_click_btn_pages,
                        kwargs={'btn': 'reset_password'},
                        use_container_width=True)
        
    if st.session_state.btn_signup_page:
        from src.external.app_pages.auth_manager.signup import signup_page
        signup_page(authenticator, credentials, username)

    if st.session_state.btn_reset_password_page:
        from src.external.app_pages.auth_manager.reset_password import \
            reset_password_page
        reset_password_page(authenticator, credentials, username, placeholder_msg)
else:
    if 'btn_signup_page' in st.session_state:
        st.session_state.pop('btn_signup_page')

    if 'btn_reset_password_page' in st.session_state:
        st.session_state.pop('btn_reset_password_page')
        