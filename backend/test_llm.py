import asyncio
import logging
import sys

from app.llm_generator import generate_match_problems

logging.basicConfig(level=logging.DEBUG, stream=sys.stdout)

async def main():
    print("Generating...")
    problems = generate_match_problems("Python", "Easy", count=1)
    if problems:
        print("Success!", len(problems))
    else:
        print("Failed to generate problems.")

if __name__ == "__main__":
    asyncio.run(main())
