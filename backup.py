#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script that runs a MongoDB backup job periodically according
to the interval defined by the INTERVAL_NAME environment variable.
"""

import time
import datetime
import subprocess
import functools
import traceback
import os
import schedule
import begin


ENV_BACKUP_INTERVAL = "BACKUP_INTERVAL"
ENV_BACKUP_TIME = "BACKUP_TIME"
TIME_FORMAT = "%H:%M"


def catch_exceptions(job_func):
    @functools.wraps(job_func)
    def wrapper(*args, **kwargs):
        try:
            job_func(*args, **kwargs)
        except Exception:
            print(traceback.format_exc())

    return wrapper


@catch_exceptions
def backup_job():
    print("Executing backup at {}".format(datetime.datetime.now().isoformat()))
    date = datetime.datetime.today().strftime(os.environ["DATE_FORMAT"])
    dbs = os.environ["MONGO_DB"].split(",")
    storage = os.environ["MONGO_BACKUP_STORAGE"]
    for db in dbs:
        path = (
            os.environ["BUCKET"]
            + os.environ["FILE_PREFIX"]
            + db
            + "-"
            + date
            + ".dump.gzip"
        )
        args = {
            "host": os.environ.get("MONGO_HOST"),
            "port": os.environ.get("MONGO_PORT"),
            "user": os.environ.get("MONGO_USERNAME"),
            "pwd": os.environ.get("MONGO_PASSWORD"),
            "db": os.environ.get("MONGO_DB"),
            "path": path,
        }
        if storage == "s3":
            cmd_ = (
                "mongodump -h {host} --port {port} -u {user} -p {pwd} --db {db} "
                + "--gzip --archive --authenticationDatabase admin | "
                + "aws s3 cp - {path}"
            )
        elif storage == "gs":
            cmd_ = (
                "mongodump -h {host} --port {port} -u {user} -p {pwd} --db {db} "
                + "--gzip --archive --authenticationDatabase admin | "
                + "gsutil cp - {path}"
            )
        else:
            raise ValueError("Storage needs to be in ['s3', 'gs']")

        backup_result = subprocess.check_output([cmd_.format(**args)], shell=True)
        print(backup_result)
    print("Backup finished at {}".format(datetime.datetime.now().isoformat()))


@begin.start(auto_convert=True)
def main(test=False):
    print(
        "Starting periodic MongoDB backup at {}".format(
            datetime.datetime.now().isoformat()
        )
    )

    try:
        interval_days = int(os.environ.get(ENV_BACKUP_INTERVAL))
    except Exception:
        raise ValueError("Undefined or invalid var: {}".format(ENV_BACKUP_INTERVAL))

    try:
        backup_time = os.environ.get(ENV_BACKUP_TIME)
        datetime.datetime.strptime(backup_time, TIME_FORMAT)
    except Exception:
        raise ValueError("Undefined or invalid var: {}".format(ENV_BACKUP_TIME))

    print("Executing backups every {} day/s at {}".format(interval_days, backup_time))

    if test:
        backup_job()
    else:
        schedule.every(interval_days).days.at(backup_time).do(backup_job)

        while True:
            schedule.run_pending()
            time.sleep(1)
