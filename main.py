# Starting of the program
############## ! Imports ##############
# ? Selenium --> For interacting with the web browser
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    InvalidSessionIdException,
    WebDriverException,
)

# ? Time --> For pausing the program
from time import sleep

# ? Questionary --> For beautiful command line prompts
from questionary import Style, select, text

# ? OS --> For clearing the screen
from os import system, name as OSNAME

# ? re --> For extracting meeting ID from link
import re

# ? Rich --> For a box and loading bar
from rich import print
from rich.console import Console

console = Console()
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    Progress,
    TextColumn,
)


############## ! Functions ##############
# * Initializing selenium with Chrome settings
def setSelenium():
    global allNames, chromeOptions
    chromeOptions = ChromeOptions()
    chromeOptions.add_experimental_option("detach", True)
    chromeOptions.add_argument("--use-fake-ui-for-media-stream")
    prefs = {"profile.managed_default_content_settings.images": 2}
    chromeOptions.add_experimental_option("prefs", prefs)
    # ? Reading all the names from 'names.txt' (with proper file handling)
    with open("names.txt", "r") as f:
        allNames = [name.strip() for name in f.read().split("\n") if name.strip()]


# * Extract meeting ID and password from a Zoom link
def parseLinkToIdPass(link):
    """Extract meeting ID and password from a Zoom URL.
    Example: https://us06web.zoom.us/j/84981941628?pwd=tze2BLZ... 
    Returns (meeting_id, password) or (None, None) if parsing fails.
    """
    meeting_id = None
    password = None

    # Extract meeting ID from /j/DIGITS pattern
    id_match = re.search(r'/j/(\d+)', link)
    if id_match:
        meeting_id = id_match.group(1)

    # Extract password from pwd= parameter
    pwd_match = re.search(r'[?&]pwd=([^&#]+)', link)
    if pwd_match:
        password = pwd_match.group(1)

    return meeting_id, password


# * Check if the page shows an authentication-required message
def checkForAuthWall(driver, timeout=5):
    """Check if Zoom is showing a 'Sign in to join' authentication wall.
    Returns True if auth is required, False otherwise.
    """
    try:
        page_source = driver.page_source.lower()
        auth_indicators = [
            "sign in to join",
            "host requires authentication",
            "sign in with a commercial zoom account",
            "pwa_signin",
        ]
        for indicator in auth_indicators:
            if indicator in page_source:
                return True
    except Exception:
        pass
    return False


