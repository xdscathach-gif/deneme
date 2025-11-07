# Quick Start Guide - Telegram Bot

## 🚀 Getting Started in 3 Steps

### 1. Get Your Bot Token
1. Open Telegram and search for [@BotFather](https://t.me/BotFather)
2. Send `/newbot` command
3. Follow the prompts to create your bot
4. Copy the bot token (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Setup and Install
```bash
# Clone the repository
git clone https://github.com/xdscathach-gif/deneme.git
cd deneme

# Install dependencies
pip install -r bot_requirements.txt

# Set your bot token
export BOT_TOKEN='your-bot-token-here'
# Or on Windows: set BOT_TOKEN=your-bot-token-here
```

### 3. Run the Bot
```bash
python test.py
```

That's it! Your bot is now running.

---

## 📝 Essential Commands

### For Users:
- `/start` - Start the bot
- `/help` - Show help menu
- `/language` - Change language

### For Admins:
- `/settings` - Open settings menu
- `/whitelist @username` - Add user to whitelist
- `/blacklist @username` - Add user to blacklist
- `/violations` - View violations
- `/clearviolations @username` - Clear violations

---

## ⚙️ Quick Configuration

### Using .env file (Recommended):
```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your token
# BOT_TOKEN=your-bot-token-here
```

### Settings Menu:
Once bot is running, use `/settings` in your group to configure:
- 🔞 NSFW Detection
- 🛡️ Spam Protection
- 📝 Whitelist Management
- 🚫 Blacklist Management
- ⚠️ Violations Tracking

---

## 🌍 Change Language

1. Send `/language` to the bot
2. Select your preferred language:
   - 🇹🇷 Turkish
   - 🇬🇧 English
   - 🇮🇳 Hindi

---

## 🐛 Troubleshooting

### Bot doesn't respond?
- Check if bot token is set correctly
- Verify bot has proper permissions in the group
- Check if internet connection is working

### "Bot token not set" error?
```bash
# Make sure you've set the environment variable
export BOT_TOKEN='your-actual-token'
```

### Permission errors?
- Make sure bot is an admin in the group
- Check `/settings` commands are run by group admins

---

## 📚 Documentation

- **Detailed Setup**: See `BOT_README.md`
- **Implementation Details**: See `IMPLEMENTATION_SUMMARY.md`
- **Code Reference**: See `test.py` (well documented)

---

## 🆘 Need Help?

1. Check `BOT_README.md` for detailed documentation
2. Check `IMPLEMENTATION_SUMMARY.md` for technical details
3. Review the troubleshooting section above
4. Check bot logs in console for error messages

---

## ✨ Features Overview

- ✅ NSFW Content Detection
- ✅ Spam Protection
- ✅ User Whitelist/Blacklist
- ✅ Violation Tracking
- ✅ Auto-ban System
- ✅ 3 Languages (TR, EN, HI)
- ✅ Fast Response (<0.5s)
- ✅ Optimized Performance

---

**Enjoy your Telegram bot! 🎉**
