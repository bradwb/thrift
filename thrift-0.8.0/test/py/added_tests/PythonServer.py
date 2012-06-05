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
sys.path.append('../gen-py')

from debug import UnionTest
from debug.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

class UnionTestHandler:

	def messAround(self, br, tu):
		br.set_field('field1', 'awwwwyeaaaaaa')
		assert br.get_field() == 'awwwwyeaaaaaa'
		try:
			br.set_field('field', None)
		except TProtocol.TProtocolException, exe:
			print "D'oh:  %s" % exe.message
		br.clear()
		assert br.setfield is None
		br.set_field('field3', '\'ello')
		try:
			br.validate()
		except TProtocol.TProtocolException, exe:
			print "D'oh:  %s" % exe.message
		br.clear()
		br.set_field('field3', 1234)
		br.set_field('field2', BigFieldIdStruct())
		br.set_field('field2', tu)
		try:
			br.validate()
		except TProtocol.TProtocolException, exe:
			print "D'oh:  %s" % exe.message
		

	def makeFromTU(self, tu):
		pass

	def record(self, n):
		pass

	def makeSomethingBreak(self, tu):
		pass


handler = UnionTestHandler()
processor = UnionTest.Processor(handler)
transport = TSocket.TServerSocket(port=9090)
tfactory = TTransport.TBufferedTransportFactory()
pfactory = TBinaryProtocol.TBinaryProtocolFactory()

server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)

# You could do one of these for a multithreaded server
#server = TServer.TThreadedServer(processor, transport, tfactory, pfactory)
#server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)

print 'Starting the server...'
server.serve()
print 'done.'
