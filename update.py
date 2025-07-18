from dotenv import (
    load_dotenv,
    dotenv_values
)
from logging import (
    ERROR,
    INFO,
    basicConfig,
    error as log_error,
    FileHandler,
    getLogger,
    info as log_info,
    StreamHandler,
)
from os import (
    environ,
    path,
    remove
)
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from subprocess import run as urun
from sys import exit

getLogger("pymongo").setLevel(ERROR)

if path.exists("Zee_Logs.txt"):
    with open(
        "Zee_Logs.txt",
        "r+"
    ) as f:
        f.truncate(0)

if path.exists("rlog.txt"):
    remove("rlog.txt")

basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        FileHandler("Zee_Logs.txt"),
        StreamHandler()
    ],
    level=INFO,
)

load_dotenv(
    "config.env",
    override=True
)

try:
    if bool(environ.get("_____REMOVE_THIS_LINE_____")):
        log_error("The README.md file there to be read! Exiting now!")
        exit(1)
except:
    pass

BOT_TOKEN = environ.get(
    "BOT_TOKEN",
    ""
)
if len(BOT_TOKEN) == 0:
    log_error("BOT_TOKEN variable is missing! Exiting now")
    exit(1)

BOT_ID = BOT_TOKEN.split(
    ":",
    1
)[0]

DATABASE_URL = environ.get(
    "DATABASE_URL",
    ""
)
if len(DATABASE_URL) == 0:
    DATABASE_URL = None

if DATABASE_URL is not None:
    try:
        conn = MongoClient(
            DATABASE_URL,
            server_api=ServerApi("1")
        )
        db = conn.zee
        old_config = db.settings.deployConfig.find_one({"_id": BOT_ID})
        config_dict = db.settings.config.find_one({"_id": BOT_ID})
        if old_config is not None:
            del old_config["_id"]
        if (
            old_config is not None
            and old_config == dict(dotenv_values("config.env"))
            or old_config is None
        ) and config_dict is not None:
            environ["UPSTREAM_REPO"] = config_dict["UPSTREAM_REPO"]
            environ["UPSTREAM_BRANCH"] = config_dict["UPSTREAM_BRANCH"]
        conn.close()
    except Exception as e:
        log_error(f"Database ERROR: {e}")

UPSTREAM_REPO = environ.get(
    "UPSTREAM_REPO",
    ""
)
if len(UPSTREAM_REPO) == 0:
    UPSTREAM_REPO = "https://github.com/Jircksy/Z-Mirror"

UPSTREAM_BRANCH = environ.get(
    "UPSTREAM_BRANCH",
    ""
)
if len(UPSTREAM_BRANCH) == 0:
    UPSTREAM_BRANCH = "main"

if UPSTREAM_REPO is not None:
    if path.exists(".git"):
        urun([
            "rm",
            "-rf",
            ".git"
        ])

    update = urun(
        [
            f"git init -q \
                     && git config --global user.email support@z-mirror.com \
                     && git config --global user.name zee \
                     && git add . \
                     && git commit -sm update -q \
                     && git remote add origin {UPSTREAM_REPO} \
                     && git fetch origin -q \
                     && git reset --hard origin/{UPSTREAM_BRANCH} -q"
        ],
        shell=True,
    )

    if update.returncode == 0:
        log_info("Successfully updated...")
        log_info("Thanks For Using @Z_Mirror")
    else:
        log_error("Error while getting latest updates.")
        log_error("Check if entered UPSTREAM_REPO is valid or not!")

urun(
    [
        "rm",
        "-rf",
        "py_generators",
        "config_sample.env",
        "Dockerfile",
        "LICENSE",
        "README.md",
        "requirements.txt"
    ]
)
