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
import argparse
import string

__author__ = 'duanqizhi'


class Options:
    def __init__(self, **kwds):
        self.__dict__.update(kwds)

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(description='Split traces by each pid.')
        parser.add_argument('-f', '--file', dest='file', help='text file containing android traces log')
        parser.add_argument('-p', '--pid', dest='pid', help='filter out trace partitions of the pid', type=int)

        args = parser.parse_args()
        if args.file is None:
            parser.print_help()
            sys.exit(1)

        return args


class Traces:
    """ Model of text traces file
    """

    # Regex to match text like: "----- pid 880 at 2015-10-14 13:47:53 -----", group out pid and time
    RE_START = re.compile("----- pid (?P<pid>\d+) at (?P<time>.*?) -----")

    # Regex to match text like: "Cmd line: system_server", group out process name
    RE_PNAME = re.compile("Cmd line: (?P<pname>.*)")

    # Regex to match text like: "----- end 880 -----", group out pid
    RE_END = re.compile("----- end (?P<pid>\d+) -----")

    def __init__(self, in_file):
        self.in_file = in_file

        self.partition_dir = os.path.join(os.path.dirname(in_file), "partitions")
        if not os.path.exists(self.partition_dir):
            os.makedirs(self.partition_dir)

    def split(self, pid=None):
        """ Split the traces.txt to partitions.
            :param pid: If pid is presented, only keep partitions of the pid
        """

        f = open(self.in_file, "r")
        all_lines = f.readlines()

        partition_name = None
        process_name = None
        content = None
        for line in all_lines:
            # Escape the illegal characters
            line = line.replace("\00", "")

            if partition_name is None:
                start = Traces.RE_START.match(line)
                if start is not None:
                    start_pid = start.group("pid")
                    if pid is not None and string.atoi(start_pid) != pid:
                        #print "ignore"
                        continue

                    start_time = start.group("time")
                    # Generate the partition_name with pid and time
                    partition_name = "%s_%s" % (start_pid, start_time.replace(" ", "-"))
                    content = line
                    continue

            if partition_name:
                content += line
                if process_name is None:
                    process_match = Traces.RE_PNAME.match(line)
                    if process_match is not None:
                        process_name = os.path.basename(process_match.group("pname"))
                        # Insert the process_name to partition_name
                        partition_name = "%s_%s" % (process_name, partition_name)
                        print "%s" % partition_name
                else:
                    end = Traces.RE_END.match(line)
                    if end is not None:
                        self.write_partition(partition_name, content)

                        partition_name = None
                        process_name = None

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
    args = Options.parse_arguments()

    Traces(args.file).split(args.pid)
