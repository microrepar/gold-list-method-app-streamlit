import pandas as pd
import streamlit as st  # pip install streamlit
from st_pages import add_page_title

from src.core.user import User
from src.adapters import Controller

# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(layout="wide")

add_page_title(layout="wide")
placeholder_msg = st.empty()

if st.session_state.get('username'):
    # ---- SIDEBAR ----
    st.session_state.authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")
    
    username = st.session_state['username']
    credentials = st.session_state['credentials']
    user: User = st.session_state['credentials']['usernames'][username]['user']

    try:
        col1, col2 = st.columns(2)
        selected_username = col1.selectbox('Username', list(credentials['usernames']))
        field = col2.selectbox('Field', ['name', 'email'])

        new_value = None
        actual_value = None

        with st.form("my_form"):   
            st.write("### Update user detail")
            actual_value = st.text_input('Actual value', 
                          value=credentials['usernames'][selected_username][field], 
                          disabled=True)
            new_value = st.text_input('New value')
            # Every form must have a submit button.
            submitted = st.form_submit_button("UPDATE USER", type="primary")

        if submitted:
            #############################################################
            ### UPDATE USER ###
            #############################################################
            request = {'resource': '/user/update_detail',
                       'user_username': selected_username 
                       }
            request.setdefault(f'user_{field}', new_value)

            controller = Controller()
            resp = controller(request=request)
            msg = resp.get('messages')
            
            messages = resp['messages']
            entities = resp['entities']

            if 'error' in messages:
                raise Exception('\n\n'.join(messages['error']))
            #############################################################

            st.success(f'User change {field} from "{actual_value}" to "{new_value}" registred successfully')       

    except Exception as e:
        placeholder_msg.error(e)
        st.error(e)

    #############################################################
    ### GET ALL USERS ###
    #############################################################
    controller = Controller()
    request    = {'resource': '/user'}
    resp       = controller(request=request)
    #############################################################
    messages = resp['messages']
    entities = resp['entities']

    if 'error' in messages:
        placeholder_msg.erro('\n\n'.join(messages['error']), icon='🚨')
    #############################################################

    st.divider()

    if entities:
        st.markdown('### Users')
        df = pd.concat([pd.DataFrame(u.data_to_dataframe()) for u in entities], ignore_index=True)
        st.dataframe(df, hide_index=True, use_container_width=True)
    else:
        st.markdown('### Users')
        st.markdown(':red[Atteption! There are no registred users.]')

else:
    st.warning("Please access **[main page](/)** and enter your username and password.")