# * Join a single participant — returns True on success, False on failure
def joinOneParticipant(name, meeting_id, password, method="idpass"):
    """Open a Chrome window and join the meeting as the given name.
    method: 'idpass' uses the /wc/ direct URL, 'link' uses the full link.
    """
    driver = None
    try:
        driver = webdriver.Chrome(options=chromeOptions)

        if method == "link":
            # ? Use the link directly, but construct the /wc/ URL to skip landing page
            url = f"https://app.zoom.us/wc/{meeting_id}/join?pwd={password}&from=join" if password else f"https://app.zoom.us/wc/{meeting_id}/join?from=join"
            driver.get(url)
        else:
            # ? ID/Pass method — go to Zoom web client directly
            driver.get(f"https://zoom.us/wc/{meeting_id}/join?from=join")

        sleep(3)

        # ? Check for authentication wall BEFORE trying to find elements
        if checkForAuthWall(driver):
            console.print(
                f"[bold red]✗[/bold red] [red]Meeting requires authentication "
                f"(host has 'Only authenticated users can join' enabled). "
                f"Cannot join without signing in.[/red]"
            )
            driver.quit()
            return False, "AUTH_REQUIRED"

        # ? Wait for iframe to load, then switch into it
        try:
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            driver.switch_to.frame(driver.find_element(By.TAG_NAME, "iframe"))
        except TimeoutException:
            # ? Maybe no iframe — check if auth wall appeared after redirect
            if checkForAuthWall(driver):
                console.print(
                    f"[bold red]✗[/bold red] [red]Meeting requires sign-in authentication. "
                    f"The host has 'Only authenticated users can join' enabled.[/red]"
                )
                driver.quit()
                return False, "AUTH_REQUIRED"
            console.print(f"[yellow]⚠ Could not find meeting iframe for {name}, skipping...[/yellow]")
            driver.quit()
            return False, "NO_IFRAME"

        # ? Enter password (if field exists — some meetings don't need this via URL)
        if method == "idpass":
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "input-for-pwd"))
                )
                pwd = driver.find_element(By.ID, "input-for-pwd")
                pwd.clear()
                pwd.send_keys(password)
            except TimeoutException:
                pass  # Password might already be in the URL

        # ? Enter name — try multiple selectors
        name_entered = False
        for selector_type, selector_value in [
            (By.ID, "input-for-name"),
            (By.CLASS_NAME, "preview-meeting-info-field-input"),
            (By.CSS_SELECTOR, "input[placeholder*='name' i]"),
        ]:
            try:
                user = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((selector_type, selector_value))
                )
                user.clear()
                user.send_keys(name)
                name_entered = True
                break
            except (TimeoutException, NoSuchElementException):
                continue

        if not name_entered:
            console.print(f"[yellow]⚠ Could not find name input for {name}, skipping...[/yellow]")
            driver.quit()
            return False, "NO_NAME_INPUT"

        # ? Mute audio
        try:
            audioButton = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "preview-audio-control-button"))
            )
            audioButton.click()
            sleep(0.1)
            audioButton2 = driver.find_element(By.ID, "preview-audio-control-button")
            audioButton2.click()
        except Exception:
            pass  # Audio controls may not be present

        # ? Click Join
        user.send_keys(Keys.RETURN)
        console.print(f"[bold green]✓[/bold green] [green]Joined as {name}[/green]")
        return True, "OK"

    except InvalidSessionIdException:
        console.print(f"[yellow]⚠ Browser session crashed for {name}, skipping...[/yellow]")
        return False, "SESSION_CRASH"
    except WebDriverException as e:
        console.print(f"[yellow]⚠ Browser error for {name}: {str(e)[:80]}...[/yellow]")
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        return False, "DRIVER_ERROR"
    except Exception as e:
        console.print(f"[red]✗ Unexpected error for {name}: {str(e)[:80]}[/red]")
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        return False, "UNKNOWN_ERROR"


# * Function if user selected ID and Password method
def idPass(id=None, password=None, test=False):
    # ? If ID is not provided
    if id is None:
        id = text("Enter Zoom Meeting ID:", style=minimalStyle).ask().replace(' ', '')
    else:
        id = str(id).replace(" ", "")

    # ? If password is not provided
    if password is None:
        password = text("Enter Zoom Meeting Password:", style=minimalStyle).ask()

    names_to_join = [allNames[0]] if test else allNames
    if test:
        console.print(f"[cyan]🧪 Test mode: joining with only 1 participant ({allNames[0]})[/cyan]")

    console.print(f"[cyan]Joining meeting {id} with {len(names_to_join)} participant(s)...[/cyan]\n")

    for i, name in enumerate(names_to_join, 1):
        console.print(f"[dim]({i}/{len(names_to_join)})[/dim] Joining as [bold]{name}[/bold]...")
        success, reason = joinOneParticipant(name, id, password, method="idpass")
        if reason == "AUTH_REQUIRED":
            console.print("\n[bold red]Aborting — this meeting requires Zoom sign-in.[/bold red]")
            console.print("[dim]Ask the host to disable 'Only authenticated users can join' in meeting settings.[/dim]")
            break
        sleep(1)  # Small delay between joins to avoid rate limiting


