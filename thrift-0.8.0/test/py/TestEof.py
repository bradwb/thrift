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

import sys, glob
from optparse import OptionParser
parser = OptionParser()
parser.add_option('--genpydir', type='string', dest='genpydir', default='gen-py')
options, args = parser.parse_args()
del sys.argv[1:] # clean up hack so unittest doesn't complain
sys.path.insert(0, options.genpydir)
sys.path.insert(0, glob.glob('../../lib/py/build/lib.*')[0])

import sys
sys.path.append('../gen-py')

from ThriftTest import ThriftTest
from ThriftTest.ttypes import *
from thrift.transport import TTransport
from thrift.transport import TSocket
from thrift.protocol import TBinaryProtocol
from thrift.protocol import TCompactProtocol
from thrift.protocol import TJSONProtocol
import unittest
import time

class TestEof(unittest.TestCase):

  def make_data(self, pfactory=None):
    trans = TTransport.TMemoryBuffer()
    if pfactory:
      prot = pfactory.getProtocol(trans)
    else:
      prot = TBinaryProtocol.TBinaryProtocol(trans)

    x = Xtruct()
    x.string_thing = "Zero"
    x.byte_thing = 0

    x.write(prot)

    x = Xtruct()
    x.string_thing = "One"
    x.byte_thing = 1

    x.write(prot)

    return trans.getvalue()

  def testTransportReadAll(self):
    """Test that readAll on any type of transport throws an EOFError"""
    trans = TTransport.TMemoryBuffer(self.make_data())
    trans.readAll(1)

    try:
      trans.readAll(10000)
    except EOFError:
      return

    self.fail("Should have gotten EOFError")

  def eofTestHelper(self, pfactory):
    trans = TTransport.TMemoryBuffer(self.make_data(pfactory))
    prot = pfactory.getProtocol(trans)

    x = Xtruct()
    x.read(prot)
    self.assertEqual(x.string_thing, "Zero")
    self.assertEqual(x.byte_thing, 0)

    x = Xtruct()
    x.read(prot)
    self.assertEqual(x.string_thing, "One")
    self.assertEqual(x.byte_thing, 1)

    try:
      x = Xtruct()
      x.read(prot)
    except EOFError:
      return

    self.fail("Should have gotten EOFError")

  def eofTestHelperStress(self, pfactory):
    """Teest the ability of TBinaryProtocol to deal with the removal of every byte in the file"""
    # TODO: we should make sure this covers more of the code paths

    data = self.make_data(pfactory)
    for i in xrange(0, len(data) + 1):
      trans = TTransport.TMemoryBuffer(data[0:i])
      prot = pfactory.getProtocol(trans)
      try:
        x = Xtruct()
        x.read(prot)
        x.read(prot)
        x.read(prot)
      except EOFError:
        continue
      self.fail("Should have gotten an EOFError")

  def testBinaryProtocolEof(self):
    """Test that TBinaryProtocol throws an EOFError when it reaches the end of the stream"""
    self.eofTestHelper(TBinaryProtocol.TBinaryProtocolFactory())
    self.eofTestHelperStress(TBinaryProtocol.TBinaryProtocolFactory())

  def testBinaryProtocolAcceleratedEof(self):
    """Test that TBinaryProtocolAccelerated throws an EOFError when it reaches the end of the stream"""
    self.eofTestHelper(TBinaryProtocol.TBinaryProtocolAcceleratedFactory())
    self.eofTestHelperStress(TBinaryProtocol.TBinaryProtocolAcceleratedFactory())

  def testCompactProtocolEof(self):
    """Test that TCompactProtocol throws an EOFError when it reaches the end of the stream"""
    self.eofTestHelper(TCompactProtocol.TCompactProtocolFactory())
    self.eofTestHelperStress(TCompactProtocol.TCompactProtocolFactory())

  def testJSONProtocolEof(self):
    """Test that TJSONProtocol throws an EOFError when it reaches the end of the stream"""
    self.eofTestHelper(TJSONProtocol.TJSONProtocolFactory())
    self.eofTestHelperStress(TJSONProtocol.TJSONProtocolFactory())


def suite():
  suite = unittest.TestSuite()
  loader = unittest.TestLoader()
  suite.addTest(loader.loadTestsFromTestCase(TestEof))
  return suite

if __name__ == "__main__":
  unittest.main(defaultTest="suite", testRunner=unittest.TextTestRunner(verbosity=2))
