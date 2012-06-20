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

from thrift.Thrift import TType
from TProtocol import *
from json import dumps, loads

class LookaheadReader:
  def __init__(self, trans):
    self.trans = trans
    self._hasData = False
    self.data = ''

  def read(self, size=1):
    if self._hasData:
      self._hasData = False
      chars = self.data + self.trans.readAll(size - 1)
      self.data = chars[-1] 
    else:
      self.data = self.trans.readAll(size)[-1]
    return self.data

  def peek(self):
    if not self._hasData:
      self.data = self.trans.readAll(1)
    self._hasData = True
    return self.data

class TJSONProtocol(TProtocolBase):

  """Binary implementation of the Thrift protocol driver."""

  VERSION = 1

  INTEGRAL = "1234567890+-"
  NUMERIC = INTEGRAL + ".eEinfinitynanINFINITYNAN"

  ARRAY_ST = "["
  ARRAY_END = "]"
  OBJ_ST = "{"
  OBJ_END = "}"
  PAIR = ":"
  SEP = ","
  FIRST = ""

  nameMap = {
      TType.MAP : "map",
      TType.LIST : "lst",
      TType.SET : "set",
      TType.STRUCT : "rec",
      TType.BOOL : "tf",
      TType.BYTE : "i8",
      TType.I16 : "i16",
      TType.I32 : "i32",
      TType.I64 : "i64",
      TType.DOUBLE : "dbl",
      TType.STRING : "str"
  }

  typeMap = dict((v,k) for k, v in nameMap.iteritems())

  def __init__(self, trans, strictRead=False, strictWrite=True):
    TProtocolBase.__init__(self, trans)
    self.reader = LookaheadReader(self.trans)
    self.context = [self.FIRST]
    self.strictRead = strictRead
    self.strictWrite = strictWrite

  def _flushContext(self):
    self.trans.write(self.context.pop())

  def _universalWrite(self, outStruct):
    displayContext = self.context.pop()
    outerContext = self.context[-1]
    isKey = outerContext == self.OBJ_END and displayContext in (self.SEP, self.FIRST)
    if isinstance(outStruct, (int, float)) and isKey:
      outStruct = str(outStruct) # If key is number, put quotes around
    self.trans.write(displayContext)
    out = dumps(outStruct)#.replace(" ", "") # No Spaces
    self.trans.write(out)
    if isKey:
      self.context.append(self.PAIR)
    else:
      self.context.append(self.SEP)

  writeString = writeBool = writeByte = writeI16 = \
      writeI32 = writeI64 = writeDouble = _universalWrite

  def _universalWriteSeqEnd(self):
    self.context.pop() # Unqueue separator
    self.trans.write(self.context.pop()) # Write seq end
    self.context.append(self.SEP) # Queue separator

  writeStructEnd = writeSetEnd = \
      writeListEnd = writeFieldEnd = _universalWriteSeqEnd

  def _seqBegin(self, start, end):
    self._flushContext()
    self.trans.write(start)
    self.context.extend([end, self.FIRST])

  def writeMessageBegin(self, name, type, seqid):
    self._seqBegin(self.ARRAY_ST, self.ARRAY_END)
    if self.strictWrite:
      self.writeI32(self.VERSION)
      self.writeString(name)
      self.writeByte(type)
      self.writeI32(seqid)
    else:
      self.writeString(name)
      self.writeByte(type)
      self.writeI32(seqid)

  def writeMessageEnd(self):
    self._universalWriteSeqEnd()
    self.context = [self.FIRST]

  def writeStructBegin(self, name):
    self._seqBegin(self.OBJ_ST, self.OBJ_END)

  def writeFieldBegin(self, name, type, id):
    self.writeI16(id)
    self._seqBegin(self.OBJ_ST, self.OBJ_END)
    self.writeString(self.nameMap[type])

  def writeFieldStop(self):
    pass

  def writeMapBegin(self, ktype, vtype, size):
    self._seqBegin(self.ARRAY_ST, self.ARRAY_END)
    self.writeString(self.nameMap[ktype])
    self.writeString(self.nameMap[vtype])
    self.writeI32(size)
    self._seqBegin(self.OBJ_ST, self.OBJ_END)

  def writeMapEnd(self):
    self.context.pop()
    self.trans.write(self.context.pop())
    self.trans.write(self.context.pop())
    self.context.append(self.SEP)

  def writeListBegin(self, etype, size):
    self._seqBegin(self.ARRAY_ST, self.ARRAY_END)
    self.writeString(self.nameMap[etype])
    self.writeI32(size)

  def writeSetBegin(self, etype, size):
    self._seqBegin(self.ARRAY_ST, self.ARRAY_END)
    self.writeString(self.nameMap[etype])
    self.writeI32(size)

  def _universalReadSeqEnd(self):
    self.reader.read()

  readMessageEnd = readListEnd = readSetEnd = readStructEnd = \
      readFieldEnd = _universalReadSeqEnd

  def _stripSeparators(self):
    if self.reader.peek() in (self.SEP, self.PAIR):
      self.reader.read()

  def readMessageBegin(self):
    self.reader.read()
    version = self.readI32()
    if version != self.VERSION:
      raise TProtocolException(type=TProtocolException.BAD_VERSION, message='Bad version in readMessageBegin: %d' % (version))
    name = self.readString()
    type = self.readByte();
    seqid = self.readI32()
    return (name, type, seqid)

  def readStructBegin(self):
    self._stripSeparators()
    self.reader.read()

  def readFieldBegin(self):
    self._stripSeparators()
    if self.reader.peek() == self.OBJ_END:
      return (None, TType.STOP, 0)
    id = self.readByte()
    self.reader.read(2)
    typeNum = self.readString()
    type = self.typeMap[typeNum]
    return (None, type, id)

  def readMapBegin(self):
    self._stripSeparators()
    self.reader.read()
    ktypeStr = self.readString()
    vtypeStr = self.readString()
    ktype = self.typeMap[ktypeStr]
    vtype = self.typeMap[vtypeStr]
    size = self.readI32()
    self.reader.read(2)
    return (ktype, vtype, size)

  def readMapEnd(self):
    self.reader.read(2)

  def readListBegin(self):
    self._stripSeparators()
    self.reader.read()
    etypeStr = self.readString()
    etype = self.typeMap[etypeStr]
    size = self.readI32()
    return (etype, size)

  def readSetBegin(self):
    self._stripSeparators()
    self.reader.read()
    etypeStr = self.readString()
    etype = self.typeMap[etypeStr]
    size = self.readI32()
    return (etype, size)

  def readBool(self):
    self._stripSeparators()
    quoted = self.reader.peek() == '"'
    if quoted:
      self.reader.read()
    buff = self.reader.read()
    ret = buff[0].lower() == "t"
    burn = 3 if ret else 4
    burn = burn + int(quoted)
    self.reader.read(burn)
    return ret

  def _getInt(self):
    self._stripSeparators()
    buff = [self.reader.read()]
    quoted = buff[0] == '"'
    if quoted:
      buff[0] = self.reader.read()
    while self.reader.peek() in self.INTEGRAL:
      buff.append(self.reader.read())
    if quoted:
      self.reader.read()
    return int("".join(buff)) if buff else ""

  readByte = readI16 = readI32 = readI64 = _getInt

  def readDouble(self):
    self._stripSeparators()
    buff = [self.reader.read()]
    quoted = buff[0] == '"'
    if quoted:
      buff[0] = self.reader.read()
    while self.reader.peek() in self.NUMERIC:
      buff.append(self.reader.read())
    if quoted:
      self.reader.read()
    return float("".join(buff)) if buff else ""

  def readString(self):
    self._stripSeparators()
    buff = self.reader.read()
    while self.reader.peek() != '"':
      buff = "".join([buff, self.reader.read()])
    self.reader.read()
    return buff.strip('"')


class TJSONProtocolFactory:
  def __init__(self, strictRead=False, strictWrite=True):
    self.strictRead = strictRead
    self.strictWrite = strictWrite

  def getProtocol(self, trans):
    prot = TJSONProtocol(trans, self.strictRead, self.strictWrite)
    return prot

