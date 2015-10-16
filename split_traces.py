#!/usr/bin/python

# Copyright 2015 Personal duanqz@gmail.com.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys
import re
import string

__author__ = 'duanqizhi'


class Options:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    @staticmethod
    def parse_arguments():
        try:
            import argparse
            parser = argparse.ArgumentParser(description='Split traces by each pid.')
            parser.add_argument('-f', '--file', dest='file', help='text file containing android traces log')
            parser.add_argument('-p', '--pid', dest='pid', help='filter out trace partitions of the pid', type=int)

            options = parser.parse_args()
            if options.file is None:
                parser.print_help()
                sys.exit(1)

            return options
        except ImportError:
            sys.exit(1)


class Traces:
    RE_START = re.compile("----- pid (?P<pid>\d+) at (?P<time>.*?) -----")
    RE_PNAME = re.compile("Cmd line: (?P<pname>.*)")
    RE_END = re.compile("----- end (?P<pid>\d+) -----")

    def __init__(self, in_file):
        self.in_file = in_file

        self.partition_dir = os.path.join(os.path.dirname(in_file), "partitions")
        if not os.path.exists(self.partition_dir):
            os.mkdir(self.partition_dir)

    def split(self, pid=None):

        f = open(self.in_file, "r")
        all_lines = f.readlines()

        partition_name = None
        content = None
        for line in all_lines:

            if partition_name is None:
                start = Traces.RE_START.match(line)
                if start is not None:
                    start_pid = start.group("pid")
                    if pid is not None and string.atoi(start_pid) != pid:
                        #print "ignore"
                        continue

                    start_time = start.group("time")
                    partition_name = "%s_%s" % (start_pid, start_time.replace(" ", "-"))
                    print "Catch %s" % partition_name
                    content = line
                    continue

            if partition_name:
                content += line

                process_name = Traces.RE_PNAME.match(line)
                if process_name is not None:
                    short_pname = os.path.basename(process_name.group("pname"))
                    partition_name = "%s_%s" % (short_pname, partition_name)
                    continue

            if partition_name:
                end = Traces.RE_END.match(line)
                if end is not None:
                    self.write_partition(partition_name, content)
                    partition_name = None

        f.close()

    def write_partition(self, partition_name, content):
        partition_path = os.path.join(self.partition_dir, partition_name)
        f = open(partition_path, "w+")
        f.seek(0)
        f.truncate()
        f.writelines(content)
        f.flush()
        f.close()


if __name__ == '__main__':
    options = Options.parse_arguments()
    Traces(options.file).split(options.pid)
