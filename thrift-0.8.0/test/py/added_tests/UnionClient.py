#!/usr/bin/env python

#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements. See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership. The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.
#

import sys
sys.path.append('./gen-py')

from union import UnionTest
from union.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

try:
  transport = TSocket.TSocket('localhost', 9090)
  transport = TTransport.TBufferedTransport(transport)
  protocol = TBinaryProtocol.TBinaryProtocolAccelerated(transport)
  client = UnionTest.Client(protocol)
  transport.open()

  print " UNION TEST ".center(50, "=")

  # Implicitly checks read and write methods
  try:
    res = client.test_constructor()
    print res, res.setfield
    res = client.test_set_field()
    print res, res.setfield
    res = client.test_clear()
    print res, res.setfield
  except Exception, exe:
    print "TEST FAILED:\n\t%r" % exe
    sys.exit(1)

  print "ALL TESTS PASSED"
  transport.close()

except Thrift.TException, tx:
  print '%s' % (tx.message)
