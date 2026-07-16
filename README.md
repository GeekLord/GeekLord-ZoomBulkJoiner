<div align="center">

  <a href="https://shobhit.net/"><img src="https://img.shields.io/badge/Website-shobhit.net-blue?style=for-the-badge&logo=google-chrome" alt="Website" /></a> <a href="https://x.com/Shobhit"><img src="https://img.shields.io/badge/Twitter-%40Shobhit-black?style=for-the-badge&logo=x" alt="Twitter" /></a> <a href="https://linkedin.com/in/geeklord/"><img src="https://img.shields.io/badge/LinkedIn-GeekLord-blue?style=for-the-badge&logo=linkedin" alt="LinkedIn" /></a> <a href="https://github.com/GeekLord/"><img src="https://img.shields.io/badge/GitHub-GeekLord-181717?style=for-the-badge&logo=github" alt="GitHub" /></a> <a href="https://g.dev/Shobhit"><img src="https://img.shields.io/badge/Google Dev-Shobhit-blue?style=for-the-badge&logo=google" alt="Google Dev" /></a>

  <img src="https://img.shields.io/badge/Python-informational?style=for-the-badge&logo=python" alt="badge" /> <img src="https://img.shields.io/github/license/GeekLord/GeekLord-ZoomBulkJoiner?style=for-the-badge" alt="badge" /> <img src="https://img.shields.io/github/stars/GeekLord/GeekLord-ZoomBulkJoiner?style=for-the-badge&logo=github" alt="badge" /> <img src="https://img.shields.io/github/forks/GeekLord/GeekLord-ZoomBulkJoiner?style=for-the-badge&logo=github" alt="badge" /> <img src="https://img.shields.io/github/last-commit/GeekLord/GeekLord-ZoomBulkJoiner?style=for-the-badge" alt="badge" />

</div>

# ZoomBulkJoiner 
Multi-Participant Zoom Meeting Script

![image](https://github.com/eXtizi/ZoomBulkJoiner/assets/75202685/0cb71466-9581-4aaf-8d10-6b362521f963)




ZoomBulkJoiner is a Python and Selenium-based script that helps you join a Zoom meeting with multiple instances, using different names. Whether you have a Zoom meeting link or an ID with a passcode, this script automates the join flow for repeated testing or simulations.

- FOR **EDUCATIONAL PURPOSES ONLY**. Please use it at your own risk and follow Zoom's terms of service.

## **Requirements:**

### Python

Have Python3 language installed as the program was written in it.
It can be installed using https://www.python.org/downloads/

- Below are the python libraries used for running the program, you can run either of the code blocks to download all the libraries.
```
pip install selenium questionary rich
```
```
pip install -r requirements.txt
```

### Chrome

Have Chrome browser installed, because the program relies on Chrome drivers.
It can be installed using https://www.google.com/chrome/

## **How It Works**

- The program using the `Selenium` web-driver and Python library for the same, exploits a vulnerability in Zoom's webapp that let's a user join a meeting without needing an account.
- Given the names in the text file, it proceeds to launch an instance of a web-driver and fill the required details to joining the meeting automatically.
- It proceeds to mute audio to prevent an audio loop or unnecessary transfer of microphone audio into the meeting, giving you control over each of the web instances.
- Change names in `names.txt` which will be used in the meeting.
- Example are given in `names.txt`

## **Usage**

### Interactive Mode (menu-based)
```
python main.py
```
You'll be prompted to choose between **ID/Pass** or **Link** method, and then enter the meeting details.

### Command Line Mode (non-interactive)

**Join via Meeting Link:**
```
python main.py --mode link --link "https://us06web.zoom.us/j/84981941628?pwd=YOUR_PASSWORD_HERE"
```

**Join via Meeting ID & Passcode:**
```
python main.py --mode idpass --id 84981941628 --password 4321
```

### CLI Arguments

| Argument     | Required | Description |
|------------|----------|-------------|
| `--mode`     | No       | `link` or `idpass`. If omitted, interactive menu is shown |
| `--link`     | With `--mode link` | The full Zoom meeting URL |
| `--id`       | With `--mode idpass` | The Zoom meeting ID |
| `--password` | With `--mode idpass` | The Zoom meeting passcode |
| `--test`     | No       | Join with only the first name in `names.txt` to verify everything works |

### Help
```
python main.py --help
```

## What's Different?
- Fixed the element locating problem
- Added waiting for page load
- Dismisses confirmation alerts
- Added CLI argument support for non-interactive usage

## TO-DO
- Stoping Incoming Video Audio Feed
- Going Headless is Triggers Cloudflare . Gotta Find a Workaround(Maybe a virtual Browser)
- Cookies Accepting Function
  
### Credits:
https://github.com/AverageBlank/ZoomBomber

```
Note: The program may contain bugs, and only the link-join option has been tested. Please proceed with care and modify the code to suit your needs.
```
