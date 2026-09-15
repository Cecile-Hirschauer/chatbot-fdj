from chatbot_fdj.domain.exceptions import ChatbotDomainError
from chatbot_fdj.domain.orchestrator import ChatbotOrchestrator
from chatbot_fdj.infrastructure.openrouter_adapter import OpenRouterAdapter


def main() -> None:
    print("Initialisation de l'adaptateur OpenRouter...")
    try:
        llm = OpenRouterAdapter()
        orchestrator = ChatbotOrchestrator(llm=llm)
    except ValueError as e:
        print(f"Erreur de configuration : {e}")
        return

    print("\n=== Test du Harnais Applicatif FDJ ===")
    print("Pose une question sur les tirages pour voir le SQL généré.")
    print("Tape 'quit' pour arrêter.\n")

    chat_history: list[dict[str, str]] = []

    while True:
        try:
            question = input("\nTa question : ")
            if question.lower() in ["quit", "exit"]:
                break

            if not question.strip():
                continue

            print("Sending to AI...")
            safe_sql, db_results, answer = orchestrator.answer_question(
                question, history=chat_history
            )
            print(f"\n SQL:\n{safe_sql}")
            print(f"\n Results:\n{db_results}")
            print(f"\n Answer:\n{answer}")

            chat_history.append({"role": "user", "content": question})
            chat_history.append({"role": "assistant", "content": answer})
            chat_history = chat_history[-4:]

        except ChatbotDomainError as e:
            print(f"❌ [{type(e).__name__}] {e}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"⚠️ Erreur inattendue : {e}")

if __name__ == "__main__":
    main()
