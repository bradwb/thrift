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

from union import UnionTest
from union.ttypes import *

from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

import unittest

class UnionTestHandler(unittest.TestCase):

	def setup(self):
		self.tu = TestUnion()

	def test_set_field(self):
		self.tu.set_field('i32_field', 43)
		self.tu.validate()
		self.assertEqual(self.tu, TestUnion(i32_field=43))

		self.tu.set_field('string_field', '43')
		self.tu.validate()
		self.assertEqual(self.tu, TestUnion(string_field='43'))

		self.tu.set_field('struct_field', OneOfEach(what_who=True))
		self.tu.validate()
		self.assertEqual(self.tu, TestUnion(struct_field=OneOfEach(what_who=True)))

		self.tu.clear()

		self.tu.set_field('i32_set', set([5,4,2,1]))
		self.tu.validate()
		self.assertEqual(self.tu, TestUnion(i32_set=set([5,4,2,1])))
		self.assertEqual(self.tu.setfield, 'i32_set')

		self.tu.set_field('i32_map', {1:1, 2:3, 6:50})
		self.tu.validate()
		self.assertEqual(self.tu, TestUnion(i32_map={1:1, 2:3, 6:50}))
		self.assertEqual(self.tu.setfield, 'i32_map')

		self.tu.i32_field = 'anything?'

		self.tu.set_field('enum_field', SomeEnum.ONE)
		self.tu.validate()
		self.assertEqual(self.tu, TestUnion(enum_field=1))
		self.assertEqual(self.tu.setfield, 'enum_field')

		self.assertRaises(TProtocol.TProtocolException, self.tu.set_field, 'not_a_field', 43)
		self.assertRaises(TProtocol.TProtocolException, self.tu.set_field, 'should_fail', 'blah')
		
		return TestUnion(enum_field=SomeEnum.TWO)

	def test_constructor(self):
		self.tu = TestUnion(enum_field=2, struct_field=OneOfEach())
		self.assertRaises(TProtocol.TProtocolException, self.tu.validate)
		
		self.tu = TestUnion(struct_field=BigFieldIdStruct())
		self.assertRaises(TProtocol.TProtocolException, self.tu.validate)
		
		# Because of the declaration order of these 2 fields in the thrift spec,
		# setfield will default to 'enum_field'. This is behavior is purely
		# a result of the implementation
		self.tu = TestUnion(enum_field=SomeEnum.TWO, struct_field=OneOfEach())
		self.tu.enum_field = None
		self.assertRaises(TProtocol.TProtocolException, self.tu.validate)

		return TestUnion(struct_field=OneOfEach(what_who=False))

	def test_clear(self):
		empty = TestUnion(string_field=None, i32_field=None, struct_field=None,
				struct_list=None, other_i32_field=None, enum_field=None, i32_set=None,
				i32_map=None)
		
		self.tu.set_field('i32_field', 30)
		self.tu.clear()
		self.assertEqual(self.tu, TestUnion())
		self.assertEqual(self.tu, empty)

		self.tu = TestUnion(string_field='a value', i32_field=34, other_i32_field=445)
		self.tu.clear()
		self.assertEqual(self.tu, TestUnion())
		self.assertEqual(self.tu, empty)

		return TestUnion(i32_field=30)

	def runTest(self):
		self.test_constructor()
		self.test_clear()
		self.test_set_field()

#	def messAround(self, br, self.tu):
#		br.set_field('field1', 'awwwwyeaaaaaa')
#		assert br.get_field() == 'awwwwyeaaaaaa'
#		try:
#			br.set_field('field', None)
#		except TProtocol.TProtocolException, exe:
#			print "D'oh:  %s" % exe.message
#		br.clear()
#		assert br.setfield is None
#		br.set_field('field3', '\'ello')
#		try:
#			br.validate()
#		except TProtocol.TProtocolException, exe:
#			print "D'oh:  %s" % exe.message
#		br.clear()
#		br.set_field('field3', 1234)
#		br.set_field('field2', BigFieldIdStruct())
#		br.set_field('field2', self.tu)
#		try:
#			br.validate()
#		except TProtocol.TProtocolException, exe:
#			print "D'oh:  %s" % exe.message
		

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
