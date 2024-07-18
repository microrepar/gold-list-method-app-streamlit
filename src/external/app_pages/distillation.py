import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth  # pip install streamlit-authenticator
import yaml
from st_pages import add_page_title
from yaml.loader import SafeLoader

from src.adapters import Controller
from src.core.notebook import Notebook
from src.core.pagesection import Group, PageSection

st.set_page_config(layout='wide')

placeholder_container_msg = st.container()
controller = Controller()

add_page_title(layout="wide")  # Optional method to add title and icon to current page

def get_group_dataframe(pagesection):    

    sentences  = None if pagesection is None else pagesection.sentences
    
    columns = [
        "foreign_language",
        "translated_sentences",
        "remembered",
        "mother_tongue"]
    
    df = pd.DataFrame(columns=columns) if sentences is None \
        else pd.concat([pd.DataFrame(s.data_to_dataframe()) for s in sentences])


    if pagesection:
        df['translated_sentences'] = pagesection.translated_sentences
        df['remembered'] = pagesection.memorializeds
    else:
        df['translated_sentences'] = ''
        df['remembered'] = False        
    
    return df, pagesection

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
            placeholder_container_msg.error(msg, icon='🚨')
        user_id = None
    else:
        user_id = entities[-1].id
    if 'info' in messages:
        placeholder_container_msg.info('\n  - '.join(messages['info']), icon='⚠️')
    if 'warning' in messages:
        placeholder_container_msg.warning('\n  - '.join(messages['warning']), icon='ℹ️')
    if 'success' in messages:
        placeholder_container_msg.success('\n  - '.join(messages['success']), icon='✅')
    ######################################################
        
    #############################################################
    # FIND BY FIELD - NOTEBOOK
    #############################################################
    request = {
        'resource': '/notebook/find_by_field',
        'notebook_user': {'user_id_': user_id}
    }
    resp = controller(request=request)
    notebook_list = resp.get('entities')
    messages = resp.get('messages')

    if 'error' in messages:
        for msg in messages['error']:
            placeholder_container_msg.error(msg, icon="🚨")

    if 'info' in messages:
        placeholder_container_msg.info('\n  - '.join(messages['info']), icon='⚠️')
    if 'warning' in messages:
        placeholder_container_msg.warning('\n  - '.join(messages['warning']), icon='ℹ️')
    if 'success' in messages:
        placeholder_container_msg.success('\n  - '.join(messages['success']), icon='✅')
    #############################################################

    notebook_dict = {n.name: n for n in notebook_list}

    if len(notebook_list) > 0:
        selected_notebook = st.sidebar.selectbox('**SELECT NOTEBOOK:**', 
                                                [n.name for n in notebook_list],
                                                key='select_notebook')
        

        notebook: Notebook = notebook_dict.get(selected_notebook)

        placeholder_subtitle = st.empty()

        col_group_1, col_group_2, col_group_3, col_group_4 = st.sidebar.columns(4)

        selected_day = st.sidebar.date_input('**LIST OF THE DAY:**', 
                                            datetime.datetime.now().date(), 
                                            format='DD/MM/YYYY')

        pagesection_a = notebook.get_pagesection(distillation_at=selected_day,
                                                group=Group.A)
        pagesection_b = notebook.get_pagesection(distillation_at=selected_day,
                                                group=Group.B)
        pagesection_c = notebook.get_pagesection(distillation_at=selected_day,
                                                group=Group.C)
        pagesection_d = notebook.get_pagesection(distillation_at=selected_day,
                                                group=Group.D)
        
        def get_btn_label(pagesection: PageSection):
            if pagesection is None:
                return "⚠️"
            elif pagesection.distillated:
                return "✅"
            else:
                return "🟩"

        choiced_group = st.sidebar.radio('SELECT GROUP:', 
            (
                f'GROUP A - {get_btn_label(pagesection_a)}',
                f'GROUP B - {get_btn_label(pagesection_b)}',
                f'GROUP C - {get_btn_label(pagesection_c)}',
                f'GROUP D - {get_btn_label(pagesection_d)}'
            )
        )
        
        dataframe, pagesection_group = get_group_dataframe({
            'GROUP A': pagesection_a,
            'GROUP B': pagesection_b,
            'GROUP C': pagesection_c,
            'GROUP D': pagesection_d,
        }.get(choiced_group.split(' - ')[0]))

        placeholder_subtitle.subheader(f'{notebook.name.upper()} NOTEBOOK - {choiced_group}')

        st.sidebar.markdown("[Show Calendar](Calendar)")

        column_configuration = {
            "foreign_language": st.column_config.TextColumn(
                "Foreign Language", 
                help="Read aloud the sentece or word just once",
                width="large"
            ),
            "translated_sentence": st.column_config.TextColumn(
                "Translation", 
                help="Write the sentece or word in your mother tongue",
                width="large"
            ),
            "remembered": st.column_config.CheckboxColumn(
                "You remember?", 
                help="Check the checkbox if you remembered this sentence?",
                width='small'
            ),
        }

        rename_columns = {
            'remembered': 'You remember?',
            'foreign_language':'Foreign Language',
            'translated_sentences': 'Translate Sentence',
            'mother_tongue': 'Mother Tongue'
        }

        
    ##########################Group Section####################################

        distilled_columns = ['remembered', 'foreign_language', 'mother_tongue', 'translated_sentences', ]
        
        btn_update = False
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            read_aloud = st.checkbox('Read aloud', value=True, 
                                        key='read_aloud', disabled=True)
        with col2:
            translate = st.checkbox('Translate', value=True, 
                                        key='translate', disabled=True)
        with col3:
            placeholder_checkbox_distill = st.empty()
            if  pagesection_group and pagesection_group.distillated:
                distill = placeholder_checkbox_distill.checkbox(
                    'Distill', key='distill', value=True, disabled=True
                )
            else:
                distill = placeholder_checkbox_distill.checkbox(
                    'Distill', key='distill', value=False, disabled=False
                )
        
        col4.markdown(f'Date: {selected_day}')


        
        if not dataframe.empty:
        
            if read_aloud and not translate and not distill:
                df_distilled = st.data_editor(
                    dataframe[['foreign_language']],
                    column_config=column_configuration,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="fixed",
                    disabled=['foreign_language', 'mother_tongue'],
                    key='read_aloud_data')
            elif translate and not distill:
                df_distilled = st.data_editor(
                    dataframe[['foreign_language', 'translated_sentences']],
                    column_config=column_configuration,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="fixed",
                    disabled=['foreign_language'] if not pagesection_group.distillated \
                        else ['translated_sentences', 'foreign_language'],
                    key='translate_data')
                
                btn_update = st.button('RECORD TRANSLATION',
                                    use_container_width=True, 
                                    type='secondary', 
                                    key='btn_record_group_a')
            
            elif distill and not pagesection_group.distillated:
                
                df_distilled = st.data_editor(
                    dataframe[distilled_columns],
                    column_config=column_configuration,
                    use_container_width=True,
                    hide_index=True,
                    num_rows="fixed",
                    disabled=['foreign_language', 'mother_tongue', 'translated_sentences'] \
                                    if not pagesection_group.distillated \
                                    else distilled_columns,
                    key='distill_data')

            elif pagesection_group.distillated:
                st.dataframe(
                    dataframe[distilled_columns].rename(columns=rename_columns),
                    use_container_width=True, hide_index=True)
            
            
            if btn_update:
                
                df_update = df_distilled.copy().reset_index(drop=True)
                df_update['remembered'] = False
                df_update['foreign_idiom'] = notebook.foreign_idiom
                df_update['mother_idiom'] = notebook.mother_idiom
                df_update['created_at'] = selected_day

                ###############################################################
                # UPDATE PAGESECTION - BODY REQUEST
                ###############################################################
                cols_to_rename = {
                    "foreign_language":"sentence_foreign_language",
                    "mother_tongue":"sentence_mother_tongue",
                    "foreign_idiom":"sentence_foreign_idiom",
                    "mother_idiom":"sentence_mother_idiom",
                    "created_at":"sentence_created_at",
                }
                df_update.rename(columns=cols_to_rename, inplace=True)


                request = {
                    'resource': '/pagesection/update',
                    'pagesection_notebook': {'notebook_id_': notebook.id,
                                            'notebook_days_period': notebook.days_period},
                    'pagesection_id_': pagesection_group.id,
                    'pagesection_page_number': pagesection_group.page_number,
                    'pagesection_group': pagesection_group.group,
                    'pagesection_created_at': pagesection_group.created_at,
                    'pagesection_distillation_at': pagesection_group.distillation_at,
                    'pagesection_translated_sentences': df_update['translated_sentences'].to_list(),
                    'pagesection_memorializeds': df_update['remembered'].to_list(),
                    'pagesection_sentences': list(df_update.T.to_dict().values()),            
                }
                ####################
                # FrontController
                ####################
                resp = controller(request=request)
                messages = resp.get('messages')
                entities = resp.get('entities')

                ####################
                # Feadback
                ####################
                if 'error' in messages:
                    for msg in messages['error']:
                        placeholder_container_msg.error(msg,  icon="🚨")
                    st.toast('Something went wrong!')
                elif entities:
                    pagesection_group = entities[-1]
                    placeholder_container_msg.success(f'{entities[-1]} was updated successfully!')
                    placeholder_container_msg.empty()
                    st.toast('Page section was updated successfully.')
                ###############################################################
                if 'info' in messages:
                    placeholder_container_msg.info('\n  - '.join(messages['info']), icon='⚠️')
                if 'warning' in messages:
                    placeholder_container_msg.warning('\n  - '.join(messages['warning']), icon='ℹ️')
                if 'success' in messages:
                    placeholder_container_msg.success('\n  - '.join(messages['success']), icon='✅')
                ###############################################################

            if distill:
                placeholder_distill_button = st.empty()

                if placeholder_distill_button.button('HEADLIST DISTILLATION FINISH',
                                                    use_container_width=True, 
                                                    type='primary', 
                                                    key='btn_distill',
                                                    disabled=True if pagesection_group.distillated \
                                                        else False):
                    
                    df_distilled = df_distilled.reset_index(drop=True)
                    df_distilled['foreign_idiom'] = notebook.foreign_idiom
                    df_distilled['mother_idiom'] = notebook.mother_idiom

                    ###############################################################
                    # DISTILLATION PAGESECTION - BODY REQUEST
                    ###############################################################
                    cols_to_rename = {
                        "foreign_language":"sentence_foreign_language",
                        "mother_tongue":"sentence_mother_tongue",
                        "foreign_idiom":"sentence_foreign_idiom",
                        "mother_idiom":"sentence_mother_idiom",
                    }
                    df_distilled.rename(columns=cols_to_rename, inplace=True)

                    request = {
                        'resource': '/pagesection/distillation',
                        'pagesection_notebook': {'notebook_id_': notebook.id,
                                                'notebook_days_period': notebook.days_period},
                        'pagesection_id_': pagesection_group.id,
                        'pagesection_page_number': pagesection_group.page_number,
                        'pagesection_group': pagesection_group.group,
                        'pagesection_created_at': selected_day,
                        'pagesection_distillation_at': pagesection_group.distillation_at,
                        'pagesection_translated_sentences': df_distilled['translated_sentences'].to_list(),
                        'pagesection_memorializeds': df_distilled['remembered'].to_list(),
                        'pagesection_sentences': list(df_distilled.T.to_dict().values()),            
                    }
                    ####################
                    # FrontController
                    ####################
                    resp = controller(request=request)
                    messages = resp.get('messages')
                    entities = resp.get('entities')

                    ####################
                    # FeedBack
                    ####################
                    if 'error' in messages:
                        for msg in messages['error']:
                            placeholder_container_msg.error(msg,  icon="🚨")
                        st.toast('Something went wrong!')
                    elif entities:
                        pagesection_after_a = entities[-1]
                        notebook.pagesection_list.append(pagesection_after_a)

                        st.toast('Distillation was saved!')
                        placeholder_container_msg.success(f'{pagesection_after_a} was distilled successfully!')
                        
                        placeholder_distill_button.button('HEADLIST DISTILLATION FINISH', 
                                                            use_container_width=True, 
                                                            type='primary', 
                                                            key='btn_distillated',
                                                            disabled=True)
                        placeholder_checkbox_distill.checkbox('Distill', 
                                                            value=True, 
                                                            disabled=True,
                                                            key='cbox_distillated')
                    if 'info' in messages:
                        placeholder_container_msg.info('\n  - '.join(messages['info']), icon='⚠️')
                    if 'warning' in messages:
                        placeholder_container_msg.warning('\n  - '.join(messages['warning']), icon='ℹ️')
                    if 'success' in messages:
                        placeholder_container_msg.success('\n  - '.join(messages['success']), icon='✅')

                    
        else:
            st.warning('⚠️There is no a list of expressions '
                        'in "Group A" to distill on the selected day!')

    else:
        st.warning('⚠️Attention! There are no notebooks registred!')
        st.markdown('[Create a Notebook](Add%20Notebook)')

else:
    st.warning("Please access **[main page](/)** and enter your username and password.")