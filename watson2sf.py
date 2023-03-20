#!/usr/bin/python3

import csv
import click
import re
import math

from string import Template
from datetime import datetime, timedelta, date


entryTemplate = Template(('[\\"$name\\",\\"$caseNumber\\",\\"$minutes\\",'
                          '\\"$date\\",\\"9:00 AM\\",\\"$note\\"]'))
projectCaseFormat = re.compile(r"^sf-([0-9]{8})$")
tagCaseFormat = re.compile(r"^[0-9]{8}$")
roundingDelta = timedelta(minutes=15)


def round_dt(dt, delta):
    return datetime.min + math.ceil((dt - datetime.min) / delta) * delta


def extractCaseNumber(project, tags):
    caseNumber = None

    if projectCaseFormat.match(project):
        caseNumber = projectCaseFormat.match(project).group(1)
    elif tagCaseFormat.match(tags):
        caseNumber = tags
    else:
        print(f"No valid case number found for {project} or {tags}")
        while not caseNumber:
            caseNumberInput = input("Enter case number: ")
            if tagCaseFormat.match(caseNumberInput):
                caseNumber = caseNumberInput
            else:
                print(f"{caseNumberInput} isn't a valid SalesForce case")

    return caseNumber


def extractMinutesWorked(startTimeStr, stopTimeStr):
    startTime = datetime.strptime(startTimeStr, '%Y-%m-%d %H:%M:%S')
    roundedStart = round_dt(startTime, roundingDelta)
    stopTime = datetime.strptime(stopTimeStr, '%Y-%m-%d %H:%M:%S')
    roundedStop = round_dt(stopTime, roundingDelta)

    minutes = int((roundedStop - roundedStart).total_seconds() / 60)

    return minutes


def extractDate(dateString):
    dateObject = datetime.strptime(dateString, '%Y-%m-%d %H:%M:%S')

    return dateObject.strftime('%-m/%-d/%Y')


def generateSeleniumScript(jsonOutput):
    with open("new-timecards.side", "r") as timecards:
        lines = timecards.readlines()
        filename = f"timecards-{date.today().strftime('%Y-%m-%d')}.side"
    with open(filename, "w") as timecards:
        for line in lines:
            timecards.write(re.sub(r'^#TIMECARDS_JSON#$', jsonOutput, line))
    print(f"New Selenium script can be found here: {filename}")


@click.command()
@click.option('-n', '--name', help='Full SF username')
@click.argument('file', type=click.File('r'))
def cli(name, file):
    if not name:
        name = input("Enter SalesForce display name: ")

    jsonOutput = '"['

    reader = csv.DictReader(file)
    for row in reader:
        caseNumber = extractCaseNumber(row['project'], row['tags'])
        minutes = extractMinutesWorked(row['start'], row['stop'])
        workDate = extractDate(row['start'])
        jsonOutput += entryTemplate.substitute(name=name,
                                               caseNumber=caseNumber,
                                               minutes=minutes,
                                               date=workDate,
                                               note=row['note'])
        jsonOutput += ','

    # Remove comma after last entry
    jsonOutput = jsonOutput.rstrip(',')
    jsonOutput += ']"'

    generateSeleniumScript(jsonOutput)
