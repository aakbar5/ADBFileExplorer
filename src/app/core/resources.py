# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov

from pkg_resources import resource_filename
from app.helpers.singleton import Singleton

class Resources:
    __metaclass__ = Singleton

    style_window = resource_filename('resources.styles', 'window.qss')
    style_file_list = resource_filename('resources.styles', 'file-list.qss')
    style_device_list = resource_filename('resources.styles', 'device-list.qss')
    style_notification_button = resource_filename('resources.styles', 'notification-button.qss')

    icon_logo = resource_filename('resources.icons', 'logo.svg')
    icon_link = resource_filename('resources.icons', 'link.svg')
    icon_no_link = resource_filename('resources.icons', 'no_link.svg')
    icon_close = resource_filename('resources.icons', 'close.svg')
    icon_phone = resource_filename('resources.icons', 'phone.svg')
    icon_phone_unknown = resource_filename('resources.icons', 'phone_unknown.svg')
    icon_home = resource_filename('resources.icons', 'home.svg')
    icon_refresh = resource_filename('resources.icons', 'refresh.svg')
    icon_plus = resource_filename('resources.icons', 'plus.svg')
    icon_up = resource_filename('resources.icons', 'up.svg')
    icon_arrow = resource_filename('resources.icons', 'arrow.svg')
    icon_file = resource_filename('resources.icons.files', 'file.svg')
    icon_folder = resource_filename('resources.icons.files', 'folder.svg')
    icon_file_unknown = resource_filename('resources.icons.files', 'file_unknown.svg')
    icon_link_file = resource_filename('resources.icons.files', 'link_file.svg')
    icon_link_folder = resource_filename('resources.icons.files', 'link_folder.svg')
    icon_link_file_unknown = resource_filename('resources.icons.files', 'link_file_unknown.svg')
    icon_files_upload = resource_filename('resources.icons.files.actions', 'files_upload.svg')
    icon_folder_upload = resource_filename('resources.icons.files.actions', 'folder_upload.svg')
    icon_folder_create = resource_filename('resources.icons.files.actions', 'folder_create.svg')

    anim_loading = resource_filename('resources.anim', 'loading.gif')

    # Icons for status bar
    icon_tag = resource_filename('resources.icons', 'tag.svg')
    icon_android = resource_filename('resources.icons', 'android.svg')
    icon_lock = resource_filename('resources.icons', 'lock.svg')
    icon_unlock = resource_filename('resources.icons', 'unlock.svg')
    icon_battery_00 = resource_filename('resources.icons.battery', 'battery_00.svg')
    icon_battery_100 = resource_filename('resources.icons.battery', 'battery_100.svg')
    icon_battery_xx = resource_filename('resources.icons.battery', 'battery_unknown.svg')
    icon_battery_charging_10 = resource_filename('resources.icons.battery.charging', 'battery_10.svg')
    icon_battery_charging_20 = resource_filename('resources.icons.battery.charging', 'battery_20.svg')
    icon_battery_charging_40 = resource_filename('resources.icons.battery.charging', 'battery_40.svg')
    icon_battery_charging_60 = resource_filename('resources.icons.battery.charging', 'battery_60.svg')
    icon_battery_charging_80 = resource_filename('resources.icons.battery.charging', 'battery_80.svg')
    icon_battery_charging_90 = resource_filename('resources.icons.battery.charging', 'battery_90.svg')
    icon_battery_normal_10 = resource_filename('resources.icons.battery.normal', 'battery_10.svg')
    icon_battery_normal_20 = resource_filename('resources.icons.battery.normal', 'battery_20.svg')
    icon_battery_normal_40 = resource_filename('resources.icons.battery.normal', 'battery_40.svg')
    icon_battery_normal_60 = resource_filename('resources.icons.battery.normal', 'battery_60.svg')
    icon_battery_normal_80 = resource_filename('resources.icons.battery.normal', 'battery_80.svg')
    icon_battery_normal_90 = resource_filename('resources.icons.battery.normal', 'battery_90.svg')
