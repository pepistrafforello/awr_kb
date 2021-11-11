#
#    Copyright 2021 Expert System USA, Inc.

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#

python3 wd2dgraph2.py        0  10000000 a. > /tmp/chunk01.log 2>&1 &
python3 wd2dgraph2.py 10000000  20000000 b. > /tmp/chunk02.log 2>&1 &
python3 wd2dgraph2.py 20000000  30000000 c. > /tmp/chunk03.log 2>&1 &
python3 wd2dgraph2.py 30000000  40000000 d. > /tmp/chunk04.log 2>&1 &
python3 wd2dgraph2.py 40000000  50000000 e. > /tmp/chunk05.log 2>&1 &
python3 wd2dgraph2.py 50000000  60000000 f. > /tmp/chunk06.log 2>&1 &
python3 wd2dgraph2.py 60000000  70000000 g. > /tmp/chunk07.log 2>&1 &
python3 wd2dgraph2.py 70000000  80000000 h. > /tmp/chunk08.log 2>&1 &
python3 wd2dgraph2.py 80000000  90000000 i. > /tmp/chunk09.log 2>&1 &
python3 wd2dgraph2.py 90000000 100000000 j. > /tmp/chunk10.log 2>&1 &
