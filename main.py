import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)

def parse_input(text):
    groups = []
    entries = [e.strip() for e in text.split('@') if e.strip()]
    group_id = 1

    for entry in entries:
        if "into" not in entry:
            continue
        parts = entry.split("into")
        nums_raw, amts_raw = parts[0].strip(), parts[1].strip()

        is_cancel = '-' in nums_raw

        nums = [int(n.strip()) for n in nums_raw.replace('-', '').replace('/', ',').split(',') if n.strip().isdigit()]
        amts = [int(a.strip()) for a in amts_raw.replace('/', ',').split(',') if a.strip().isdigit()]

        if is_cancel:
            for num in nums:
                for group in groups:
                    if num in group["numbers"]:
                        group["numbers"].remove(num)
        else:
            if len(amts) == 1:
                groups.append({"id": group_id, "numbers": nums, "amount": amts[0]})
                group_id += 1
            elif len(amts) == len(nums):
                for i in range(len(nums)):
                    groups.append({"id": group_id, "numbers": [nums[i]], "amount": amts[i]})
                    group_id += 1

    number_amount_map = {}
    total = 0

    for group in groups:
        for num in group["numbers"]:
            if num not in number_amount_map:
                number_amount_map[num] = 0
            number_amount_map[num] += group["amount"]
            total += group["amount"]

    amount_groups = {}
    for num, amt in number_amount_map.items():
        if amt not in amount_groups:
            amount_groups[amt] = []
        amount_groups[amt].append(num)

    summary_lines = []
    for amt in sorted(amount_groups.keys(), reverse=True):
        nums = sorted(amount_groups[amt])
        summary_lines.append(f"{', '.join(map(str, nums))} into ₹{amt}")

    result = "Groups:\n" + "\n".join(summary_lines) + f"\n\nOverall Total = ₹{total}"
    return result

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Deep Brothers Bot!\nSend input like: 1,2 into 50 @ 3 into 20"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    result = parse_input(user_input)
    await update.message.reply_text(result)

def main():
    TOKEN = os.getenv("7793916759:AAEmuOs2VemL0a7_Tby7iuP5t75jpkmgqwk")
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == "__main__":
    main()
