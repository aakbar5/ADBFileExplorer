# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov

import datetime
import posixpath

from app.core.settings import SettingsOptions, Settings

size_types = (
    ('BYTE', 'B'),
    ('KILOBYTE', 'KB'),
    ('MEGABYTE', 'MB'),
    ('GIGABYTE', 'GB'),
    ('TERABYTE', 'TB')
)

file_types = (
    ('-', 'File'),
    ('d', 'Directory'),
    ('l', 'Link'),
    ('c', 'Character'),
    ('b', 'Block'),
    ('s', 'Socket'),
    ('p', 'FIFO')
)

months = (
    ('NONE', 'None', 'None'),
    ('JANUARY', 'Jan.', 'January'),
    ('FEBRUARY', 'Feb.', 'February'),
    ('MARCH', 'Mar.', 'March'),
    ('APRIL', 'Apr.', 'April'),
    ('MAY', 'May', 'May'),
    ('JUNE', 'Jun.', 'June'),
    ('JULY', 'Jul.', 'July'),
    ('AUGUST', 'Aug.', 'August'),
    ('SEPTEMBER', 'Sep.', 'September'),
    ('OCTOBER', 'Oct.', 'October'),
    ('NOVEMBER', 'Nov.', 'November'),
    ('DECEMBER', 'Dec.', 'December'),
)

days = (
    ('MONDAY', 'Monday'),
    ('TUESDAY', 'Tuesday'),
    ('WEDNESDAY', 'Wednesday'),
    ('THURSDAY', 'Thursday'),
    ('FRIDAY', 'Friday'),
    ('SATURDAY', 'Saturday'),
    ('SUNDAY', 'Sunday'),
)


class File:
    def __init__(self, **kwargs):
        self.name = str(kwargs.get("name"))
        self.owner = str(kwargs.get("owner"))
        self.group = str(kwargs.get("group"))
        self.other = str(kwargs.get("other"))
        self.path = str(kwargs.get("path"))
        self.link = str(kwargs.get("link"))
        self.link_type = str(kwargs.get("link_type"))
        self.file_type = str(kwargs.get("file_type"))
        self.permissions = str(kwargs.get("permissions"))

        self.raw_size = kwargs.get("size") or 0
        self.raw_date = kwargs.get("date_time")

    def __str__(self):
        return f"{self.type} '{self.name}' (at '{self.location}')"

    @property
    def size(self):
        if not self.raw_size:
            return ''
        count = 0
        result = self.raw_size
        while result >= 1024 and count < len(size_types):
            result /= 1024
            count += 1

        return f'{round(result, 2)} {size_types[count][1]}'

    @property
    def date(self):
        if not self.raw_date:
            return None

        # An object of <class 'datetime.datetime'>
        created = self.raw_date

        date_fmt_type = Settings.get_value(SettingsOptions.FILE_DATE_FORMAT)
        if date_fmt_type == 'ISO':
            return str(created.isoformat())

        if date_fmt_type == 'Locale (24 Hours)':
            fmt = "%m/%d/%Y %H:%M"
            return str(created.strftime(fmt))

        if date_fmt_type == 'Locale (12 Hours)':
            fmt = "%m/%d/%Y %I:%M %p"
            return str(created.strftime(fmt))

        # Default is informal
        now = datetime.datetime.now()
        if created.year < now.year:
            return f'{created.day} {months[created.month][1]} {created.year}'
        if created.month < now.month:
            return f'{created.day} {months[created.month][1]}'
        if created.day + 7 < now.day:
            return f'{created.day} {months[created.month][2]}'
        if created.day + 1 < now.day:
            return f'{days[created.weekday()][1]} at {str(created.time())[:-3]}'
        if created.day < now.day:
            return f"Yesterday at {str(created.time())[:-3]}"
        return str(created.time())[:-3]

    @property
    def location(self):
        return posixpath.dirname(self.path or '') + '/'

    @property
    def type(self):
        for ft in file_types:
            if self.permissions and self.permissions[0] == ft[0]:
                return ft[1]
        return 'Unknown'

    @property
    def isdir(self):
        return self.type in (FileType.DIRECTORY, FileType.DIRECTORY)


class FileType:
    FILE = 'File'
    DIRECTORY = 'Directory'
    LINK = 'Link'
    CHARACTER = 'Character'
    BLOCK = 'Block'
    SOCKET = 'Socket'
    FIFO = 'FIFO'
    UNKNOWN = 'Unknown'


class Device:
    def __init__(self, **kwargs):
        self.id = kwargs.get("id")
        self.name = kwargs.get("name")
        self.type = kwargs.get("type")


class DeviceType:
    DEVICE = 'device'
    UNKNOWN = 'Unknown'


class MessageData:
    def __init__(self, **kwargs):
        self.timeout = kwargs.get("timeout") or 0
        self.title = kwargs.get("title") or "Message"
        self.body = kwargs.get("body")
        self.message_type = kwargs.get("message_type") or MessageType.MESSAGE
        self.message_catcher = kwargs.get("message_catcher") or None


class MessageType:
    MESSAGE = 1
    LOADING_MESSAGE = 2
