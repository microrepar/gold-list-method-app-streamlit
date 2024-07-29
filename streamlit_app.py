import streamlit as st
from dotenv import load_dotenv
from st_pages import Page, add_page_title

from src.external.app_pages.auth_manager.authentication import streamlit_auth

import ptvsd
ptvsd.enable_attach(address=('localhost', 5678))
ptvsd.wait_for_attach() # Only include this line if you always want to attach the debugger

load_dotenv()

st.set_page_config(layout='wide')
add_page_title(layout="wide")       # Optional method to add title and icon to current page

placeholder_msg = st.empty()
streamlit_auth(placeholder_msg)

if st.session_state.get('username'):
    # ---- SIDEBAR ----
    st.session_state.authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")


title = st.header('GOLD LIST METHOD')
subtitle = st.subheader('The Key to Effective Language Learning')

introdution = """
Have you ever dreamed of mastering a new language but felt overwhelmed by the amount of vocabulary you need to learn? If so, the "Gold List Method" might be the solution you've been searching for. This language learning method offers a unique and proven approach to memorizing words and phrases, enabling you to achieve remarkable results.

The "Gold List Method" is a learning technique that focuses on retaining information through spaced repetition. It was developed to simplify the memorization process and make it more efficient, especially when it comes to learning a new language.

The operation of the Gold List Method is quite simple yet incredibly effective. It begins with creating a "List of Words, phrases, or expressions" in the language you want to learn, along with translations into your native language. After 15 days, following the calendar, you passively review the list, marking the words you have memorized. The words not memorized are copied to a new list for review at a future date. This process is repeated at spaced intervals of 15 days, harnessing the power of spaced repetition, a concept based on scientific research into long-term memory.

The Gold List Method is designed to help you remember words and phrases for an extended period, not just temporarily. It optimizes your study time, allowing you to memorize more with less effort. It relieves the pressure of trying to memorize everything at once, making learning more relaxed and effective. Plus, you can customize your lists to match your specific interests and needs.

Mastering a new language can open doors to incredible opportunities, whether for travel, work, or connecting with people from around the world. The "Gold List Method" offers a proven and effective approach to accelerate your language learning progress. So, if you'd like to experience the Method in a practical and efficient way, we invite you to explore our application implemented with this revolutionary technique. Discover how this method can make learning a new language a more enjoyable and successful journey. Give the Gold List Method a chance, and be amazed by the results it can offer. Start your journey of effective and memorable language learning today!

"""

# Use HTML para justificar o texto
for paragrafo in introdution.splitlines():
    st.markdown(f'<p style="text-align: justify;">{paragrafo}</p>', unsafe_allow_html=True)

st.markdown('[E-book here](https://www.languagementoring.com/wp-content/uploads/2018/11/The-Goldlist-method-in-a-Nutshell-Language-mentoring.pdf)')