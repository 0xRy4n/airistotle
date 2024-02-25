import re
import time
import requests
from io import BytesIO
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from tinydb import TinyDB, Query
from ..settings import SLACK_BOT_TOKEN, SLACK_APP_TOKEN, SLACK_SIGNING_SECRET, OPENAI_API_KEY, ASSISTANT_ID, DB_LOCATION
from ..assistant import Assistant
from ..logger import GlobalLogger

app = App(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
handler = SocketModeHandler(app, SLACK_APP_TOKEN)
log = GlobalLogger("Slack App")
db = TinyDB(DB_LOCATION)
ThreadMap = Query()

def process_image_links(text, channel_id, thread_ts) -> bool:
    # Regex to capture Markdown image syntax
    markdown_image_regex = r'!\[.*?\]\((.*?)\)'
    markdown_images = re.findall(markdown_image_regex, text)
    posted = False
    for url in markdown_images:
        if is_image_url(url):
            try:
                text = re.sub(r'!\[.*?\]\('+re.escape(url)+r'\)', '', text)
                upload_image_to_slack(url, channel_id, thread_ts, text=text)
                posted = True
            except Exception as e:
                log.error(f"Error processing image URL {url}: {e}")
    return posted

def is_image_url(url):
    try:
        response = requests.head(url, allow_redirects=True, timeout=5)
        return 'image' in response.headers.get('Content-Type', '')
    except requests.RequestException as e:
        log.error(f"Request error for URL {url}: {e}")
        return False

def upload_image_to_slack(url, channel_id, thread_ts, text="Image: "):
    response = requests.get(url, timeout=5)
    image_bytes = BytesIO(response.content)
    upload_response = app.client.files_upload(
        channels=channel_id, 
        file=image_bytes, 
        filename='image.png', 
        thread_ts=thread_ts,
        initial_comment=text
    )
    if upload_response["ok"]:
        return upload_response['file']['permalink']
    else:
        raise Exception("Failed to upload image to Slack")

@app.event("app_mention")
def handle_app_mention(event, say):
    log.debug("Handling app mention.")
    prompt = re.sub(r"(?:\s)<@[^, ]*|(?:^)<@[^, ]*", "", event.get("text", ""))
    thread_ts = event.get("thread_ts") or event.get("ts")
    channel_id = event['channel']

    response = get_response_from_assistant(prompt, thread_ts)
    posted_image = process_image_links(response, channel_id, thread_ts)
    if not posted_image:
        post_message(response, channel_id, thread_ts, say)


@app.event("message")
def handle_message(event, say, context):
    # Filter out messages that are not direct messages
    if event.get("channel_type") == "im":
        log.debug("Handling DM.")
        thread_ts = event.get("ts")  # In DMs, the thread_ts is just the timestamp of the message
        channel_id = event['channel']

        # Direct messages don't require removal of @ mention, so we can use the text directly
        prompt = event.get("text", "")

        response = get_response_from_assistant(prompt, thread_ts)
        posted_image = process_image_links(response, channel_id, thread_ts)
        if not posted_image:
            post_message(response, channel_id, thread_ts, say)


def get_response_from_assistant(prompt, thread_ts):
    mappings = db.search(ThreadMap.slack_thread_id == thread_ts)
    log.debug(f"Found mappings: {mappings}")
    assistant = Assistant(OPENAI_API_KEY, ASSISTANT_ID, thread_id=mappings[0]["openai_thread_id"]) if mappings else Assistant(OPENAI_API_KEY, ASSISTANT_ID)
    if not mappings:
        db.insert({"slack_thread_id": thread_ts, "openai_thread_id": assistant.thread_id, "last_message_time": time.time()})
    return assistant.send_message(prompt)

def post_message(text, channel_id, thread_ts, say_function):
    say_function({"text": text, "channel": channel_id, "thread_ts": str(thread_ts), "reply_broadcast": False})

def run():
    log.info("Starting Slack App.")
    handler.start()
