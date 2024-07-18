import os
from pathlib import Path

import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from dotenv import load_dotenv
from st_pages import Page, Section, add_page_title, show_pages
from yaml.loader import SafeLoader

from src.adapters.controller import Controller

# import ptvsd
# ptvsd.enable_attach(address=('localhost', 5678))
# ptvsd.wait_for_attach() # Only include this line if you always want to attach the debugger

load_dotenv()

st.set_page_config(layout='wide')

placeholder_msg = st.empty()

config_file = Path(__file__).parent / 'src/external/app_pages' / 'config.yaml'
with config_file.open('rb') as file:
    config = yaml.load(file, Loader=SafeLoader)

#############################################################
### GET ALL USERS ###
#############################################################
controller = Controller()
request    = {'resource': '/user'}
resp       = controller(request=request)
#############################################################
messages = resp['messages']
entities = resp['entities']
#############################################################


credentials = {'usernames': {}}
if not messages:
    for user in entities:
        credentials['usernames'].setdefault(user.username, {})
        credentials['usernames'][user.username]['name'] = user.name
        credentials['usernames'][user.username]['email'] = user.email
        credentials['usernames'][user.username]['password'] = user.password
else:
    placeholder_msg.warning('\n\n'.join(messages))

config['credentials'] = credentials
st.session_state.credentials = credentials

authenticator = stauth.Authenticate(
    config['credentials'],              # credentials:      Dict['usernames', Dict['<alias>', Dict['email | name | password', str]]]
    config['cookie']['name'],           # cookie:           str
    config['cookie']['key'],            # cookie:           str
    config['cookie']['expiry_days'],    # cookie:           str
    config['preauthorized'],            # preauthorized:    List[str]
)

name, authentication_status, username = authenticator.login("Login", "sidebar")

if authentication_status == False:
    st.sidebar.error("Username/password is incorrect")

if authentication_status == None:
    st.sidebar.warning("Please enter your username and password to access application")

if authentication_status:
    # ---- SIDEBAR ----
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")

    st.session_state.username = username

    if username == 'admin':
        show_pages(
            [   Page("streamlit_app.py", "GOLD LIST METHOD", "🪙"),
                Page("src/external/app_pages/calendar.py", "Calendar", "🗓️"),
                # Page("src/external/app_pages/maps.py", "Folium", "🗺️"),
                Page("src/external/app_pages/distillation.py", "Distillation", "🧠"),
                Page("src/external/app_pages/headlist.py", "HeadList", "📃"),
                # Section(name="Notebooks", icon=":books:"),
                Section(name="NOTEBOOKS"),
                # # Can use :<icon-name>: or the actual icon 
                Page("src/external/app_pages/notebook.py", "Add Notebook", "📖"),
                # Section(name="ADMIN", icon="⚙️"),
                Section(name="LOGIN ADMIN"),
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


    placehold_container_msg = st.container()
    placehold_container_msg.empty()

else:
    show_pages(
        [Page("streamlit_app.py", "GOLD LIST METHOD", "🪙"),]
    )


add_page_title(layout="wide")
  # Optional method to add title and icon to current page

title = 'GOLD LIST METHOD'
subtitle = 'The Key to Effective Language Learning'

introdution = """
Have you ever dreamed of mastering a new language but felt overwhelmed by the amount of vocabulary you need to learn? If so, the "Gold List Method" might be the solution you've been searching for. This language learning method offers a unique and proven approach to memorizing words and phrases, enabling you to achieve remarkable results.

The "Gold List Method" is a learning technique that focuses on retaining information through spaced repetition. It was developed to simplify the memorization process and make it more efficient, especially when it comes to learning a new language.

The operation of the Gold List Method is quite simple yet incredibly effective. It begins with creating a "List of Words, phrases, or expressions" in the language you want to learn, along with translations into your native language. After 15 days, following the calendar, you passively review the list, marking the words you have memorized. The words not memorized are copied to a new list for review at a future date. This process is repeated at spaced intervals of 15 days, harnessing the power of spaced repetition, a concept based on scientific research into long-term memory.

The Gold List Method is designed to help you remember words and phrases for an extended period, not just temporarily. It optimizes your study time, allowing you to memorize more with less effort. It relieves the pressure of trying to memorize everything at once, making learning more relaxed and effective. Plus, you can customize your lists to match your specific interests and needs.

Mastering a new language can open doors to incredible opportunities, whether for travel, work, or connecting with people from around the world. The "Gold List Method" offers a proven and effective approach to accelerate your language learning progress. So, if you'd like to experience the Method in a practical and efficient way, we invite you to explore our application implemented with this revolutionary technique. Discover how this method can make learning a new language a more enjoyable and successful journey. Give the Gold List Method a chance, and be amazed by the results it can offer. Start your journey of effective and memorable language learning today!

"""

# st.title(title)
st.header(subtitle)

# Use HTML para justificar o texto
for paragrafo in introdution.splitlines():
    st.markdown(f'<p style="text-align: justify;">{paragrafo}</p>', unsafe_allow_html=True)

st.markdown('[E-book here](https://www.languagementoring.com/wp-content/uploads/2018/11/The-Goldlist-method-in-a-Nutshell-Language-mentoring.pdf)')