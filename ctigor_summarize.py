import asyncio
import readline
import os
import atexit
from argparse import ArgumentParser
from ctiagent import CTIgor, CTIgorBackend, CTIReport, CTIWebReport, CTIFileReport
from typing import Any


class CTIgorReportSummarizer:
    def __init__(self):
        pass

    def argparse():
        ap = ArgumentParser(
            description="Have the AI agent ummarize a CTI report, and optionally provide interactive analysis of it"
        )
        ap.add_argument(
            "-f",
            "--filename",
            required=False,
            type=str,
            help="File path on disk to summarize",
        )
        ap.add_argument(
            "-w",
            "--webpage",
            required=False,
            type=str,
            help="URL of HTML webpage to summarize",
        )
        ap.add_argument(
            "-i",
            "--interactive",
            required=False,
            default=False,
            action="store_true",
            help="Provide an interactive prompt for more analysis",
        )
        ap.add_argument(
            "-o",
            "--ollama",
            required=False,
            default=False,
            action="store_true",
            help="Use a local Ollama instance instead of the default (Azure OpenAI)",
        )
        ap.add_argument(
            "--disable-memory",
            required=False,
            default=False,
            action="store_true",
            help="Disable the creation of TextCanvasMemory tools",
        )
        return ap.parse_args()

    async def exec_slash_cmd(self, slash_input: str) -> Any:
        command = slash_input.lstrip("/")
        cmdline = command.split(" ")

        if len(cmdline) > 0:
            if cmdline[0].lower() in ["quit", "exit", "bye"]:
                raise EOFError

            return await self.ctigor.exec_cmd(cmd_with_args=cmdline)

    async def main(self):
        self.args = CTIgorReportSummarizer.argparse()

        # Determine the type of report provided (if any) and load it
        report = CTIReport()
        if self.args.webpage:
            report = CTIWebReport(url=self.args.webpage)
        elif self.args.filename:
            report = CTIFileReport(filename=self.args.filename)

        if self.args.ollama:
            self.ctigor = CTIgor(
                backend=CTIgorBackend.OLLAMA_LOCAL,
                report=report,
                built_in_memory=not self.args.disable_memory,
            )
        else:
            self.ctigor = CTIgor(
                backend=CTIgorBackend.AZURE_OPENAI,
                report=report,
                built_in_memory=not self.args.disable_memory,
            )

        await self.ctigor.init_agent()

        # If both -w and -f are specified, the -w takes precedence and the -f will be ignored
        if self.ctigor.get_summary():
            print(f"Summary of {self.ctigor.get_context_entity()}")
            print("================================")
            print(f"{self.ctigor.get_summary()}\n")
            print("================================")

        if not self.args.interactive:
            # If -i was not specified, then exit early
            return

        # Loop forever while the user has more input
        while True:
            try:
                # Get input from the user, display a prompt to indicate waiting on user input.
                # Strip whitespace.
                user_prompt = input("CTIgor> ").strip()

                # Clear response variable
                response = ""
                if len(user_prompt) >= 1 and user_prompt[0] == "/":
                    response = await self.exec_slash_cmd(user_prompt)
                else:
                    # Send the user's prompt to the LLM and wait for the response
                    response = await self.ctigor.prompt(user_prompt)

                # Display response on console
                print(f"{response}\n")
            except EOFError:
                # On EOF, exit the program gracefully
                print("Thank you, bye!")
                break


if __name__ == "__main__":
    ctigor_histfile = os.path.join(os.path.expanduser("~"), ".ctigor_history")

    try:
        readline.read_history_file(ctigor_histfile)
        readline.set_history_length(1000)
    except:
        pass  # If loading histfile fails, just move along

    atexit.register(readline.write_history_file, ctigor_histfile)
    summarizer = CTIgorReportSummarizer()
    asyncio.run(summarizer.main())