# * Function if user selected link method
def link(link=None, test=False):
    # ? If link is not provided
    if link is None:
        link = text("Enter Zoom Meeting Link:", style=minimalStyle).ask()

    # ? Parse the link to extract meeting ID and password
    meeting_id, password = parseLinkToIdPass(link)
    if meeting_id is None:
        console.print("[bold red]Error: Could not extract meeting ID from the link.[/bold red]")
        console.print(f"[dim]Link provided: {link}[/dim]")
        return

    names_to_join = [allNames[0]] if test else allNames
    if test:
        console.print(f"[cyan]🧪 Test mode: joining with only 1 participant ({allNames[0]})[/cyan]")

    console.print(f"[cyan]Joining meeting {meeting_id} with {len(names_to_join)} participant(s)...[/cyan]\n")

    for i, name in enumerate(names_to_join, 1):
        console.print(f"[dim]({i}/{len(names_to_join)})[/dim] Joining as [bold]{name}[/bold]...")
        success, reason = joinOneParticipant(name, meeting_id, password, method="link")
        if reason == "AUTH_REQUIRED":
            console.print("\n[bold red]Aborting — this meeting requires Zoom sign-in.[/bold red]")
            console.print("[dim]Ask the host to disable 'Only authenticated users can join' in meeting settings.[/dim]")
            break
        sleep(1)  # Small delay between joins


# * Loading Bar
def StatBar(time: float, desc: str):
    progress_bar = Progress(
        TextColumn(f"{desc} "),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
    )
    with progress_bar as p:
        for i in p.track(range(100), description=desc):
            sleep(time / 100)
    sleep(0.5)


############## ! Printing Options ##############
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="ZoomBulkJoiner — Join Zoom meetings with multiple participants",
        epilog="Examples:\n"
               "  python main.py --mode link --link \"https://zoom.us/j/123?pwd=abc\"\n"
               "  python main.py --mode idpass --id 84981941628 --password 4321\n"
               "  python main.py --mode link --link \"https://zoom.us/j/123?pwd=abc\" --test\n"
               "  python main.py   (interactive mode)\n",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--mode", choices=["link", "idpass"], default=None,
                        help="Join method: 'link' or 'idpass'. If omitted, interactive menu is shown.")
    parser.add_argument("--link", type=str, default=None,
                        help="Zoom meeting link (used with --mode link)")
    parser.add_argument("--id", type=str, default=None,
                        help="Zoom meeting ID (used with --mode idpass)")
    parser.add_argument("--password", type=str, default=None,
                        help="Zoom meeting passcode (used with --mode idpass)")
    parser.add_argument("--test", action="store_true", default=False,
                        help="Test mode: join with only the first name to verify everything works")
    args = parser.parse_args()

    setSelenium()
    system("clear" if OSNAME == 'posix' else "cls")
    StatBar(2, desc="[cyan]Loading Zoom Bulk Joiner")
    system("clear" if OSNAME == 'posix' else "cls")
    console.print(
        Panel.fit("[bold italic #77DDD4]Zoom Bulk Joiner", padding=(0, 22))
    )
    minimalStyle = Style(
        [
            ("answer", "fg:#FFFFFF italic"),  # ? White
            ("question", "fg:#FFFFFF bold"),  # ? White
            ("pointer", "fg:#00FFFF bold"),  # ? Cyan
            ("highlighted", "fg:#FFFFFF"),  # ? White
            ("selected", "fg:#A9A9A9"),  # ? Grey
            ("qmark", "fg:#77DD77"),  # ? Green
        ]
    )

    # ? CLI mode — skip interactive menu
    if args.mode == "link":
        if args.link is None:
            parser.error("--link is required when using --mode link")
        link(link=args.link, test=args.test)
    elif args.mode == "idpass":
        if args.id is None or args.password is None:
            parser.error("--id and --password are required when using --mode idpass")
        idPass(id=args.id, password=args.password, test=args.test)
    else:
        # ? Interactive mode — show menu
        userSelect = select(
            "Choose a way to join meetings: ", ["ID/Pass", "Link"], style=minimalStyle
        ).ask()
        sleep(0.5)
        system("clear" if OSNAME == 'posix' else "cls")
        if userSelect == "ID/Pass":
            idPass(test=args.test)
        elif userSelect == "Link":
            link(test=args.test)
        else:
            print("Unknown error, please restart the program")
