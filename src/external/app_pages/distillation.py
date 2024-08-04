import datetime

import pandas as pd
import streamlit as st
from st_pages import add_page_title

from src.adapters import Controller
from src.core.notebook import Notebook
from src.core.pagesection import Group, PageSection
from src.core.user import User


def get_group_dataframe(pagesection):
    sentencelabels = None
    if pagesection:
        if pagesection.sentencelabels:
            sentencelabels = pagesection.sentencelabels

    columns = [
        'sentencelabel_id'
        "foreign_language",
        "translated_sentences",
        "remembered",
        "mother_tongue"]
    
    df = pd.DataFrame(columns=columns) if sentencelabels is None \
        else pd.concat([pd.DataFrame(s.sentencetranslation.data_to_dataframe()) 
                        for s in sentencelabels], ignore_index=True)

    if pagesection:
        df['translated_sentences'] = [{None: ''}.get(sl.translation, sl.translation) for sl in pagesection.sentencelabels]
        df['remembered'] = [sl.memorized for sl in pagesection.sentencelabels]
    else:
        df['translated_sentences'] = ''
        df['remembered'] = False
    return df


st.set_page_config(layout='wide')

placeholder_container_msg = st.container()
controller = Controller()

add_page_title(layout="wide")  # Optional method to add title and icon to current page

