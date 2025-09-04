#!/usr/bin/env python3
import json
import sys


checklist = """
Review the changes you have made in this conversation.

Check that you
- did not implement try-except unless specifically given approval
- did not implement logic forks unless specifically given approval
- did not silently fail
- tested your changes
    - if you have made changes since your last change you have to test again
    - if html files are involved you have to use Puppeteer to test

List all the requirements from the user.
Enumerate over all the requirements from the user
- and write down HOW did you fulfil the requirement.

If you did not address anything, stop enumerating the checklist and address it immediately.
"""

input_data = json.load(sys.stdin)
transcript_path = input_data["transcript_path"]
phrase_to_check = "I have addressed everything in the checklist"

import json
with open(transcript_path) as f:
    lines = f.readlines()
    has_edits = False
    for line in lines[::-1]:  # for the last message
        transcript = json.loads(line)
        if transcript['type'] == 'assistant':
            for content in transcript['message']['content']:
                if content['type'] == "tool_use":
                    if content['name'] == "Edit":
                        has_edits = True
                    if content['name'] == "Write":
                        has_edits = True
        if has_edits:
            break
    if has_edits:
        for line in lines[::-1]:  # for the last message
            transcript = json.loads(line)
            if transcript['type'] == 'assistant':
                for content in transcript['message']['content']:
                    if 'text' in content:
                        assistant_message = content['text']
                        if phrase_to_check in assistant_message:
                            sys.exit(0)
                        print(
                            f"Please iterate over ALL items in the checklist. If everything is correct, end your response with '{phrase_to_check}'.",
                            file=sys.stderr
                        )
                        print(
                            "The following is the checklist.",
                            file=sys.stderr
                        )
                        print(
                            checklist,
                            file=sys.stderr
                        )
                        sys.exit(2)

