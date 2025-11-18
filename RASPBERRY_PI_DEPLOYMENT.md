# Deploying MTG Bot to Raspberry Pi

Complete guide for deploying your MTG Commander bot to a Raspberry Pi (including Home Assistant setups).

## Prerequisites

- Raspberry Pi with Raspbian/Raspberry Pi OS (tested on Pi 3B)
- SSH access to your Pi
- Your Pi connected to the internet
- Your Discord bot token

## Quick Deploy

### 1. SSH into Your Raspberry Pi

```bash
ssh pi@<your-pi-ip-address>
# Default password is usually 'raspberry' if you haven't changed it
```

### 2. Install Dependencies

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install python3 python3-pip git -y
```

### 3. Clone the Repository

```bash
cd /home/pi
git clone https://github.com/ShowmiGG/mtg-bot.git
cd mtg-bot
```

### 4. Install Python Dependencies

```bash
pip3 install -r requirements.txt
```

### 5. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit with your token
nano .env
```

Add your Discord token:
```
DISCORD_TOKEN=your_discord_token_here
COMMAND_PREFIX=!mtg
```

Save: `Ctrl+X`, `Y`, `Enter`

### 6. Test Run

```bash
python3 bot.py
```

You should see:
```
Starting MTG Commander Bot...
Loaded extension: cogs.game
Loaded extension: cogs.cards
Loaded extension: cogs.utils
Connecting to Discord...
Logged in as MTG-Bot (...)
Bot is ready!
```

Press `Ctrl+C` to stop for now.

## Set Up Automatic Startup (Systemd Service)

### 1. Create Systemd Service File

```bash
sudo nano /etc/systemd/system/mtg-bot.service
```

Paste this content:
```ini
[Unit]
Description=MTG Commander Discord Bot
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/mtg-bot
ExecStart=/usr/bin/python3 /home/pi/mtg-bot/bot.py
Restart=always
RestartSec=10
Environment="PYTHONUNBUFFERED=1"

[Install]
WantedBy=multi-user.target
```

Save: `Ctrl+X`, `Y`, `Enter`

### 2. Enable and Start the Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable mtg-bot.service

# Start the service now
sudo systemctl start mtg-bot.service
```

### 3. Check Status

```bash
# Check if running
sudo systemctl status mtg-bot.service

# View logs
sudo journalctl -u mtg-bot.service -f
```

## Managing the Bot

### Start/Stop/Restart

```bash
# Start the bot
sudo systemctl start mtg-bot.service

# Stop the bot
sudo systemctl stop mtg-bot.service

# Restart the bot
sudo systemctl restart mtg-bot.service

# Check status
sudo systemctl status mtg-bot.service
```

### View Logs

```bash
# View real-time logs
sudo journalctl -u mtg-bot.service -f

# View last 50 lines
sudo journalctl -u mtg-bot.service -n 50

# View logs from today
sudo journalctl -u mtg-bot.service --since today
```

## Updating the Bot

When you push changes to GitHub:

```bash
# SSH into Pi
ssh pi@your-pi-ip

# Navigate to bot directory
cd /home/pi/mtg-bot

# Pull latest changes
git pull

# Restart the bot
sudo systemctl restart mtg-bot.service

# Check it started successfully
sudo systemctl status mtg-bot.service
```

## Troubleshooting

### Bot Won't Start

1. **Check logs:**
   ```bash
   sudo journalctl -u mtg-bot.service -n 50
   ```

2. **Check if .env file exists:**
   ```bash
   cat /home/pi/mtg-bot/.env
   ```

3. **Test manually:**
   ```bash
   cd /home/pi/mtg-bot
   python3 bot.py
   ```

### Bot Keeps Restarting

- Check Discord token is valid
- Ensure all dependencies are installed
- Check for Python errors in logs

### Memory Issues (Raspberry Pi 3B)

The Pi 3B has 1GB RAM. If you experience issues:

1. **Monitor memory:**
   ```bash
   free -h
   htop
   ```

2. **Increase swap:**
   ```bash
   sudo dphys-swapfile swapoff
   sudo nano /etc/dphys-swapfile
   # Change CONF_SWAPSIZE=100 to CONF_SWAPSIZE=1024
   sudo dphys-swapfile setup
   sudo dphys-swapfile swapon
   ```

## Home Assistant Integration Notes

If running on the same Pi as Home Assistant:

- The bot runs independently of Home Assistant
- Should not interfere with HA operations
- Monitor system resources with `htop`
- Bot typically uses ~50-100MB RAM

## Performance

**Raspberry Pi 3B Specs:**
- CPU: 1.2GHz quad-core ARM Cortex-A53
- RAM: 1GB
- **Expected Bot Performance:** Excellent for Discord bots

**Resource Usage:**
- RAM: ~50-100MB
- CPU: <5% when idle
- Network: Minimal

## Security

1. **Change default Pi password:**
   ```bash
   passwd
   ```

2. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

3. **Use SSH keys instead of passwords** (optional but recommended)

## Backup

Backup your `.env` file (contains Discord token):
```bash
cp /home/pi/mtg-bot/.env /home/pi/mtg-bot-backup.env
```

## Uninstall

```bash
# Stop and disable service
sudo systemctl stop mtg-bot.service
sudo systemctl disable mtg-bot.service

# Remove service file
sudo rm /etc/systemd/system/mtg-bot.service

# Reload systemd
sudo systemctl daemon-reload

# Remove bot files
rm -rf /home/pi/mtg-bot
```

## Support

- Check logs first: `sudo journalctl -u mtg-bot.service -f`
- Test manually: `python3 bot.py`
- Verify Discord token in `.env` file
- Ensure all dependencies installed: `pip3 install -r requirements.txt`
