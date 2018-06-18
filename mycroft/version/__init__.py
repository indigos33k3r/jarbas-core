# Copyright 2017 Mycroft AI Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json

from genericpath import exists, isfile
from os.path import join, expanduser

from mycroft.configuration import Configuration
from mycroft.util.log import LOG


# The following lines are replaced during the release process.
# START_VERSION_BLOCK
CORE_VERSION_MAJOR = 18
CORE_VERSION_MINOR = 2
CORE_VERSION_BUILD = 8

FORK_VERSION_MAJOR = 0
FORK_VERSION_MINOR = 1
FORK_VERSION_BUILD = "Dev"
# END_VERSION_BLOCK

CORE_VERSION_STR = ("Jarbas Core" + "." +
                    str(FORK_VERSION_MAJOR) + "." +
                    str(FORK_VERSION_MINOR) + "." +
                    str(FORK_VERSION_BUILD) + "." +
                    str(CORE_VERSION_MAJOR) + "." +
                    str(CORE_VERSION_MINOR) + "." +
                    str(CORE_VERSION_BUILD))


class VersionManager(object):
    @staticmethod
    def get():
        data_dir = expanduser(Configuration.get()['data_dir'])
        version_file = join(data_dir, 'version.json')
        if exists(version_file) and isfile(version_file):
            try:
                with open(version_file) as f:
                    return json.load(f)
            except Exception:
                LOG.error("Failed to load version from '%s'" % version_file)
        return {"coreVersion": None, "enclosureVersion": None}


def check_version(version_string):
    """
        Check if current version is equal or higher than the
        version string provided to the function

        Args:
            version_string (string): version string ('Major.Minor.Build')
    """
    major, minor, build = version_string.split('.')
    major = int(major)
    minor = int(minor)
    build = int(build)

    if CORE_VERSION_MAJOR > major:
        return True
    elif CORE_VERSION_MAJOR == major and CORE_VERSION_MINOR > minor:
        return True
    elif major == CORE_VERSION_MAJOR and minor == CORE_VERSION_MINOR and \
            CORE_VERSION_BUILD >= build:
        return True
    else:
        return False
