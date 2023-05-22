configFileContents="""
[watson2sf]
template = '$templatePath'

[user]
name = '$sfname'
"""

templateFileContents="""
{
  "id": "660026eb-3352-46f9-87c4-a61b26a22f03",
  "version": "2.0",
  "name": "new-timecards",
  "url": "https://canonical.lightning.force.com/lightning/o/TimeCard__c/new",
  "tests": [{
    "id": "40afadce-a98b-4e95-8a0f-4f7bb2660f8b",
    "name": "new-timecards",
    "commands": [{
      "id": "7952f694-a4a0-492c-9acc-32eef5087216",
      "comment": "Open SalesForce's \\"New Case Time Card\\" page",
      "command": "",
      "target": "",
      "targets": [],
      "value": ""
    }, {
      "id": "12368614-2c9f-47b2-80b4-d1edd9638ed7",
      "comment": "",
      "command": "open",
      "target": "https://canonical.lightning.force.com/lightning/o/TimeCard__c/new",
      "targets": [],
      "value": ""
    }, {
      "id": "bebc3e61-d982-479d-9b70-c9e929bc79dd",
      "comment": "Load JSON array with timecard arrays",
      "command": "",
      "target": "",
      "targets": [],
      "value": ""
    }, {
      "id": "d85bffa2-8e4b-4a67-b1de-c007803898fd",
      "comment": "",
      "command": "storeJson",
      "target":
#TIMECARDS_JSON#
      ,
      "targets": [],
      "value": "TIMECARDS"
    }, {
      "id": "2f3591c3-0530-462a-be06-837851e792c7",
      "comment": "",
      "command": "store",
      "target": "${TIMECARDS.length}",
      "targets": [],
      "value": "TOTAL"
    }, {
      "id": "c2ce075e-ca17-4850-861a-2c2335d38032",
      "comment": "Loop over the timecard arrays",
      "command": "",
      "target": "",
      "targets": [],
      "value": ""
    }, {
      "id": "a9a17150-a8f5-4e6c-81c0-e8776ff5f658",
      "comment": "",
      "command": "store",
      "target": "0",
      "targets": [],
      "value": "INDEX"
    }, {
      "id": "261c1837-9947-41ac-9b80-e27a4d87b29c",
      "comment": "",
      "command": "forEach",
      "target": "TIMECARDS",
      "targets": [],
      "value": "T"
    }, {
      "id": "e74f86ed-f03f-4002-904a-94d6b1e3beaf",
      "comment": "",
      "command": "store",
      "target": "${T[0]}",
      "targets": [],
      "value": "NAME"
    }, {
      "id": "62a3fdba-8517-4a66-aa2e-f1771edea20e",
      "comment": "",
      "command": "store",
      "target": "${T[1]}",
      "targets": [],
      "value": "CASE"
    }, {
      "id": "29b734d1-380b-4613-a203-3b95c6320d6a",
      "comment": "",
      "command": "store",
      "target": "${T[2]}",
      "targets": [],
      "value": "MINUTES"
    }, {
      "id": "7a62458c-cbaa-47cd-bcd7-ca9c1db3bcb0",
      "comment": "",
      "command": "store",
      "target": "${T[3]}",
      "targets": [],
      "value": "DATE"
    }, {
      "id": "36513f37-8063-422b-a30e-55db134e83c2",
      "comment": "",
      "command": "store",
      "target": "${T[4]}",
      "targets": [],
      "value": "TIME"
    }, {
      "id": "530b09b6-26f4-4a90-accc-38a854404d17",
      "comment": "",
      "command": "store",
      "target": "${T[5]}",
      "targets": [],
      "value": "COMMENT"
    }, {
      "id": "79601648-b748-4973-803c-51e02936228e",
      "comment": "",
      "command": "executeScript",
      "target": "return parseInt(${INDEX})+1",
      "targets": [],
      "value": "INDEX"
    }, {
      "id": "f78d36c3-080f-4d97-9de7-3e6b5cf74fc7",
      "comment": "",
      "command": "echo",
      "target": "Timecard ${INDEX} of ${TOTAL}: ${NAME} worked on SF#${CASE} on ${DATE} at ${TIME} for ${MINUTES} minutes (${COMMENT})",
      "targets": [],
      "value": ""
    }, {
      "id": "f7716eb5-0c18-4d3a-afe2-7fcdad2257a2",
      "comment": "Fields: Minutes, Start Date, Start Time, Work Performed. (only type)",
      "command": "",
      "target": "",
      "targets": [],
      "value": ""
    }, {
      "id": "66f6166b-adca-43bd-8792-fa8c7dc272b4",
      "comment": "",
      "command": "type",
      "target": "xpath=//textarea[@maxlength='255']",
      "targets": [],
      "value": "${COMMENT}"
    }, {
      "id": "fa2d659a-1714-4b21-8f2f-ad3e7fc78dbe",
      "comment": "",
      "command": "type",
      "target": "xpath=//input[@name='TotalMinutesStatic__c']",
      "targets": [],
      "value": "${MINUTES}"
    }, {
      "id": "c87bf6a6-332e-458a-9bb1-ffee6b29a2fb",
      "comment": "",
      "command": "type",
      "target": "xpath=//input[@name='StartTime__c' and not(@role='combobox')]",
      "targets": [],
      "value": "${DATE}"
    }, {
      "id": "6c10a4e8-9c66-40a5-b503-be00c32fc280",
      "comment": "",
      "command": "type",
      "target": "xpath=//input[@name='StartTime__c' and @role='combobox']",
      "targets": [],
      "value": "${TIME}"
    }, {
      "id": "07909d30-79ea-414a-a1db-25b7c27c3fa1",
      "comment": "Field: Time Card Owner (type and select)",
      "command": "",
      "target": "",
      "targets": [],
      "value": ""
    }, {
      "id": "e4827af2-8333-47e2-a0df-ca1ac9381041",
      "comment": "Type the string, pause for suggestions to load, click for suggestions to become visible, wait for right suggestion to become visible, click right suggestion",
      "command": "",
      "target": "",
      "targets": [],
      "value": ""
    }, {
      "id": "e8e6d8ef-c5bb-4720-8ff0-5ee158d7702f",
      "comment": "",
      "command": "type",
      "target": "xpath=//input[@placeholder='Search People...']",
      "targets": [],
      "value": "${NAME}"
    }, {
      "id": "15ab01c1-123e-4b46-a12d-0e75fb56eba5",
      "comment": "",
      "command": "click",
      "target": "xpath=//input[@placeholder='Search People...']",
      "targets": [],
      "value": ""
    }, {
      "id": "0a2e9add-1ff2-4c65-ae5b-70451a55f244",
      "comment": "",
      "command": "waitForElementVisible",
      "target": "xpath=//lightning-base-combobox-formatted-text[@title='${NAME}']",
      "targets": [],
      "value": "10000"
    }, {
      "id": "a8368c93-2f8b-4e89-a183-92fb4af48bd6",
      "comment": "",
      "command": "click",
      "target": "xpath=//lightning-base-combobox-item[span/span/lightning-base-combobox-formatted-text[@title=\\"${NAME}\\"]]",
      "targets": [],
      "value": ""
    }, {
      "id": "5d44d614-ab45-4c52-915b-5c0686c818c7",
      "comment": "Field: Case (type and select)",
      "command": "",
      "target": "",
      "targets": [],
      "value": ""
    }, {
      "id": "f65bd3ac-88bb-4342-a210-1ac56cdb627a",
      "comment": "Type the string, pause for suggestions to load, click for suggestions to become visible, wait for right suggestion to become visible, click right suggestion",
      "command": "",
      "target": "",
      "targets": [],
      "value": ""
    }, {
      "id": "8953a787-0e22-40c5-930c-0f12ff992aca",
      "comment": "",
      "command": "type",
      "target": "xpath=//input[@placeholder='Search Cases...']",
      "targets": [],
      "value": "${CASE}"
    }, {
      "id": "f673ac53-03ed-481a-a6ba-bb80b261ff34",
      "comment": "",
      "command": "click",
      "target": "xpath=//input[@placeholder='Search Cases...']",
      "targets": [],
      "value": ""
    }, {
      "id": "066d1255-dea9-428d-a6f4-0dcd6978e175",
      "comment": "",
      "command": "waitForElementVisible",
      "target": "xpath=//lightning-base-combobox-formatted-text[@title='${CASE}']",
      "targets": [],
      "value": "10000"
    }, {
      "id": "592b4ff5-bc08-44b2-8a71-159940696cbd",
      "comment": "",
      "command": "click",
      "target": "xpath=//lightning-base-combobox-item[span/span/lightning-base-combobox-formatted-text[@title=\\"${CASE}\\"]]",
      "targets": [],
      "value": ""
    }, {
      "id": "70fd647c-46f6-4da2-a961-6850797a4bb2",
      "comment": "Button: Save (just click)",
      "command": "",
      "target": "",
      "targets": [],
      "value": ""
    }, {
      "id": "5f6dd3ff-0b8b-4aea-bca9-bcc50bf3928f",
      "comment": "",
      "command": "click",
      "target": "xpath=//lightning-button[button[@name=\\"SaveAndNew\\"]]",
      "targets": [],
      "value": ""
    }, {
      "id": "28f3a7bc-5ca4-480b-b57c-e7a700b0bf48",
      "comment": "",
      "command": "echo",
      "target": "Timecard done!",
      "targets": [],
      "value": ""
    }, {
      "id": "23f432d4-2241-45de-a1c2-4c0c7f85f055",
      "comment": "Finish",
      "command": "",
      "target": "",
      "targets": [],
      "value": ""
    }, {
      "id": "f35d85ed-b68c-45b6-9812-0ee4e68cc486",
      "comment": "",
      "command": "end",
      "target": "",
      "targets": [],
      "value": ""
    }, {
      "id": "39b49c18-53eb-4ee7-b8c7-5cf36055eb48",
      "comment": "",
      "command": "echo",
      "target": "All timecards done!",
      "targets": [],
      "value": ""
    }, {
      "id": "6572135b-6722-460a-8aef-c9e07f490893",
      "comment": "",
      "command": "waitForElementVisible",
      "target": "xpath=//lightning-button[button[@name=\\"CancelEdit\\"]]",
      "targets": [],
      "value": "10000"
    }, {
      "id": "48de936d-9a5b-4e91-b80d-af7a62ae3711",
      "comment": "",
      "command": "click",
      "target": "xpath=//lightning-button[button[@name=\\"CancelEdit\\"]]",
      "targets": [],
      "value": ""
    }]
  }],
  "suites": [{
    "id": "d40d4f81-ccd1-4c33-a9a4-03c8d15b32c1",
    "name": "Default Suite",
    "persistSession": false,
    "parallel": false,
    "timeout": 300,
    "tests": ["40afadce-a98b-4e95-8a0f-4f7bb2660f8b"]
  }],
  "urls": ["https://canonical.lightning.force.com/lightning/o/TimeCard__c/new"],
  "plugins": []
}

"""