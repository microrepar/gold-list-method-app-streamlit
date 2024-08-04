import contextlib
import datetime

import pandas as pd
import streamlit as st
from st_pages import add_page_title

from src.adapters import Controller
from src.core.notebook import Notebook
from src.core.pagesection import Group
from src.core.user import User

st.set_page_config(layout="wide")
add_page_title(layout="wide")  # Optional method to add title and icon to current page

placeholder_container_msg = st.container()

if st.session_state.get('username') and st.session_state.get('credentials', {}).get('usernames'):
    
    controller = Controller()
    
    username = st.session_state['username']
    user: User = st.session_state['credentials']['usernames'][username]['user']

    #############################################################
    # REQUEST NOTEBOOK FIND BY FIELD DEPTH
    #############################################################
    request = {
        'resource': '/notebook/find_by_field_depth',
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
        placeholder_container_msg.info('\n  - '.join(messages['info']), icon='ℹ️')
    if 'warning' in messages:
        placeholder_container_msg.warning('\n  - '.join(messages['warning']), icon='⚠️')
    if 'success' in messages:
        placeholder_container_msg.success('\n  - '.join(messages['success']), icon='✅')
    #############################################################
    #############################################################

    notebook_dict = {n.name: n for n in notebook_list}
    if notebook_list:
        selected_notebook = st.sidebar.selectbox("**NOTEBOOK:**", notebook_dict.keys())
        notebook: Notebook = notebook_dict.get(selected_notebook)

        st.subheader(f"{notebook.name.upper()} NOTEBOOK")
        selected_day = st.sidebar.date_input(
            "**LIST OF THE DAY:**", datetime.datetime.now().date(), format="DD/MM/YYYY"
        )

        st.sidebar.markdown("**Groups:**")
        col_group_1, col_group_2, col_group_3, col_group_4 = st.sidebar.columns(4)

        st.sidebar.divider()

        pagesection_dict = {
            p.created_at: p for p in notebook.pagesection_list if p.group == Group.A
        }
        selected_pagesection_day = pagesection_dict.get(selected_day)
        
        non_msg = True
        if st.session_state.get('flag_success_msg'):
            msg_success = st.session_state.pop('flag_success_msg')
            placeholder_container_msg.success(msg_success)
            st.toast("Page section was inserted successfully.")
            non_msg = False

        if st.session_state.get('flag_info_msg'):
            info_msg = st.session_state.pop('flag_info_msg')
            placeholder_container_msg.info(info_msg)
            non_msg = False
            
        if st.session_state.get('flag_warning_msg'):
            warning_msg = st.session_state.pop('flag_warning_msg')
            placeholder_container_msg.warning(warning_msg)
            non_msg = False

        if st.session_state.get('flag_error_msg'):
            error_msg = st.session_state.pop('flag_error_msg')
            placeholder_container_msg.error(error_msg)
            st.toast("Something went wrong!")
            non_msg = False
        
        if non_msg and selected_pagesection_day:
            placeholder_container_msg.info(
                f"ℹ️  There is already a page for the group "
                f"{selected_pagesection_day.group.value} "
                f"and selected day ({selected_pagesection_day.created_at})."
            )

        if non_msg and selected_pagesection_day is None and 'retry_df_result' not in st.session_state:
            #############################################################
            ### FIND SENTENCES BY NP GROUP
            #############################################################
            # FrontController
            request = {
                "resource": "pagesection/get_sentences_by_group",
                "pagesection_group": Group.NEW_PAGE,
                "pagesection_notebook": {"notebook_id_": notebook.id},
            }
            #############################################################
            resp = controller(request=request)
            sentence_list = resp.get("entities")
            messages = resp.get("messages")

            if "error" in messages:
                with placeholder_container_msg.container():
                    for msg in messages["error"]:
                        st.error(msg, icon="🚨")
            elif sentence_list:
                mensagem_info = (f'{len(sentence_list)} sentences were added to table '
                                 'bellow and are free to compose a new headlist.')
                placeholder_container_msg.info(mensagem_info, icon="ℹ️")
            if "info" in messages:
                placeholder_container_msg.info("\n  - ".join(messages["info"]), icon="ℹ️")
            if "warning" in messages:
                placeholder_container_msg.warning("\n  - ".join(messages["warning"]), icon='⚠️')
            if "success" in messages:
                placeholder_container_msg.success("\n  - ".join(messages["success"]), icon="✅")
            #############################################################
        
        new_data_add = []
        new_data_block = []
        for i in range(1, notebook.sentence_list_size + 1):

            sentence_foreign_str = ""
            sentence_mother_str = ""

            with contextlib.suppress(Exception):
                sentence_foreign_str = sentence_list[i - 1].foreign_language
                sentence_mother_str = sentence_list[i - 1].mother_tongue

            new_data_add.append(
                {
                    "foreign_language": sentence_foreign_str,
                    "mother_tongue": sentence_mother_str,
                }
            )

            new_data_block.append(
                {
                    "foreign_language": 'Disabled',
                    "mother_tongue": 'There is already a page for the group A and selected day (2024-07-23).',
                }
            )

        if selected_pagesection_day is None:
            df_edit = pd.DataFrame(new_data_add)
        else:
            df_edit = pd.DataFrame(new_data_block)

        column_configuration_data = {
            "foreign_language": st.column_config.TextColumn(
                "Foreign Language",
                help="The sentece or word that you want to learn",
                required=True,
            ),
            "mother_tongue": st.column_config.TextColumn(
                "Mother Tongue",
                help="translation the sentece or word that you want to learn",
                required=True,
            ),
        }

        if 'retry_df_result' in st.session_state:
            df_edit = st.session_state.get('retry_df_result')

        st.markdown("**Add new HeadList**")

        with st.form('healist_form', clear_on_submit=True, border=False):
            df_result = st.data_editor(
                df_edit,
                column_config=column_configuration_data,
                num_rows="fixed",
                hide_index=True,
                use_container_width=True,
                disabled=False if selected_pagesection_day is None else True,
            )
            
            placehold_btn_insert = st.empty()

        submited =  placehold_btn_insert.form_submit_button(
            "INSERT NEW LIST", type="primary", use_container_width=True,
            disabled=False if selected_pagesection_day is None else True
        )

        if submited:
            if 'retry_df_result' in st.session_state:
                st.session_state.pop('retry_df_result')

            df_copy = df_result.copy().reset_index(drop=True)
            df_copy["foreign_idiom"] = notebook.foreign_idiom
            df_copy["mother_idiom"] = notebook.mother_idiom
            df_copy["created_at"] = selected_day

            sentencelabel_dict_list = []
            for sentencetranslation_dict in list(df_copy.T.to_dict().values()):
                label_dict = {
                    'sentencelabel_sentencetranslation': {
                        "sentencetranslation_foreign_language": sentencetranslation_dict["foreign_language"],
                        "sentencetranslation_mother_tongue": sentencetranslation_dict["mother_tongue"],
                        "sentencetranslation_foreign_idiom": sentencetranslation_dict["foreign_idiom"],
                        "sentencetranslation_mother_idiom": sentencetranslation_dict["mother_idiom"],
                    }
                }
                sentencelabel_dict_list.append(label_dict)
            
            ###############################################################
            # PAGESECTION REGISTRY DEPTH
            ###############################################################
            request = {
                "resource": "/pagesection/registry/depth",
                "pagesection_notebook": notebook.to_dict_with_prefix(),
                "pagesection_group": Group.HEADLIST,
                "pagesection_created_at": selected_day,
                "pagesection_sentencelabels": sentencelabel_dict_list,
            }
            ###############################################################
            # FrontController
            resp = controller(request=request)
            messages = resp.get("messages")
            entities = resp.get("entities")
            ###############################################################
            # FeedBack
            if "error" in messages:
                st.session_state.retry_df_result = df_result                
                st.session_state['flag_error_msg'] = "\n  - ".join(messages["error"])
                
            elif entities:
                notebook.pagesection_list.extend(entities)
                st.session_state['flag_success_msg'] = f"{entities[-1]} was inserted successfully!\n"

            if "success" in messages:
                if st.session_state.get('flag_success_msg'):
                    st.session_state['flag_success_msg'] += "\n  - ".join(messages["success"])
                else:
                    st.session_state['flag_success_msg'] = "\n  - ".join(messages["success"])

            if "info" in messages:
                st.session_state['flag_info_msg'] = "\n  - ".join(messages["info"])
            
            if "warning" in messages:
                st.session_state['flag_warning_msg'] = "\n  - ".join(messages["warning"])
            ###############################################################
            ###############################################################            
            st.rerun()

        qty_group_a = notebook.count_pagesection_by_group(group=Group.A)
        qty_group_b = notebook.count_pagesection_by_group(group=Group.B)
        qty_group_c = notebook.count_pagesection_by_group(group=Group.C)
        qty_group_d = notebook.count_pagesection_by_group(group=Group.D)

        col_group_1.markdown(f"**A:** {qty_group_a:0>3}")
        col_group_2.markdown(f"**B:** {qty_group_b:0>3}")
        col_group_3.markdown(f"**C:** {qty_group_c:0>3}")
        col_group_4.markdown(f"**D:** {qty_group_d:0>3}")

        st.divider()

        if notebook.pagesection_list:
            df = pd.concat(
                [
                    pd.DataFrame(n.data_to_dataframe())
                    for n in notebook.pagesection_list
                    if n.group == Group.A and n.created_at != n.distillation_at
                ],
                ignore_index=True,
            )
            df = df.groupby("created_at").first().reset_index()
            df_result = df.sort_values("created_at", ascending=False).head(5)

            columns = notebook.pagesection_list[-1].get_columns_from_dataframe()

            st.markdown("#### Last 5 Registred HeadLists:")
            st.dataframe(df_result[columns], hide_index=True, use_container_width=True)
            st.markdown(f"Lines total: {df.shape[0]}")
        else:
            st.subheader("HeadLists")
            st.markdown(":orange[Atteption! There are no registred Headlists.]")

    else:
        st.warning("⚠️Attention! There are no notebooks registred!")
        st.markdown("[Create a Notebook](Add%20Notebook)")

    # ---- SIDEBAR ----
    st.session_state.authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")
    
else:
    st.warning("Please access **[Home page](/)** and enter your username and password.")
