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

from tutorial import Calculator
from tutorial.ttypes import *

from thrift import Thrift
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol

try:

  # Make socket
  transport = TSocket.TSocket('localhost', 9090)

  # Buffering is critical. Raw sockets are very slow
  transport = TTransport.TBufferedTransport(transport)

  # Wrap in a protocol
  protocol = TBinaryProtocol.TBinaryProtocol(transport)

  # Create a client to use the protocol encoder
  client = Calculator.Client(protocol)

  # Connect!
  transport.open()
  
  print "TEST SIMPLE NUMBERS"
  out = lambda num: "Client got: " + str(num) 
  integ = Num(num1=12)
  print "Begin: ", integ
  flt = Num(num2=124.1281)
  print "Begin: ", flt
  print out(client.echo(integ))
  print out(client.echo(flt))
  integ.set_field('num2', 12.0)
  assert client.echo(integ) == integ
  try:
    flt.set_field('num1', 40)
    flt.num2 = 123
    #print out(client.echo(flt))
  except TProtocol.TProtocolException, exe:
    print "Invalid Operation %r" % exe

#  client.change(ret1)
#  client.change(ret2)
  big1 = Biggun(myi32=34)
  big2 = Biggun(mylist=[2,456,12154])
  big2.set_field('mymap', {'hey':123, 'watup':22})
  big2.set_field('myset', set([1,4,5,2,1]))
  print big2
  print out(client.echoBig(big1))
  print out(client.echoBig(big2))
  client.clear(big1)
  print big1
  # Close!
  transport.close()

except Thrift.TException, tx:
  print '%s' % (tx.message)
