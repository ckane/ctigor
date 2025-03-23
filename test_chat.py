import asyncio
from ctiagent import CTIgor

async def main():
    ctigor = CTIgor()

    # Loop forever while the user has more input
    while True:
        try:
            # Get input from the user, display a prompt to indicate waiting on user input
            user_prompt = input('CTIgor> ')

            # If user says 'quit' then exit
            if user_prompt.lower() in ['quit', 'exit', 'bye']:
                raise EOFError

            # Send the user's prompt to the LLM and wait for the response
            response = await ctigor.prompt(user_prompt)

            # Display response on console
            print(f"=======\n{response}\n=======")
        except EOFError:
            # On EOF, exit the program gracefully
            print("Thank you, bye!")
            break

if __name__ == "__main__":
    asyncio.run(main())
