# Built-ins
import re
import traceback
import time

from threading import Thread

# Third-party
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

from tinydb import TinyDB, Query


# HackGPT
from ..settings import (
    SLACK_BOT_TOKEN,
    SLACK_APP_TOKEN,
    SLACK_SIGNING_SECRET,
    OPENAI_API_KEY,
    ASSISTANT_ID,
    DB_LOCATION,
)

from ..assistant import Assistant
from ..logger import GlobalLogger

app = App(
    token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
)

handler = SocketModeHandler(app, SLACK_APP_TOKEN)

log = GlobalLogger("Slack App")
db = TinyDB(DB_LOCATION)
ThreadMap = Query()


@app.event("app_mention")
def handle_app_mention(event, say):
    log.debug("Handling app mention.")
    log.audit(f"Event: {event}")

    # Extracting the text from the event and removing the mention to the bot
    prompt = re.sub(r"(?:\s)<@[^, ]*|(?:^)<@[^, ]*", "", event.get("text", ""))

    # Determine the correct thread timestamp
    thread_ts = event.get("thread_ts") if event.get("thread_ts") else event.get("ts")

    tries = 0
    trying = True
    success = False
    while trying:
        tries += 1
        try:
            mappings = db.search(ThreadMap.slack_thread_id == thread_ts)

            if mappings:
                assistant = Assistant(
                    OPENAI_API_KEY,
                    ASSISTANT_ID,
                    thread_id=mappings[0]["openai_thread_id"],
                )
            else:
                assistant = Assistant(OPENAI_API_KEY, ASSISTANT_ID)

                db.insert(
                    {
                        "slack_thread_id": thread_ts,
                        "openai_thread_id": assistant.thread_id,
                        "last_message_time": time.time(),
                    }
                )

            # Send the prompt to the assistant and get a response
            response = assistant.send_message(prompt)

            # Ensure that 'thread_ts' is a string, as required by the Slack API
            say(
                {
                    "text": response,
                    "thread_ts": str(thread_ts),
                    "reply_broadcast": False,
                }
            )

            trying = False
            success = True
            break

        except Exception as e:
            log.error(f"Error: {e}")
            log.error(f"Traceback: {traceback.format_exc()}")

            if tries >= 3:
                trying = False
                break

            log.warning("Retrying...")
            time.sleep(1)


    if not trying and not success:
        say(
            {
                "text": "An error occurred. Please try again later.",
                "thread_ts": str(thread_ts),
                "reply_broadcast": False,
            }
        )


def run():
    log.info("Starting Slack App.")
    handler.start()
