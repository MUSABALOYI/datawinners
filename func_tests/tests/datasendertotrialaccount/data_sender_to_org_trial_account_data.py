from datetime import datetime
from datawinners.messageprovider.tests.test_message_handler import THANKS

today = datetime.utcnow()
current_date = today.strftime("%d.%m.%Y") #str(today.day) + "." + str(today.month) + "." + str(today.year)

SENDER = "from"
RECEIVER = "to"
SMS = "sms"
SUCCESS_MESSAGE = "message"

VALID_DATA = {SENDER: "1234567890",
              RECEIVER: '17752374679',
              SMS: "cli001 .EID cid003 .NA Mr. Tessy .FA 38 .RD 17.01.2012 .BG b .SY ade .GPS 27.178057  -78.007789 .RM a",
              SUCCESS_MESSAGE: "Thank you Shweta. We received : EID: cid003 NA: Mr. Tessy FA: 58.0 RD: 17.05.2011 BG: O- SY: Rapid weight loss,Memory loss,Neurological disorders GPS: 27.178057,-78.007789"}

TRIAL_SMS_DATA = u"Testcid003 %s Shwetarep1 Mr. Tessy 38 17.01.2012 O- Rapid weight loss, Memory loss, Neurological disorders 27.178057 -78.007789 Hivid" % (current_date,)

VALID_PAID_DATA = {SENDER: "1234567890",
              RECEIVER: '919880734937',
              SMS: "cli001 .EID cid003 .NA Mr. Tessy .FA 77 .RD %s .BG b .SY ade .GPS 27.178057  -78.007789 .RM a" % current_date,
              SUCCESS_MESSAGE: THANKS + " EID: cid003 NA: Mr. Tessy FA: 77.0 RD: %s BG: O- SY: Rapid weight loss,Memory loss,Neurological disorders GPS: 27.178057,-78.007789" % current_date}

PAID_SMS_DATA = u"Testcid003 %s %s Shwetarep1 Mr. Tessy 77 O- Rapid weight loss, Memory loss, Neurological disorders 27.178057 -78.007789 Hivid" % (current_date,current_date)

PROJECT_NAME = 'clinic test project'




