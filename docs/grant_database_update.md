# Grant Database Updater: CLI & Cron Usage

This document explains how to use the Grant AI project's grant database updater via the command line (CLI) and how to schedule automatic updates using cron.

---

## What is CLI?

**CLI** stands for **Command Line Interface**. It allows you to interact with your computer or software by typing commands into a terminal or shell (such as Bash, zsh, or Command Prompt). Many developer tools and scripts are run from the CLI.

---

## What is Cron?

**cron** is a time-based job scheduler in Unix-like operating systems (Linux, macOS). It allows you to schedule scripts or commands to run automatically at specified times and intervals (e.g., daily, weekly, monthly).

A **crontab** is a file that contains a list of cron jobs (scheduled tasks).

---

## Available CLI Commands

The Grant AI project provides several CLI commands for managing the grant database:

### Check Database Statistics
```bash
python -m grant_ai.core.cli database-stats
```
Shows current statistics about the grant database including total grants, breakdown by funder type, and update timestamps.

### Update Database Manually
```bash
python -m grant_ai.core.cli update-database
```
Forces a manual update of the grant database with the latest grants from federal, state, and foundation sources.

### Launch GUI (with auto-update)
```bash
python -m grant_ai.core.cli gui
```
Launches the GUI application and automatically checks for database updates in the background.

---

## Updating the Grant Database via CLI

You can manually update the grant database at any time using the CLI. From your project root directory, run:

```bash
python -m grant_ai.core.cli update-database
```

Or, if you prefer to run the script directly:

```bash
python src/grant_ai/utils/grant_database_manager.py
```

This will download and update the local database with the latest grants for afterschool programs, education, robotics, and arts.

---

## Scheduling Automatic Updates with Cron

To keep your grant database up-to-date automatically, you can schedule the updater to run once a month using cron.

### 1. Open your crontab for editing:

```bash
crontab -e
```

### 2. Add a line like this to run the update at 3:00 AM on the 1st of every month:

```
0 3 1 * * cd /home/kevin/Projects/grant-ai && /home/kevin/Projects/grant-ai/venv/bin/python -m grant_ai.core.cli update-database
```

- Adjust the path to your Python executable and project directory as needed.
- This example assumes you are using a virtual environment at `/home/kevin/Projects/grant-ai/venv/`.

### 3. Save and exit the editor.

Your system will now automatically update the grant database every month.

---

## Automatic Updates on GUI Start

The grant database is automatically checked for updates every time you launch the GUI:

```bash
python -m grant_ai.core.cli gui
```

The system will:
1. Check if the database needs updating (based on 30-day interval)
2. Download new grants in the background if needed
3. Launch the GUI without blocking the interface

---

## Tips
- You can run the updater manually at any time if you want the latest grants immediately.
- Check the logs/output for any errors or status messages.
- You can change the schedule in your crontab to run more or less frequently (see `man 5 crontab` for syntax).
- The database update runs in the background when launching the GUI, so it won't slow down the interface.

---

**For more information:**
- [Wikipedia: Command-line interface](https://en.wikipedia.org/wiki/Command-line_interface)
- [Wikipedia: cron](https://en.wikipedia.org/wiki/Cron)
- [Crontab Guru (schedule helper)](https://crontab.guru/) 