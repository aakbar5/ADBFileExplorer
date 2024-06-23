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

    icon_search_case_sensitive = resource_filename('resources.icons', 'case_sensitive.svg')

    icon_back = resource_filename('resources.icons.toolbar', 'back.svg')
    icon_forward = resource_filename('resources.icons.toolbar', 'forward.svg')
    icon_history = resource_filename('resources.icons.toolbar', 'history.svg')
    icon_home = resource_filename('resources.icons.toolbar', 'home.svg')
    icon_open = resource_filename('resources.icons.toolbar', 'open.svg')
    icon_refresh = resource_filename('resources.icons.toolbar', 'refresh.svg')
    icon_upload = resource_filename('resources.icons.toolbar', 'upload.svg')
    icon_up = resource_filename('resources.icons.toolbar', 'up.svg')
    icon_path_fork = resource_filename('resources.icons.toolbar', 'fork_right.svg')

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
    icon_tag = resource_filename('resources.icons.statusbar', 'tag.svg')
    icon_android = resource_filename('resources.icons.statusbar', 'android.svg')
    icon_lock = resource_filename('resources.icons.statusbar', 'lock.svg')
    icon_unlock = resource_filename('resources.icons.statusbar', 'unlock.svg')
    icon_battery_00 = resource_filename('resources.icons.statusbar.battery', 'battery_00.svg')
    icon_battery_100 = resource_filename('resources.icons.statusbar.battery', 'battery_100.svg')
    icon_battery_xx = resource_filename('resources.icons.statusbar.battery', 'battery_unknown.svg')
    icon_battery_charging_10 = resource_filename('resources.icons.statusbar.battery.charging', 'battery_10.svg')
    icon_battery_charging_20 = resource_filename('resources.icons.statusbar.battery.charging', 'battery_20.svg')
    icon_battery_charging_40 = resource_filename('resources.icons.statusbar.battery.charging', 'battery_40.svg')
    icon_battery_charging_60 = resource_filename('resources.icons.statusbar.battery.charging', 'battery_60.svg')
    icon_battery_charging_80 = resource_filename('resources.icons.statusbar.battery.charging', 'battery_80.svg')
    icon_battery_charging_90 = resource_filename('resources.icons.statusbar.battery.charging', 'battery_90.svg')
    icon_battery_normal_10 = resource_filename('resources.icons.statusbar.battery.normal', 'battery_10.svg')
    icon_battery_normal_20 = resource_filename('resources.icons.statusbar.battery.normal', 'battery_20.svg')
    icon_battery_normal_40 = resource_filename('resources.icons.statusbar.battery.normal', 'battery_40.svg')
    icon_battery_normal_60 = resource_filename('resources.icons.statusbar.battery.normal', 'battery_60.svg')
    icon_battery_normal_80 = resource_filename('resources.icons.statusbar.battery.normal', 'battery_80.svg')
    icon_battery_normal_90 = resource_filename('resources.icons.statusbar.battery.normal', 'battery_90.svg')

    # This "File Formats Flat Multicolor Icons" icon pack was downloaded from
    # https://www.reshot.com/free-svg-icons/pack/file-formats-flat-multicolor-icons-HCK8PU3MX9/
    icons_files = {
        '.aac': resource_filename('resources.icons.files.types', 'aac.svg'),
        '.ai': resource_filename('resources.icons.files.types', 'ai.svg'),
        '.aut': resource_filename('resources.icons.files.types', 'aut.svg'),
        '.avi': resource_filename('resources.icons.files.types', 'avi.svg'),
        '.bin': resource_filename('resources.icons.files.types', 'bin.svg'),
        '.bmp': resource_filename('resources.icons.files.types', 'bmp.svg'),
        '.cad': resource_filename('resources.icons.files.types', 'cad.svg'),
        '.cdr': resource_filename('resources.icons.files.types', 'cdr.svg'),
        '.css': resource_filename('resources.icons.files.types', 'css.svg'),
        '.csv': resource_filename('resources.icons.files.types', 'csv.svg'),
        '.db': resource_filename('resources.icons.files.types', 'db.svg'),
        '.doc': resource_filename('resources.icons.files.types', 'doc.svg'),
        '.docx': resource_filename('resources.icons.files.types', 'docx.svg'),
        '.eps': resource_filename('resources.icons.files.types', 'eps.svg'),
        '.exe': resource_filename('resources.icons.files.types', 'exe.svg'),
        '.flv': resource_filename('resources.icons.files.types', 'flv.svg'),
        '.gif': resource_filename('resources.icons.files.types', 'gif.svg'),
        '.hlp': resource_filename('resources.icons.files.types', 'hlp.svg'),
        '.htm': resource_filename('resources.icons.files.types', 'htm.svg'),
        '.html': resource_filename('resources.icons.files.types', 'html.svg'),
        '.ini': resource_filename('resources.icons.files.types', 'ini.svg'),
        '.iso': resource_filename('resources.icons.files.types', 'iso.svg'),
        '.java': resource_filename('resources.icons.files.types', 'java.svg'),
        '.jpg': resource_filename('resources.icons.files.types', 'jpg.svg'),
        '.js': resource_filename('resources.icons.files.types', 'js.svg'),
        '.mkv': resource_filename('resources.icons.files.types', 'mkv.svg'),
        '.mov': resource_filename('resources.icons.files.types', 'mov.svg'),
        '.mp3': resource_filename('resources.icons.files.types', 'mp3.svg'),
        '.mp4': resource_filename('resources.icons.files.types', 'mp4.svg'),
        '.mpeg': resource_filename('resources.icons.files.types', 'mpeg.svg'),
        '.mpg': resource_filename('resources.icons.files.types', 'mpg.svg'),
        '.pdf': resource_filename('resources.icons.files.types', 'pdf.svg'),
        '.php': resource_filename('resources.icons.files.types', 'php.svg'),
        '.png': resource_filename('resources.icons.files.types', 'png.svg'),
        '.ppt': resource_filename('resources.icons.files.types', 'ppt.svg'),
        '.ps': resource_filename('resources.icons.files.types', 'ps.svg'),
        '.psd': resource_filename('resources.icons.files.types', 'psd.svg'),
        '.rar': resource_filename('resources.icons.files.types', 'rar.svg'),
        '.rss': resource_filename('resources.icons.files.types', 'rss.svg'),
        '.rtf': resource_filename('resources.icons.files.types', 'rtf.svg'),
        '.sql': resource_filename('resources.icons.files.types', 'sql.svg'),
        '.svg': resource_filename('resources.icons.files.types', 'svg.svg'),
        '.swf': resource_filename('resources.icons.files.types', 'swf.svg'),
        '.sys': resource_filename('resources.icons.files.types', 'sys.svg'),
        '.txt': resource_filename('resources.icons.files.types', 'txt.svg'),
        '.wma': resource_filename('resources.icons.files.types', 'wma.svg'),
        '.xls': resource_filename('resources.icons.files.types', 'xls.svg'),
        '.xlsx': resource_filename('resources.icons.files.types', 'xlsx.svg'),
        '.xml': resource_filename('resources.icons.files.types', 'xml.svg'),
        '.zip': resource_filename('resources.icons.files.types', 'zip.svg'),
    }
