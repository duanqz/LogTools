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
import shutil
import unittest
from split_traces import Options, Traces

__author__ = 'duanqizhi'


class Test(unittest.TestCase):

    TRACES_TXT = os.path.join(os.curdir, "traces.txt")
    PATITIONS_DIR = os.path.join(os.curdir, "partitions")

    def setUp(self):
        if os.path.exists(Test.PATITIONS_DIR):
            shutil.rmtree(Test.PATITIONS_DIR)

    def test_split_traces(self):
        args = Options(file=Test.TRACES_TXT, pid=880)
        Traces(args.file).split(args.pid)

        self.assertTrue(os.path.exists(Test.PATITIONS_DIR))

        # Totally have 21 partitions of pid=880
        self.assertEqual(len(os.listdir(Test.PATITIONS_DIR)), 21)

        shutil.rmtree(Test.PATITIONS_DIR)


if __name__ == '__main__':
    unittest.main()