if st.session_state.get('username') and st.session_state.get('credentials', {}).get('usernames'):
    username = st.session_state['username']
    user: User = st.session_state['credentials']['usernames'][username]['user']

    #############################################################
    # REQUEST NOTEBOOK FIND BY FIELD CLEAN
    #############################################################
    request = {
        'resource': '/notebook/find_by_field_clean',
        'notebook_user': {'user_id_': user.id},
    }
    resp = controller(request=request)
    messages = resp['messages']
    entities = resp['entities']
    notebook_list = entities
    # RESPONSE MESSAGES##########################################        
    if 'error' in messages:
        for msg in messages['error']:
            placeholder_container_msg.error(msg, icon='🚨')
    if 'info' in messages:
        placeholder_container_msg.info('\n  - '.join(messages['info']), icon='⚠️')
    if 'warning' in messages:
        placeholder_container_msg.warning('\n  - '.join(messages['warning']), icon='ℹ️')
    if 'success' in messages:
        placeholder_container_msg.success('\n  - '.join(messages['success']), icon='✅')
    #############################################################
    #############################################################
    
    notebook_dict = {n.name: n for n in notebook_list}
    if len(notebook_list) > 0:
        selected_notebook = st.sidebar.selectbox(
            '**SELECT NOTEBOOK:**', [n.name for n in notebook_list], key='select_notebook')

        col_group_1, col_group_2, col_group_3, col_group_4 = st.sidebar.columns(4)
        selected_day = st.sidebar.date_input(
            '**LIST OF THE DAY:**', datetime.datetime.now().date(), format='DD/MM/YYYY')        
        notebook: Notebook = notebook_dict.get(selected_notebook)

        #############################################################
        # REQUEST PAGESECTION FIND BY FIELD DEPTH - NOTEBOOK AND DISTILLATION_AT
        #############################################################
        request = {
            'resource': '/pagesection/find_by_field/depth',
            'pagesection_notebook': {'notebook_id_': notebook.id},
            'pagesection_distillation_at': selected_day,
        }
        resp = controller(request=request)
        messages = resp['messages']
        entities = resp['entities']
        notebook.pagesection_list = entities
        # RESPONSE MESSAGES##########################################        
        if 'error' in messages:
            for msg in messages['error']:
                placeholder_container_msg.error(msg, icon='🚨')
        if 'info' in messages:
            placeholder_container_msg.info('\n  - '.join(messages['info']), icon='⚠️')
        if 'warning' in messages:
            placeholder_container_msg.warning('\n  - '.join(messages['warning']), icon='ℹ️')
        if 'success' in messages:
            placeholder_container_msg.success('\n  - '.join(messages['success']), icon='✅')
        #############################################################
        #############################################################

        pagesection_a = notebook.get_pagesection(distillation_at=selected_day,
                                                group=Group.A)
        pagesection_b = notebook.get_pagesection(distillation_at=selected_day,
                                                group=Group.B)
        pagesection_c = notebook.get_pagesection(distillation_at=selected_day,
                                                group=Group.C)
        pagesection_d = notebook.get_pagesection(distillation_at=selected_day,
                                                group=Group.D)        

        ########################################################################
        def get_btn_label(pagesection: PageSection):
            if pagesection is None:
                return "⚠️"
            elif pagesection.distillated:
                return "✅"
            else:
                return "🟧"

        choiced_group = st.sidebar.radio('SELECT GROUP:', 
            (
                f'GROUP A - {get_btn_label(pagesection_a)}',
                f'GROUP B - {get_btn_label(pagesection_b)}',
                f'GROUP C - {get_btn_label(pagesection_c)}',
                f'GROUP D - {get_btn_label(pagesection_d)}'
            )
        )        
        pagesection_group_dict = {
            'GROUP A': pagesection_a,
            'GROUP B': pagesection_b,
            'GROUP C': pagesection_c,
            'GROUP D': pagesection_d,
        }
        pagesection_group = pagesection_group_dict.get(choiced_group.split(' - ')[0])
        dataframe = get_group_dataframe(pagesection_group)
        ########################################################################

        placeholder_subheader_empty = st.empty()
        placeholder_subheader_empty.subheader(f'{notebook.name.upper()} NOTEBOOK - {choiced_group}')

        ########################################################################
        if st.session_state.get('flag_success_msg'):
            msg_success = st.session_state.pop('flag_success_msg')
            placeholder_container_msg.success(msg_success)
            st.toast('Action executed successfully.')

        if st.session_state.get('flag_info_msg'):
            info_msg = st.session_state.pop('flag_info_msg')
            placeholder_container_msg.info(info_msg)
            
        if st.session_state.get('flag_warning_msg'):
            warning_msg = st.session_state.pop('flag_warning_msg')
            placeholder_container_msg.warning(warning_msg)

        if st.session_state.get('flag_error_msg'):
            error_msg = st.session_state.pop('flag_error_msg')
            placeholder_container_msg.error(error_msg)
            st.toast("Something went wrong!")
        ########################################################################
        if not dataframe.empty:
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
                    "Remembered?", 
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
        
            distilled_columns = ['remembered', 'foreign_language', 
                                'mother_tongue', 'translated_sentences',]
            
            btn_update = False        
            col1, col2, col3, col4 = st.columns(4)
            
            placeholder_form = st.empty()
            form = placeholder_form.form('distill_form', clear_on_submit=True, border=False)

            with col1:
                read_aloud = st.checkbox('Read aloud', value=True, 
                                            key='read_aloud', disabled=True)
            with col2:
                translate = st.checkbox('Translate', value=True, 
                                            key='translate', disabled=True)
            with col3:
                placeholder_checkbox_distill = st.empty()
                if pagesection_group and pagesection_group.distillated:
                    distill = st.checkbox(
                        'Distill', key='distill', value=True, disabled=True 
                    )
                else:
                    distill = placeholder_checkbox_distill.checkbox(
                        'Distill', key='distill', value=False, disabled=False 
                    )
            col4.markdown(f'Date: {selected_day}')
        
            if read_aloud and not translate and not distill:
                df_distilled = form.data_editor(
                    dataframe[['foreign_language']], column_config=column_configuration, num_rows="fixed",
                    hide_index=True, use_container_width=True, disabled=['foreign_language', 'mother_tongue'],
                    key='form_data_editor'
                )
                    
            elif translate and not distill:
                if 'retry_df_update' in st.session_state:
                    dataframe = st.session_state.get('retry_df_update')

                df_distilled = form.data_editor(
                    dataframe[['foreign_language', 'translated_sentences']], column_config=column_configuration,
                    use_container_width=True, hide_index=True, num_rows="fixed", key='form_data_editor',
                    disabled=['foreign_language'] if not pagesection_group.distillated else ['translated_sentences', 'foreign_language'],
                )
                btn_update = form.form_submit_button('RECORD TRANSLATION', use_container_width=True, type='primary')
            
            elif distill and not pagesection_group.distillated:
                if 'retry_df_distilled' in st.session_state:
                    dataframe = st.session_state.get('retry_df_distilled')

                df_distilled = form.data_editor(
                    dataframe[distilled_columns], column_config=column_configuration, 
                    use_container_width=True, hide_index=True, num_rows="fixed", key='form_data_editor',
                    disabled=['foreign_language', 'mother_tongue', 'translated_sentences'] if not pagesection_group.distillated else distilled_columns,
                )

            elif pagesection_group.distillated:
                df_distilled = form.dataframe(dataframe[distilled_columns].rename(columns=rename_columns),use_container_width=True, hide_index=True)
            
            if btn_update:
                if 'retry_df_update' in st.session_state:
                    st.session_state.pop('retry_df_update')

                df_update = df_distilled.copy().reset_index(drop=True)
                df_update['remembered'] = False
                df_update['foreign_idiom'] = notebook.foreign_idiom
                df_update['mother_idiom'] = notebook.mother_idiom
                df_update['updated_at'] = selected_day

                sentencelabel_updated_list = []
                for sl, dist_update_dict in zip(pagesection_group.sentencelabels, list(df_update.T.to_dict().values())):
                    sl.translation = dist_update_dict['translated_sentences']
                    sl.memorized = dist_update_dict['remembered']
                    sentencelabel_updated_list.append(sl)

                ###############################################################
                # UPDATE PAGESECTION - BODY REQUEST
                ###############################################################
                request = {
                    'resource': '/pagesection/update_depth',
                    'pagesection_id_': pagesection_group.id,
                    'pagesection_sentencelabels': [sl.to_dict_with_prefix() for sl in sentencelabel_updated_list],            
                }
                ###############################################################
                # FrontController
                ###############################################################
                resp = controller(request=request)
                messages = resp.get('messages')
                entities = resp.get('entities')
                ###############################################################
                # Feadback
                ###############################################################
                if 'error' in messages:
                    st.session_state.retry_df_update = df_update
                    for msg in messages['error']:
                        st.session_state['flag_error_msg'] = "\n  - ".join(messages["error"])
                
                elif entities:
                    pagesection_group = entities[-1]
                    
                if 'info' in messages:
                    st.session_state['flag_info_msg'] = "\n  - ".join(messages["info"])

                if 'warning' in messages:
                    st.session_state['flag_warning_msg'] = "\n  - ".join(messages["warning"])

                if 'success' in messages:
                    st.session_state['flag_success_msg'] = "\n  - ".join(messages["success"])                    
                ###############################################################
                ###############################################################

                st.rerun()

            if distill:
                placeholder_distill_button = st.empty()

                if form.form_submit_button('HEADLIST DISTILLATION FINISH', use_container_width=True, type='primary', 
                                           disabled=True if pagesection_group.distillated else False):
                    if 'retry_df_distilled' in st.session_state:
                        st.session_state.pop('retry_df_distilled')
                    
                    df_distilled = df_distilled.reset_index(drop=True)
                    df_distilled['foreign_idiom'] = notebook.foreign_idiom
                    df_distilled['mother_idiom'] = notebook.mother_idiom
                    
                    sentencelabel_distilled_list = []
                    for sl, dist_update_dict in zip(pagesection_group.sentencelabels, 
                                                    list(df_distilled.T.to_dict().values())):
                        sl.translation = dist_update_dict['translated_sentences']
                        sl.memorized = dist_update_dict['remembered']
                        sentencelabel_distilled_list.append(sl)

                    ###############################################################
                    # DISTILLATION PAGESECTION - BODY REQUEST
                    ###############################################################
                    request = {
                        'resource': '/pagesection/distillation/depth',
                        'pagesection_notebook': notebook.to_dict_with_prefix(),
                        'pagesection_id_': pagesection_group.id,
                        'pagesection_page_number': pagesection_group.page_number,
                        'pagesection_group': pagesection_group.group,
                        'pagesection_created_at': selected_day,
                        'pagesection_distillation_at': pagesection_group.distillation_at,
                        'pagesection_distillation_actual': selected_day,
                        'pagesection_sentencelabels':[sl.to_dict_with_prefix() for sl in sentencelabel_distilled_list],            
                    }
                    ############################################################
                    # FrontController
                    ############################################################
                    resp = controller(request=request)
                    messages = resp.get('messages')
                    entities = resp.get('entities')

                    ############################################################
                    # FeedBack
                    ############################################################
                    if 'error' in messages:
                        st.session_state['retry_df_distilled'] = df_distilled
                        st.session_state['flag_error_msg'] = "\n  - ".join(messages["error"])
                    
                    elif entities:
                        pagesection_after_group = entities[-1]
                        notebook.pagesection_list.append(pagesection_after_group)

                    if 'info' in messages:
                        st.session_state['flag_info_msg'] = "\n  - ".join(messages["info"])

                    if 'warning' in messages:
                        st.session_state['flag_warning_msg'] = "\n  - ".join(messages["warning"])

                    if 'success' in messages:
                        messages['success'].append(f'{pagesection_after_group} was distilled successfully!')
                        st.session_state['flag_success_msg'] = "\n  - ".join(messages["success"])
                    ############################################################
                    ############################################################

                    st.rerun()

        else:
            st.warning('⚠️There is no a list of expressions '
                        'in "Group A" to distill on the selected day!')

    else:
        st.warning('⚠️Attention! There are no notebooks registred!')
        st.markdown('[Create a Notebook](Add%20Notebook)')

    # ---- SIDEBAR ----
    st.sidebar.divider()
    st.session_state.authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")
    st.sidebar.divider()
else:
    st.warning("Please access **[Home page](/)** and enter your username and password.")
