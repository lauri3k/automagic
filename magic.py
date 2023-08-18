import os
import json
import logging
import shutil
from datetime import datetime, timedelta
from traitlets.config import get_config

from nbgrader.apps import NbGraderAPI
from nbgrader.utils import parse_utc

GRACE_PERIOD = int(os.environ.get("GRACE_PERIOD", 15))
CHECKPOINT_PATH = "/home/jovyan/.ipynb_checkpoints"
CONFIG_PATH = "/etc/jupyter/nbgrader_config.py"

c = get_config()

log = logging.getLogger(__name__)
hdlr = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
hdlr.setFormatter(formatter)
log.addHandler(hdlr)
log.setLevel(logging.INFO)

if os.path.exists(CHECKPOINT_PATH):
    shutil.rmtree(CHECKPOINT_PATH)

if os.path.isfile(CONFIG_PATH):
    exec(open(CONFIG_PATH, encoding="utf-8").read())

if os.environ.get("RELEASE_NAME"):
    fhdlr = logging.FileHandler(
        f"./courses/{os.environ.get('RELEASE_NAME')}/autograde.log", "a"
    )
    fhdlr.setFormatter(formatter)
    log.addHandler(fhdlr)

    user_config_path = f"./courses/{os.environ.get('RELEASE_NAME')}/nbgrader_config.py"
    if os.path.isfile(user_config_path):
        exec(open(user_config_path, encoding="utf-8").read())

log.info("Starting autograding.")

api = NbGraderAPI(config=c)

released = api.get_released_assignments()
all_assignments = api.get_assignments()
assignments = [x for x in all_assignments if x.get("name") in released]

for assignment in assignments:
    # print(json.dumps(assignment, indent=2))
    name = assignment.get("name")
    due_date = assignment.get("duedate")
    if due_date:
        if parse_utc(due_date) < datetime.utcnow() - timedelta(minutes=GRACE_PERIOD):
            log.info(f"Skipping assignment '{name}' as it is past due date.")
            continue

    log.info(f"Collecting submissions for assignment '{name}'.")
    res_collect = api.collect(name)
    if res_collect.get("success") is not True:
        log.error(json.dumps(res_collect, indent=2))

    if assignment["num_submissions"] > 0:
        log.info(f"Autograding new submissions for assignment '{name}'.")
        students = api.get_submitted_students(name)
        for student in students:
            # if due_date:
            #    submission = api.get_submission(name, student)
            #    ts = submission.get("timestamp")
            #
            #     if ts and parse_utc(due_date) < parse_utc(ts):
            #         print(f"Skipping '{student}' as submission is past due.")
            #         continue
            res_autograde = api.autograde(name, student, force=False)
            # print(json.dumps(res_autograde, indent=2))
            autograde_log = res_autograde.get("log")
            if (
                autograde_log
                and isinstance(autograde_log, str)
                and not "Skipping existing assignment" in autograde_log
            ):
                log.info(f"Autograded submission for student '{student}'.")
            if res_autograde.get("success") is not True:
                log.error(json.dumps(res_autograde, indent=2))
        log.info(f"Generating feedback for assignment '{name}'.")
        res_generate = api.generate_feedback(name, force=False)
        if res_generate.get("success") is not True:
            log.error(json.dumps(res_generate, indent=2))
        log.info(f"Releasing feedback for assignment '{name}'.")
        res_release = api.release_feedback(name)
        if res_release.get("success") is not True:
            log.error(json.dumps(res_release, indent=2))

log.info("Autograding finished.")
