import json
from pyrogram import Client, filters
import os
from subprocess import Popen, PIPE

# Load and Save JSON Data
def load_data():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            return json.load(f)
    else:
        return {"users": []}

def save_data(data):
    with open('users.json', 'w') as f:
        json.dump(data, f, indent=4)

async def get_username(client, user_id):
    try:
        user = await client.get_chat(user_id)
        return f"@{user.username}" if user.username else user.first_name
    except Exception:
        return "Unknown"

async def find_or_create_user(user_id, inviter_id=None):
    data = load_data()
    user = next((u for u in data['users'] if u['userId'] == user_id), None)

    if user:
        return user
    else:
        new_user = {'userId': user_id, 'inviterId': inviter_id}
        data['users'].append(new_user)
        save_data(data)
        return new_user

# Replace with your API credentials
AppToken = '8055664535:AAHvjkIG7yFPywrB1ytYGa31EzyKBtSUfK8'
api_id = 29400566
api_hash = "8fd30dc496aea7c14cf675f59b74ec6f"

app = Client("matrix_ai_bot", api_id=api_id, api_hash=api_hash, bot_token=AppToken)

MATRIX_START_TEXT = """
Want to know how cool your Telegram presence is? 
Check your profile rating and unlock awesome rewards with $MTRX Matrix AI!

Time to vibe ✨ and step into the world of Web3.
$MTRX is on the way... Ready to explore something new?

Take the first step and see just how you stack up!
"""

@app.on_message(filters.command("start"))
async def start(client, message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    command_args = message.text.split(' ')[1] if len(message.text.split(' ')) > 1 else None

    share_link = f"https://telegram.me/share/url?url=Join%20the%20Matrix%20AI%20journey%20with%20me%21%20...%20{user_id}"

    inline_keyboard = [[
        {"text": "Play Now 🪂", "url": f"https://mtx-ai-bot.vercel.app/?userId={user_id}"},
        {"text": "Join Community 🔥", "url": "https://telegram.me/MatrixAi_Ann"},
        {"text": "Share Link 📤", "url": share_link}
    ]]

    if command_args and command_args.startswith('ref_'):
        inviter_id = command_args.split('ref_')[1]

        # Load data and find inviter
        data = load_data()
        inviter = next((u for u in data['users'] if u['userId'] == inviter_id), None)
        
        if inviter:
            await find_or_create_user(user_id, inviter_id)
            inviter_name = await get_username(client, inviter_id)
            message_text = f"{MATRIX_START_TEXT}\nInvited by: {inviter_name}"

            await client.send_photo(chat_id, "https://i.ibb.co/XDPzBWc/pngtree-virtual-panel-generate-ai-image-15868619.jpg", caption=message_text, reply_markup={"inline_keyboard": inline_keyboard})
            await client.send_message(inviter_id, f"{message.from_user.first_name} joined via your invite link!")
        else:
            await message.reply('Invalid referral link.')
    else:
        user = await find_or_create_user(user_id)
        invited_by = f"Invited by: {await get_username(client, user['inviterId'])}" if user.get('inviterId') else ''
        await client.send_photo(chat_id, "https://i.ibb.co/XDPzBWc/pngtree-virtual-panel-generate-ai-image-15868619.jpg", caption=f"{MATRIX_START_TEXT}\n{invited_by}", reply_markup={"inline_keyboard": inline_keyboard})

@app.on_message(filters.command("referrals"))
async def referrals(client, message):
    referral_link = f"https://telegram.me/MTRXAi_Bot?start=ref_{message.from_user.id}"
    await message.reply(f"Here is your referral link: {referral_link}")

@app.on_message(filters.command("myinvites"))
async def myinvites(client, message):
    data = load_data()
    invites = [u for u in data['users'] if u.get('inviterId') == message.from_user.id]
    
    if invites:
        invites_list = "\n".join([f"User ID: {user['userId']}" for user in invites])
        await message.reply(f"Your invites:\n{invites_list}")
    else:
        await message.reply('You have no invites.')

@app.on_message(filters.command("eval"))
async def eval_code(client, message):
    command = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else None

    if not command:
        await message.reply('Please provide code to execute!')
        return

    try:
        result = eval(command)
        await message.reply(f"<b>EVAL :</b> <pre>{command}</pre>\n\n<b>OUTPUT :</b>\n<pre>{result}</pre>", parse_mode='html')
    except Exception as e:
        await message.reply(f"Error:\n`{str(e)}`")

@app.on_message(filters.command("exec"))
async def exec_command(client, message):
    command = message.text.split(' ', 1)[1] if len(message.text.split()) > 1 else None

    if not command:
        await message.reply('No input found!')
        return

    processing_message = await message.reply('`Processing...`', parse_mode='Markdown')

    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    stdout, stderr = process.communicate()

    response = ""
    if stderr:
        response += f"<b>STDERR :</b> <code>{stderr.decode().strip()}</code>\n"
    if stdout:
        response += f"<b>STDOUT :</b> <code>{stdout.decode().strip()}</code>\n"
    
    if not response:
        response = 'No output from command'

    await processing_message.edit(response, parse_mode='html')

app.run()
