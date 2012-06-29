/**
 *  bool        Boolean, one byte
 *  byte        Signed byte
 *  i16         Signed 16-bit integer
 *  i32         Signed 32-bit integer
 *  i64         Signed 64-bit integer
 *  double      64-bit floating point value
 *  string      String
 *  binary      Blob (byte array)
 *  map<t1,t2>  Map from one type to another
 *  list<t1>    Ordered list of one type
 *  set<t1>     Set of unique elements of one type
 */

typedef i32 MyInteger

const i32 INT32CONSTANT = 9853
const map<string,string> MAPCONSTANT = {'hello':'world', 'goodnight':'moon'}

enum Operation {
  ADD = 1,
  SUBTRACT = 2,
  MULTIPLY = 3,
  DIVIDE = 4
}

struct Work {
  1: i32 num1 = 0,
  2: i32 num2,
  3: Operation op,
  4: optional string comment,
}

union Num {
	1: i32 num1 = 0,
	2: double num2 = 0
}

union Biggun {
  1: bool mybool,
  2: byte mybyte,
  3: i16 myi16,
  4: i32 myi32,
  5: i64 myi64,
  6: double mydouble,
  7: string mystring,
  8: list<i16> mylist,
  9: set<bool> myset,
  10: map<string, double> mymap,
  11: string myunicode,
  12: Operation myenum,
  13: Work mystruct
}

exception InvalidOperation {
  1: i32 what,
  2: string why
}



service Calculator {
   Num echo(1:Num n),

   void clear(1:Num n), 

   Biggun echoBig(1:Biggun b),

   void clearBig(1:Biggun b),

   /**
    * This method has a oneway modifier. That means the client only makes
    * a request and does not listen for any response at all. Oneway methods
    * must be void.
    */
   oneway void zip()

}

