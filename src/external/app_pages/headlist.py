import contextlib
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
from src.core.pagesection import Group

st.set_page_config(layout="wide")


placeholder_container_msg = st.container()
controller = Controller()

# Either this or add_indentation() MUST be called on each page in your
# app to add indendation in the sidebar
add_page_title(layout="wide")  # Optional method to add title and icon to current page

config_file = Path(__file__).parent / "config.yaml"
with config_file.open("rb") as file:
    config = yaml.load(file, Loader=SafeLoader)

credentials = {"usernames": {}}
config["credentials"] = credentials

authenticator = stauth.Authenticate(
    config[
        "credentials"
    ],  # credentials: Dict['usernames', Dict['<alias>', Dict['email | name | password', str]]]
    config["cookie"]["name"],  # cookie: str
    config["cookie"]["key"],  # cookie: str
    config["cookie"]["expiry_days"],  # cookie: str
    config["preauthorized"],  # preauthorized: List[str]
)

st.session_state["username"] = st.session_state["username"]

if st.session_state.username:    
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

    if "error" in messages:
        placeholder_container_msg.error("\n  - ".join(messages["error"]), icon="🚨")
    if "info" in messages:
        placeholder_container_msg.info("\n  - ".join(messages["info"]), icon="ℹ️")
    if "warning" in messages:
        placeholder_container_msg.warning("\n  - ".join(messages["warning"]), icon='⚠️')

    if "success" in messages:
        placeholder_container_msg.success("\n  - ".join(messages["success"]), icon="✅")

    if notebook_list:
        selected_notebook = st.sidebar.selectbox("**NOTEBOOK:**", notebook_dict.keys())

        notebook: Notebook = notebook_dict.get(selected_notebook)
        #############################################################
        # REQUEST PAGESECTION FIND BY FIELD CLEAN
        #############################################################
        request = {
            'resource': '/pagesection/find_by_field_clean',
            'pagesection_notebook': notebook.to_dict_with_prefix(),
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

        new_data_add = []

        if selected_pagesection_day is None:
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
                placeholder_container_msg.info(
                    f"{len(sentence_list)} sentences were added to table bellow and are free to compose a new headlist.",
                    icon="ℹ️",
                )

            if "info" in messages:
                placeholder_container_msg.info("\n  - ".join(messages["info"]), icon="ℹ️")
            if "warning" in messages:
                placeholder_container_msg.warning(
                    "\n  - ".join(messages["warning"]), icon='⚠️'
                )
            if "success" in messages:
                placeholder_container_msg.success(
                    "\n  - ".join(messages["success"]), icon="✅"
                )
            #############################################################

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

        df_edit = pd.DataFrame(new_data_add)

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

        st.markdown("**Add new HeadList**")

        placeholder_sentences_sheet = st.empty()
        placehold_btn_insert = st.empty()
        placehold_page_exists = st.empty()

        df_result = placeholder_sentences_sheet.data_editor(
            df_edit,
            column_config=column_configuration_data,
            num_rows="fixed",
            hide_index=True,
            use_container_width=True,
        )

        df_result["foreign_idiom"] = notebook.foreign_idiom
        df_result["mother_idiom"] = notebook.mother_idiom
        df_result["created_at"] = selected_day

        if selected_pagesection_day is not None:
            placeholder_sentences_sheet.warning(
                f"⚠️There is already a page for the group "
                f"{selected_pagesection_day.group.value} "
                f"and selected day ({selected_pagesection_day.created_at})."
            )

        if placehold_btn_insert.button(
            "INSERT NEW LIST",
            type="primary",
            disabled=False if selected_pagesection_day is None else True,
            use_container_width=True,
        ):

            sentencelabel_dict_list = []
            for sentencetranslation_dict in list(df_result.T.to_dict().values()):
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
            # INSERT PAGESECTION
            ###############################################################
            request = {
                "resource": "/pagesection/registry",
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
                for msg in messages["error"]:
                    placeholder_container_msg.error(msg, icon="🚨")

                st.toast("Something went wrong!")
            elif entities:
                notebook.pagesection_list.extend(entities)
                placeholder_sentences_sheet.success(
                    f"{entities[-1]} was inserted successfully!"
                )
                placeholder_container_msg.success(
                    f"{entities[-1]} was inserted successfully!"
                )
                placehold_btn_insert.empty()
                st.toast("Page section was inserted successfully.")

            if "info" in messages:
                placeholder_container_msg.info("\n  - ".join(messages["info"]), icon="ℹ️")
            if "warning" in messages:
                placeholder_container_msg.warning(
                    "\n  - ".join(messages["warning"]), icon='⚠️'
                )
            if "success" in messages:
                placeholder_container_msg.success(
                    "\n  - ".join(messages["success"]), icon="✅"
                )
            ###############################################################

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

            columns = [
                "created_at",
                "id",
                "page",
                "group",
                "distillation_at",
                "distillation_actual",
                "notebook_name",
            ]

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
    authenticator.logout(f"Logout | {st.session_state.username}", "sidebar")
else:
    st.warning("Please access **[main page](/)** and enter your username and password.")
