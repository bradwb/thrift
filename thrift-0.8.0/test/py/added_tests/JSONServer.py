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
sys.path.append('../../../lib/py/src')

from jsontest import JsonTest
from jsontest.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TJSONProtocol
from thrift.server import TServer

import unittest

class JsonTestHandler(unittest.TestCase):

#	def setup(self):
#		self.tu = TestUnion()

  def test(self, testStruct):
    ret = RandomStuff()
    ret.myintlist = testStruct.i32_list[:]
    myWrapper = Wrapper(Empty())
    ret.maps = {3 : myWrapper}
    ret.bigint = testStruct.a_i64
    ret.triple = testStruct.a_double
    ret.a = 12431234
    ret.b = testStruct.a_i32
    ret.c = 40000
    ret.d = 0
    return ret
    #self.assertEqual(self.tu, TestUnion(i32_field=43))

		#self.tu.clear()

		#self.assertEqual(self.tu.setfield, 'i32_set')

  def runTest(self):
    self.test()
    self.test()



handler = JsonTestHandler()
processor = JsonTest.Processor(handler)
transport = TSocket.TServerSocket(port=9090)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TJSONProtocol.TJSONProtocolFactory()

server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

# You could do one of these for a multithreaded server
#server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
#server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)

print 'Starting the server...'
server.serve()
print 'done.'
