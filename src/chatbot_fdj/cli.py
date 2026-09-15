# INTERNAL / DEMO TOOL — do not expose to end users.
# This CLI intentionally displays the generated SQL query and raw DB results
# to allow inspection of the full pipeline during development and demos.
# The Streamlit app (app.py) is the production interface.

from chatbot_fdj.domain.exceptions import ChatbotDomainError
from chatbot_fdj.domain.orchestrator import ChatbotOrchestrator
from chatbot_fdj.infrastructure.openrouter_adapter import OpenRouterAdapter


def main() -> None:
    """Run the interactive demo CLI.

    Initialises the orchestrator and starts a REPL loop that prints the
    generated SQL, raw DB results, and the final natural language answer for
    each question. Intended for internal development and demos only — the
    Streamlit app is the production interface.
    """
    print("Initialising OpenRouter adapter...")
    try:
        llm = OpenRouterAdapter()
        orchestrator = ChatbotOrchestrator(llm=llm)
    except ValueError as e:
        print(f"Configuration error: {e}")
        return

    print("\n=== FDJ Chatbot — Internal Demo CLI ===")
    print("Ask a question about lottery draws to inspect the generated SQL.")
    print("Type 'quit' to exit.\n")

    chat_history: list[dict[str, str]] = []

    while True:
        try:
            question = input("\nYour question: ")
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
            print(f"[{type(e).__name__}] {e}")
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
