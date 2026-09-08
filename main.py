from __future__ import annotations

import argparse
from pathlib import Path

from study_assistant import StudyAssistant


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="StudyBuddy AI")
    parser.add_argument("--materials", type=str, default="materials", help="Folder containing course text files")
    parser.add_argument("--memory", type=str, default="memory/history.json", help="Location for conversation memory")
    parser.add_argument("--topic", type=str, default="artificial intelligence", help="Topic for plan or quiz generation")
    parser.add_argument("--days", type=int, default=5, help="Number of days in the study plan")
    parser.add_argument("--count", type=int, default=3, help="Number of quiz questions to generate")
    parser.add_argument("--question", type=str, help="Ask a question about course content")
    parser.add_argument("--plan", action="store_true", help="Generate a study plan instead of answering a question")
    parser.add_argument("--quiz", action="store_true", help="Generate quiz questions instead of answering a question")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    materials_dir = Path(args.materials)
    assistant = StudyAssistant(materials_dir=materials_dir, memory_path=args.memory)

    if args.question:
        print(assistant.answer_question(args.question))
    elif args.plan:
        plan = assistant.create_learning_plan(args.topic, days=args.days)
        for item in plan:
            print(item)
    elif args.quiz:
        quiz = assistant.generate_quiz(args.topic, count=args.count)
        for item in quiz:
            print(item["question"])
            print(f"Answer: {item['answer']}\n")
    else:
        print("Welcome to StudyBuddy AI.")
        print("Try --question 'What is machine learning?' or --plan --topic 'data science'.")


if __name__ == "__main__":
    main()
