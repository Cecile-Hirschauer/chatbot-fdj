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
            padding: 0 !important;
            max-width: 450px !important;
            height: 95vh;
            border-radius: 15px;
            border: 1px solid #e0e0e0;
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
            overflow-y: auto;
            overflow-x: hidden;
            margin-top: 1rem;
        }

        .block-container::before {
            content: '🍀 Assistant Loto FDJ';
            display: block;
            background-color: #0052cc;
            color: white;
            font-weight: bold;
            font-size: 1.2rem;
            padding: 15px 20px;
            text-align: left;
        }

        [data-testid="stChatMessageContainer"] {
            padding: 10px 15px;
        }

        [data-testid="stChatInput"] {
            padding: 0 15px 15px 15px;
        }

        [data-testid="stChatInputSubmitButton"] {
            color: #0052cc !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)


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
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Je suis l'assistant Loto. Que souhaites-tu savoir sur les anciens tirages ?"}
    ]

col1, col2 = st.columns([3, 2])
with col2:
    if len(st.session_state.messages) > 1 and st.button("👋 Terminer", use_container_width=True):
        st.session_state.messages = [
            {"role": "assistant", "content": "Merci de ta visite ! N'hésite pas si tu as d'autres questions. 🍀"}
        ]
        st.rerun()

for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🍀"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

if prompt := st.chat_input("Ex: Quel est le numéro chance le plus fréquent en 2024 ?"):
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="🍀"), st.spinner("Analyse en cours..."):
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
