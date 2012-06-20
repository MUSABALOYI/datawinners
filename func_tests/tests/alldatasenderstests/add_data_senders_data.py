# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8


##Variables
NAME = "name"
MOBILE_NUMBER = "mobile_number"
MOBILE_NUMBER_WITHOUT_HYPHENS = "mobile_number_without_hyphens"
COMMUNE = "commune"
GPS = "gps"
WEB_CHANNEL = False
EMAIL_ADDRESS = ""
SUCCESS_MSG = "message"
ERROR_MSG = "message"

BLANK_FIELDS = {NAME: "",
                MOBILE_NUMBER: "",
                COMMUNE: "",
                GPS: "",
                ERROR_MSG: "Name This field is required.Mobile Number This field is required.Name Please fill out at least one location field correctly.GPS Coordinates Find GPS coordinates Please fill out at least one location field correctly."}

VALID_DATA = {NAME: "Mickey Duck",
              MOBILE_NUMBER: "9876-543-2101",
              MOBILE_NUMBER_WITHOUT_HYPHENS: "98765432101",
              COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
              GPS: "-21.7622088847 48.0690991394",
              SUCCESS_MSG: "Registration successful. ID is: rep"}
VALID_EDIT_DATA = {NAME: "EDIT Mickey Duck",
              MOBILE_NUMBER: "9876-543-2107",
              COMMUNE: "PUNE",
              GPS: "",
              SUCCESS_MSG: "Your changes have been saved."}

VALID_DATA_WITH_EMAIL = {NAME: "Mickey Duck",
              MOBILE_NUMBER: "9876-544-2103",
              COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
              EMAIL_ADDRESS: "mickey",
              GPS: "-21.7622088847 48.0690991394",
              SUCCESS_MSG: "Registration successful. ID is: rep"}
VALID_DATA_WITHOUT_EMAIL = {NAME: "Mickey Duck",
              MOBILE_NUMBER: "9876-544-2102",
              COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
              EMAIL_ADDRESS: "",
              GPS: "-21.7622088847 48.0690991394",
              ERROR_MSG: "Email address This field is required."}

EXISTING_DATA = {NAME: "Mickey Mouse",
                 MOBILE_NUMBER: "123-4567-890",
                 COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
                 GPS: "-21.7622088847 48.0690991394",
                 ERROR_MSG: "Mobile Number Sorry, the telephone number 1234567890 has already been registered"}

WITHOUT_LOCATION_NAME = {NAME: "Mini Mouse",
                         MOBILE_NUMBER: "345-673-45681",
                         COMMUNE: "",
                         GPS: "-20.676646 47.197266",
                         SUCCESS_MSG: "Registration successful. ID is: rep"}

WITHOUT_GPS = {NAME: "Alladin",
               MOBILE_NUMBER: "45673456821",
               COMMUNE: "MAHAVELO,AMBOTAKA,MANAKARA ATSIMO,VATOVAVY FITOVINANY",
               GPS: "",
               SUCCESS_MSG: "Registration successful. ID is: rep"}

INVALID_LATITUDE_GPS = {NAME: "Invalid Latitude GPS",
                        MOBILE_NUMBER: "+673-4568-345",
                        COMMUNE: "",
                        GPS: "123 90",
                        ERROR_MSG: "GPS Coordinates Find GPS coordinates Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}

INVALID_LONGITUDE_GPS = {NAME: "Invalid Longitude GPS",
                         MOBILE_NUMBER: "(73)456-834-56",
                         COMMUNE: "",
                         GPS: "23 190",
                         ERROR_MSG: "GPS Coordinates Find GPS coordinates Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}

INVALID_GPS = {NAME: "Invalid GPS with Semi-Colon",
               MOBILE_NUMBER: "7345abc456",
               COMMUNE: "",
               GPS: "23; 10",
               ERROR_MSG: "Mobile Number Please enter a valid phone number.GPS Coordinates Find GPS coordinates Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}

INVALID_GPS_WITH_COMMA = {NAME: "Invalid GPS With Comma",
                          MOBILE_NUMBER: "734ABCD456",
                          COMMUNE: "",
                          GPS: "23,10",
                          ERROR_MSG: "Mobile Number Please enter a valid phone number.Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}

WITH_UNICODE_IN_GPS = {NAME: "Unicode in GPS",
                       MOBILE_NUMBER: "567!@#$834",
                       COMMUNE: "",
                       GPS: u"23º 45",
                       ERROR_MSG: "Mobile Number Please enter a valid phone number.GPS Coordinates Find GPS coordinates Incorrect GPS format. The GPS coordinates must be in the following format: xx.xxxx,yy.yyyy. Example -18.8665,47.5315"}
