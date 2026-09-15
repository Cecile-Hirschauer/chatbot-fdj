import streamlit as st

from chatbot_fdj.domain.exceptions import ChatbotDomainError
from chatbot_fdj.domain.orchestrator import ChatbotOrchestrator
from chatbot_fdj.infrastructure.openrouter_adapter import OpenRouterAdapter

st.set_page_config(page_title="Chatbot FDJ", page_icon="🍀", layout="centered")

st.markdown(
    """
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
        .block-container {
            padding-top: 1rem;
            padding-bottom: 1rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🍀 Assistant FDJ")
st.markdown("Pose tes questions sur l'historique des tirages du Loto.")


@st.cache_resource
def get_orchestrator() -> ChatbotOrchestrator:
    llm = OpenRouterAdapter()
    return ChatbotOrchestrator(llm=llm)


try:
    orchestrator = get_orchestrator()
except Exception as e:
    st.error(f"Erreur d'initialisation : {e}")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ex: Quel est le numéro chance le plus fréquent en 2024 ?"):
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"), st.spinner("Analyse en cours..."):
            try:
                history_for_llm = [
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]

                _, _, answer = orchestrator.answer_question(
                    question=prompt,
                    history=history_for_llm,
                )

                st.markdown(answer)

                st.session_state.messages.append({"role": "user", "content": prompt})
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.messages = st.session_state.messages[-4:]

            except ChatbotDomainError as e:
                st.error(f"Rejeté par la sécurité ou l'IA : {e}")
            except Exception as e:
                st.error(f"Erreur inattendue : {e}")
