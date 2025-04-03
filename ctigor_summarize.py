import asyncio
from argparse import ArgumentParser
from ctiagent import CTIgor, CTIgorBackend
from autogen_agentchat.ui import Console as AgentConsole

class CTIgorReportSummarizer:
    def __init__(self):
        pass

    def argparse():
        ap = ArgumentParser(description="Have the AI agent ummarize a CTI report, and optionally provide interactive analysis of it")
        ap.add_argument('-f', '--filename', required=False, type=str, help="File path on disk to summarize")
        ap.add_argument('-w', '--webpage', required=False, type=str, help="URL of HTML webpage to summarize")
        ap.add_argument('-i', '--interactive', required=False, default=False, action='store_true',
                        help="Provide an interactive prompt for more analysis")
        ap.add_argument('-o', '--ollama', required=False, default=False, action='store_true',
                        help="Use a local Ollama instance instead of the default (Azure OpenAI)")
        return ap.parse_args()

    # A prompt to instruct the LLM to load an already-converted text file of a report from a file on disk
    async def load_file(self):
        return await self.ctigor.prompt(f"Summarize the text file {self.args.filename} for me")

    # A prompt to instruct the LLM to call WebPlugin to fetch + convert the webpage to Markdown for us
    async def load_webpage(self):
        return await self.ctigor.prompt(f"Summarize the webpage {self.args.webpage} for me")

    async def main(self):
        self.args = CTIgorReportSummarizer.argparse()
        if self.args.ollama:
            self.ctigor = CTIgor(backend=CTIgorBackend.OLLAMA_LOCAL)
        else:
            self.ctigor = CTIgor(backend=CTIgorBackend.AZURE_OPENAI)

        # If both -w and -f are specified, the -w takes precedence and the -f will be ignored
        if self.args.webpage:
            response = await self.load_webpage()
            print(f'Summary of {self.args.webpage}')
            print('================================')
            print(f"{response}\n")
        elif self.args.filename:
            response = await self.load_file()
            print(f'Summary of {self.args.filename}')
            print('================================')
            print(f"{response}\n")

        if not self.args.interactive:
            # If -i was not specified, then exit early
            return

        # Loop forever while the user has more input
        while True:
            try:
                # Get input from the user, display a prompt to indicate waiting on user input
                user_prompt = input('CTIgor> ')

                # If user says 'quit' then exit
                if user_prompt.lower() in ['quit', 'exit', 'bye']:
                    raise EOFError

                # Send the user's prompt to the LLM and wait for the response
                response = await self.ctigor.prompt(user_prompt)

                # Display response on console
                print(f"=======\n{response}\n=======")
            except EOFError:
                # On EOF, exit the program gracefully
                print("Thank you, bye!")
                break

if __name__ == "__main__":
    summarizer = CTIgorReportSummarizer()
    asyncio.run(summarizer.main())
