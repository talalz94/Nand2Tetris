import sys
import os

#Help taken to understand the system arguments
#Logic understood and syntax help taken from Michael Ries Youtube videos, projects on Github and Nand2tetris project forums
# Most part of the code has been made by taking different elements from solution online and merging those together.
#This does not convert all  jack files in the directory. we will have to convert each file one by one.

KEYWORDS = ["CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT","BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"]
SYMBOLS = ['(', ')', '[', ']', '{', '}', ',', ';', '=', '.', '+', '-', '*', '/', '&', '|', '~', '<', '>']
WHITE_SPACE = [' ', '\n', '\t']
Type1 = ["STATIC", "FIELD"]
Type2 = ["CONSTRUCTOR", "FUNCTION","METHOD", "VOID"]
Type3 = ["TRUE", "FALSE", "NULL", "THIS"]
Type4 = ["INT", "CHAR", "BOOLEAN", "VOID"]
Op1 = ['+', '-', '*', '/', '&', '|','<', '>', '=']
Op2 = ['-', '~']

class JackTokenizer:
	def __init__(self, filename):
		self.file = open(filename, 'r')
		self.currentToken = ""
		if self.hasMoreTokens():
			self.advance()
	#checks if there are any more tokens
	def hasMoreTokens(self):
		while True:
			if self.check() == "":
				return False

			while self.check() in WHITE_SPACE:
				self.file.read(1)
			# Checks for comments:
			i = self.check(2)
			while i in ["//", "/*"]:
				if self.check(2) == "//":
					self.file.readline()
				else:				
					self.skipComment()
				i = self.check(2)

			if self.check() not in WHITE_SPACE:
				return True

	def advance(self):
		'''Gets the next token from the input and makes it the current token. Called if hasMoreTokens is true.'''
		if self.hasMoreTokens():
			if self.check() != '"':
				self.currentToken = self.checkWord()
				self.file.read(len(self.currentToken))
			else:
				string_const = self.file.read(1) # Opening "
				while self.check() != '"':
					string_const = string_const + self.file.read(1)
				string_const = string_const + self.file.read(1) # Closing "

				self.currentToken = string_const
	
	#returns what type of token it has been given		
	def tokenType(self):
		token = self.currentToken.upper()
		if token in SYMBOLS:
			return "SYMBOL"
		if token in KEYWORDS:
			return "KEYWORD"
		if '"' in token:
			return "STRING_CONST"
		if token.isdigit():
			return "INT_CONST"

		return "IDENTIFIER"

	def keyWord(self):
		'''when type is keyword returns type of the keyword'''
		return self.currentToken.upper()

	def symbol(self):
		''' Returns the character which is the current token. should be called only when tokenType is Symbol'''
		return self.currentToken[0]

	def identifier(self):
		''' Returns the identifier which is the current token. Should only be called when tokentype is Identifier'''
		return self.currentToken

	def intVal(self):
		'''REturns the Integer Value of the curent token. Should be called only when token type is INT_CONST'''
		return int(self.currentToken) #need to convert type

	def stringVal(self):
		'''Returns the strign value of the current token, without the double quotes. Should be called if tokenType is STRING_CONST'''
		return self.currentToken.replace('"', '')

	def check(self, charCount=1):
		currentPos = self.file.tell()
		c = self.file.read(charCount)
		self.file.seek(currentPos)
		return c

	def skipComment(self):
		#ignores the commented out part in a code
		#doesn't work if I write the code there for some reason so I had to make a function
		star = False # Did we find a possible end?
		while True:
			char = self.file.read(1)
			if char == '*':
				# We have found a candidate for the comment ending.
				star = True
			else:
				# If the character is a '/', and we have found a '*' in the
				# previous iteration, we are done.
				if star == True and char == '/':
					return
				# But if not, we check for a line break. 
				# (Just in case the '/' got broken into the next line.)
				if char != '\n':
					star = False

	def checkWord(self):
		i = ""
		currentPos = self.file.tell() #returns current position of the read/write pointer
		currentChar = self.file.read(1)
		if currentChar in SYMBOLS:
			i = currentChar
		else:
			while (currentChar != "") and (currentChar not in WHITE_SPACE):
				if currentChar in SYMBOLS:
					break
				i = i + currentChar
				currentChar = self.file.read(1)
		self.file.seek(currentPos)
		return i

class JackCompilationEngine():
	def __init__(self, input_file, output_file):
		'''Creates a new compilation engine with the given input and output.'''
		self.mytokens = JackTokenizer(input_file)
		self.output = open(output_file, 'w')
		self.indentLevel = 0 #after every section begins or ends this changes to get a proper parse tree
		self.compileClass()	#not sure why. The project implementation proposal in the lecture slides say so
		self.output.close()

	def compileClass(self):
		'''Compiles a complete class'''
		self._startSection("class")
		self._writeKeyword()    
		self._writeIdentifier()
		self._writeSymbol()     

		if self.mytokens.keyWord() in Type1: #checks if it is static or field
			self.compileClassVarDec()

		while (self.mytokens.keyWord() in Type2): #checks what kind of a function it is
			self.compileSubroutine()

		self._writeSymbol()    
		self._endSection("class")   

	def compileClassVarDec(self):
		'''Compiles a static declaraton or a field declaration'''
		while ( self._tokenIsKeyword() and (self.mytokens.keyWord() == "STATIC" or self.mytokens.keyWord() == "FIELD")):
			self._startSection("classVarDec")
			self._writeKeyword()        
			self._writeType()           
			self._writeIdentifier()     

			
			while self.mytokens.symbol() == ',':
				self._writeSymbol()
				self._writeIdentifier() 

			self._writeSymbol()         
			self._endSection("classVarDec")


	def compileSubroutine(self):
		'''Compiles a method, function or constructor'''
		self._startSection("subroutineDec")
		self._writeKeyword()        # Constructor/Function/Method

		self._writeType()           

		self._writeIdentifier()     
		self.compileParameterList() 

		# Body:
		self._startSection("subroutineBody")
		self._writeSymbol()         # '{'

		if self.mytokens.keyWord() == "VAR":
			self.compileVarDec() 

		if not (self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() =='}'):
			self.compileStatements()
		self._writeSymbol()        
		self._endSection("subroutineBody")

		self._endSection("subroutineDec")


	def compileParameterList(self):
		'''Compiles a list of arguments if there are any'''
		self._writeSymbol()                
		self._startSection("parameterList")

		while self.mytokens.symbol() != ')':
			self._writeKeyword()            
			self._writeIdentifier()         
			if self.mytokens.symbol() == ',':
				self._writeSymbol()

		self._endSection("parameterList")   # ')'
		self._writeSymbol()


	def compileVarDec(self):
		'''For variable declaration'''
		while (self._tokenIsKeyword() and self.mytokens.keyWord() == "VAR"):
			self._startSection("varDec")
			self._writeKeyword()    # "Var"
			self._writeType()       # Var. type
			self._writeIdentifier() # Var name

			# Are there more variables in the same line?
			while self.mytokens.symbol() == ',':
				self._writeSymbol()
				self._writeIdentifier() # Variable name.

			self._writeSymbol() # ';' symbol at the end of the line.
			self._endSection("varDec")
		

	def compileStatements(self):
		'''compiles a sequence of statements'''
		self._startSection("statements")

		while not ( self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() == '}'):
			if self.mytokens.keyWord() == "LET":
				self.compileLet()
		
			elif self.mytokens.keyWord() == "RETURN":
				self.compileReturn()

			elif self.mytokens.keyWord() == "DO":
				self.compileDo()

			elif self.mytokens.keyWord() == "IF":
				self.compileIf()

			elif self.mytokens.keyWord() == "WHILE":
				self.compileWhile()

		self._endSection("statements")

	#compile the statements their names define
	def compileDo(self):
		self._startSection("doStatement")
		self.indentLevel = self.indentLevel + 1

		self._writeKeyword()        # "Do"
		self._writeIdentifier()     # Subroutine name/(class/var):

		if (self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() == '.'):
			self._writeSymbol()     
			self._writeIdentifier() 

		self.compileExpressionList()

		self._writeSymbol()         

		if self.indentLevel > 0:
			self.indentLevel = self.indentLevel - 1
		self._endSection("doStatement")


	def compileLet(self):
		self._startSection("letStatement")

		# "Let":
		self._writeKeyword()
		# Variable name:
		self._writeIdentifier()

		if self.mytokens.symbol() == '[':
			self._writeSymbol()        
			self.compileExpression()    
			self._writeSymbol()         

		self._writeSymbol()             
		self.compileExpression()

		self._writeSymbol() #';'
		self._endSection("letStatement")

	def compileWhile(self):
		self._startSection("whileStatement")

		self._writeKeyword()        
		self._writeSymbol()         
		self.compileExpression()   
		self._writeSymbol()         

		self._writeSymbol()        
		self.compileStatements()
		self._writeSymbol()         

		self._endSection("whileStatement")

	def compileReturn(self):
		self._startSection("returnStatement")

		self._writeKeyword()

		if not ( self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() == ';'):
			self.compileExpression()


		self._writeSymbol()
		self._endSection("returnStatement")


	def compileIf(self):
		self._startSection("ifStatement")
		self._writeKeyword()            
		self._writeSymbol()             
		self.compileExpression()        
		self._writeSymbol()             

		self._writeSymbol()             
		self.compileStatements()        
		self._writeSymbol()            

		if (self._tokenIsKeyword() and self.mytokens.keyWord() == "ELSE"):
			self._writeKeyword()        
			self._writeSymbol()         
			self.compileStatements()    
			self._writeSymbol()         

		self._endSection("ifStatement")

	def compileExpression(self):
		self._startSection("expression")
		self.compileTerm()

		while (self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() in Op1):
			self._writeSymbol()
			self.compileTerm()

		self._endSection("expression")

	def compileTerm(self):
		''' Compiles a term. If the current token is an identifier, the routine must distinguish between a variable, an array entry, and a subroutine call'''
		self._startSection("term")
		tokenType = self.mytokens.tokenType()

		if (self._tokenIsKeyword() and self.mytokens.keyWord() in Type3):  # keywordConstant
			self._writeKeyword()

		elif tokenType == "INT_CONST":      # integerConstant
			self._writeIntVal()

		elif tokenType == "STRING_CONST":   # stringConstant
			self._writeStringVal()

		elif tokenType == "IDENTIFIER":     # variable Name
			self._writeIdentifier()
			if (self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() == '['):  
				self._writeSymbol() 
				self.compileExpression()
				self._writeSymbol() 

			elif (self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() == '('): 
				self._writeSymbol()
				self.compileExpressionList()
				self._writeSymbol()
	
			elif (self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() == '.'):
				self._writeSymbol()
				self._writeIdentifier()
				self.compileExpressionList()

		elif (self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() == '('): 
			self._writeSymbol() 
			self.compileExpression()
			self._writeSymbol() 

		elif (self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() in Op2):  
			self._writeSymbol()
			self.compileTerm()

		self._endSection("term")

	def compileExpressionList(self):
		''' compiles a comma separated lsit of expressions'''
		self._writeSymbol() # '('
		self._startSection("expressionList")

		while not ( self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() == ')'):
			self.compileExpression()
			if (self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() == ','):
				self._writeSymbol()

		self._endSection("expressionList")
		self._writeSymbol() # ')'

	#all the writing helper functions which will be used to compile
	def _writeKeyword(self):
		space = ' ' * 2 * self.indentLevel
		self.output.write(space + "<keyword> " + self.mytokens.keyWord().lower() + " </keyword>" + '\n')
		self.mytokens.advance()

	def _writeIdentifier(self):
		space = ' ' * 2 * self.indentLevel
		self.output.write(space + "<identifier> " + self.mytokens.identifier() + " </identifier>" + '\n')
		self.mytokens.advance()        

	def _writeSymbol(self):
		symbol = self.mytokens.symbol()
		if symbol == '"':
			symbol = "&quot;"
		if symbol == '&':
			symbol = "&amp;"
		elif symbol == '<':
			symbol = "&lt;"
		elif symbol == '>':
			symbol = "&gt;"


		space = ' ' * 2 * self.indentLevel
		self.output.write(space + "<symbol> " + symbol + " </symbol>" + '\n')
		self.mytokens.advance()

	def _writeIntVal(self):
		space = ' ' * 2 * self.indentLevel
		self.output.write(space + "<integerConstant> "+ str(self.mytokens.intVal())+ " </integerConstant>" + '\n')
		self.mytokens.advance()        

	def _writeStringVal(self):
		space = ' ' * 2 * self.indentLevel
		self.output.write(space + "<stringConstant> "+ self.mytokens.stringVal()+ " </stringConstant>" + '\n')
		self.mytokens.advance()

	def _writeType(self):
		if (self._tokenIsKeyword() and self.mytokens.keyWord() in Type4):
			self._writeKeyword()
		else:
			self._writeIdentifier()

	#checks if it is a keyword or not
	def _tokenIsKeyword(self):
		return self.mytokens.tokenType() == "KEYWORD"


	#these two show the beginning and ending of sections in the parse tree
	def _startSection(self, piece):
		space = ' ' * 2 * self.indentLevel
		self.output.write(space + "<" + piece + ">" + '\n')
		self.indentLevel = self.indentLevel + 1

	def _endSection(self, piece):
		if self.indentLevel > 0:
			self.indentLevel = self.indentLevel - 1
		space = ' ' * 2 * self.indentLevel
		self.output.write(space + "</" + piece + ">" + '\n') 

class JacktoVM():
	def __init__(self, in_filename, out_filename):
		self.mytokens = JackTokenizer(in_filename)

		self._label_index = 0
		self._if_index = 0
		self._while_index = 0

		self.globalDict 	= {}
		self.localDict		= {}

		self.GStatIndex = 0
		self.GFieldIndex = 0
		self.LArgIndex = 0
		self.LVarIndex = 0

		self.outfile = open(out_filename, 'w')


		# Start compilation:
		self.compileClass()

	def startSubroutine(self):
		self.localDict.clear()
		self.LArgIndex = 0
		self.LVarIndex = 0

	def define(self, name, jackType, kind):
		kind = kind.upper()
		if kind == "STATIC":
			self.globalDict[name] = (jackType, kind, self.GStatIndex)
			self.GStatIndex += 1
		elif kind == "FIELD":
			self.globalDict[name] = (jackType, kind, self.GFieldIndex)
			self.GFieldIndex += 1
		elif kind == "ARG":
			self.localDict[name] = (jackType, kind, self.LArgIndex)
			self.LArgIndex += 1
		elif kind == "LOCAL":
			self.localDict[name] = (jackType, kind, self.LVarIndex)
			self.LVarIndex += 1

	def varCount(self, kind):
		kind = kind.upper()
		res = 0
		for (symbol, info) in self.localDict.items():
			if info[1] == kind:
				res += 1
		for (symbol, info) in self.globalDict.items():
			if info[1] == kind:
				res += 1

		return res

	def writePush(self, segment, index):
		self.outfile.write("push %s %d\n" % (segment.lower(), index))

	def writePop(self, segment, index):
		self.outfile.write("pop %s %d\n" % (segment.lower(), index))

	def writeArithmetic(self, command):
		if command == '+':
			self.outfile.write("add")
		elif command == '-':
			self.outfile.write("sub")
		elif command == '*':
			self.outfile.write("call Math.multiply 2")
		elif command == '/':
			self.outfile.write("call Math.divide 2")
		elif command == '&':
			self.outfile.write("and")
		elif command == '|':
			self.outfile.write("or")
		elif command == '<':
			self.outfile.write("lt")
		elif command == '>':
			self.outfile.write("gt")
		elif command == '=':
			self.outfile.write("eq")
		elif command == '~':
			self.outfile.write("not")
		elif command == 'neg': # Unary
			self.outfile.write("neg")
		self.outfile.write('\n')

	def writeLabel(self, label):
		self.outfile.write("label %s\n" % label)

	def writeGoto(self, label):
		self.outfile.write("goto %s\n" % label)

	def writeIf(self, label):
		self.outfile.write("if-goto %s\n" % label)

	def writeCall(self, name, nArgs):
		self.outfile.write("call %s %d\n" % (name, nArgs))

	def writeFunction(self, name, nLocals):
		self.outfile.write("function %s %d\n" % (name, nLocals))

	def writeReturn(self):
		self.outfile.write("return\n")

	def writeAlloc(self, size):
		self.writePush("CONSTANT", size)
		self.outfile.write("call Memory.alloc 1\n")

	def writeString(self, string):
		self.writePush("CONSTANT", len(string))
		self.writeCall("String.new", 1)
		for char in string:
			unicode_rep = ord(char)
			self.writePush("CONSTANT", unicode_rep)
			self.writeCall("String.appendChar", 2)

	def compileClass(self):
		self._getKeyword()    # "Class"
		self._class_name = self._getIdentifier() #  className
		self._getSymbol()     # '{'

		# Variable declarations:
		if self.mytokens.keyWord() in ["STATIC", "FIELD"]:
			self.compileClassVarDec()

		# Class' subroutines declarations:
		while (self.mytokens.keyWord() in ["CONSTRUCTOR", "FUNCTION",
											"METHOD", "VOID"]):
			self.compileSubroutine()

		self._getSymbol()     # '}'

	def compileClassVarDec(self):
		# While there are lines declaring variables... (There could be 0.)
		while (self._tokenMatchesKeyword("STATIC") or
			   self._tokenMatchesKeyword("FIELD")):
			var_kind = self._getKeyword()        # "static"/"field"
			var_type = self._getType()           # Var. type
			var_name = self._getIdentifier()     # Var. name

			self._defineVar(var_name, var_type, var_kind)

			# Are there more variables in the same line?
			while self.mytokens.symbol() == ',':
				self._getSymbol()
				var_name = self._getIdentifier() # Var. name
				self._defineVar(var_name, var_type, var_kind)


			self._getSymbol()         # ';' symbol at the end of the line.

	def compileSubroutine(self):
		self.startSubroutine()

		subroutine_type = self._getKeyword()	# Constructor/Function/Method
		return_type = self._getType()           # Return type
		subroutine_name = self._getIdentifier()	# Subroutine name

		# A method will receive a pointer as the first argument,
		# we reserve index 0 for it.
		if subroutine_type == "METHOD":
			self._defineVar("this_ptr", "INT", "ARG")

		self.compileParameterList()				# Parameters (may be empty)


		# Subroutine body:
		self._getSymbol()         # '{'

		local_vars = 0
		if self.mytokens.keyWord() == "VAR":
			local_vars = self.compileVarDec()

		call_name = self._class_name + "." + subroutine_name
		self.writeFunction(call_name, local_vars)

		if subroutine_type == "METHOD":
			# Argument 0 of a constructor is the this pointer.
			# The first thing the function does is move it to the pointer register.
			self.writePush("ARGUMENT", 0)
			self.writePop("POINTER", 0)

		elif subroutine_type == "CONSTRUCTOR":
			# If it is a method, invoke the OS functions to allocate space.
			self.writeAlloc(self.varCount("FIELD"))
			# Then we set the this pointer to the assigned space.
			self.writePop("POINTER", 0)


		if not self._tokenMatchesSymbol('}'):
			self.compileStatements()
		self._getSymbol()         # '}'
		# End of subroutine body.


		# If the return type is void, we need to push some value.
		# That way the caller can always pop at least one value.
		if return_type == "VOID":
			self.writePush("constant", 0)
		self.writeReturn()

	def compileParameterList(self):
		self._getSymbol()	# '('

		while self.mytokens.symbol() != ')':
			var_type = self._getKeyword()            # Type
			var_name = self._getIdentifier()         # Name
			self._defineVar(var_name, var_type, "ARG")

			# More parameters?
			if self.mytokens.symbol() == ',':
				self._getSymbol()

		self._getSymbol()	# ')'


	def compileVarDec(self):
		vars_declared = 0
		# While there are lines declaring variables... (There could be 0.)
		while self._tokenMatchesKeyword("VAR"):
			self._getKeyword()    				# "Var"
			var_type = self._getType()			# Var. type
			var_name = self._getIdentifier()	# Var. name

			self._defineVar(var_name, var_type, "LOCAL")
			vars_declared +=1

			# Are there more variables in the same line?
			while self.mytokens.symbol() == ',':
				self._getSymbol()
				var_name = self._getIdentifier()
				self._defineVar(var_name, var_type, "LOCAL")
				vars_declared +=1

			self._getSymbol() # ';' symbol at the end of the line.
		return vars_declared


	def compileStatements(self):
		while not self._tokenMatchesSymbol('}'):
			if self.mytokens.keyWord() == "LET":
				self.compileLet()

			elif self.mytokens.keyWord() == "RETURN":
				self.compileReturn()

			elif self.mytokens.keyWord() == "DO":
				self.compileDo()

			elif self.mytokens.keyWord() == "IF":
				self.compileIf()

			elif self.mytokens.keyWord() == "WHILE":
				self.compileWhile()

	def compileDo(self):
		self._getKeyword()        			# "Do"
		name = self._getIdentifier()    	# Subroutine name/(class/var)
		self._writeSubroutineCall(name, returns_void = True)
		self._getSymbol()         # ';'

	def compileLet(self):
		self._getKeyword() # "Let"
		var_name = self._getIdentifier() # Variable name

		array = False
		if self.mytokens.symbol() == '[':
			array = True

			self._writeVarPush(var_name)
			self._getSymbol()         	#'['
			self.compileExpression()    # expr
			self._getSymbol()         	#']'
			self.writeArithmetic('+')
			self.writePop("POINTER", 1) # Push to the THAT pointer.

		self._getSymbol()             	# '='
		self.compileExpression()

		if array:
			self.writePop("THAT", 0)
		else:
			self._writeVarPop(var_name)

		self._getSymbol() #';'

	def compileWhile(self):
		self._while_index += 1

		while_begin_label = "W%d" % self._while_index
		while_end_label = "Wend%d" % self._while_index

		self.writeLabel(while_begin_label)

		self._getKeyword()        	# "While"
		self._getSymbol()         	# '('
		self.compileExpression()	# condition
		self._getSymbol()         	# ')'

		# While guard. Negating it and making a goto in case its false:
		self.writeArithmetic("~")
		self.writeIf(while_end_label)

		self._getSymbol()         # '{'
		self.compileStatements()
		self._getSymbol()         # '}'
		self.writeGoto(while_begin_label)

		self.writeLabel(while_end_label)

	def compileReturn(self):
		self._getKeyword() # "Return"

		if not self._tokenMatchesSymbol(';'):
			self.compileExpression() # If there is an expression, compile it.

		self._getSymbol() #';'

	def compileIf(self):
		self._if_index += 1

		self._getKeyword()            	# "If"
		self._getSymbol()             	# '('
		self.compileExpression()		# condition
		self._getSymbol()             	# ')'
		self.writeArithmetic("~")

		false_label 	= "ifF%d" % self._if_index
		true_label 		= "ifT%d" % self._if_index
		end_if_label 	= "ifEnd%d" % self._if_index

		self.writeIf(false_label)

		self._getSymbol()             	# '{'
		self.writeLabel(true_label)
		self.compileStatements()        # (...)
		self.writeGoto(end_if_label)
		self._getSymbol()             	# '}'

		self.writeLabel(false_label)
		if self._tokenMatchesKeyword("ELSE"):
			self._getKeyword()        	# "Else"
			self._getSymbol()         	# '{'
			self.compileStatements()	# (...)r
			self._getSymbol()         	# '}'

		self.writeLabel(end_if_label)

	def compileExpression(self):
		self.compileTerm()

		while self._tokenIsOperator():
			command = self._getSymbol()
			self.compileTerm()
			self.writeArithmetic(command)

	def compileTerm(self):
		tokenType = self.mytokens.tokenType()
		var_kind = "NONE"

		if self._tokenIsKeywordConstant():  # keywordConstant
			kw = self._getKeyword()
			if kw == "FALSE" or kw == "NULL":
				self.writePush("constant", 0)
			elif kw == "TRUE":	# -1 in two's complement.
				self.writePush("constant", 0)
				self.writeArithmetic("~")
			elif kw == "THIS":
				self.writePush("pointer", 0)

		elif tokenType == "INT_CONST":      # integerConstant
			self.writePush("constant", self._getIntVal())


		elif tokenType == "STRING_CONST":   # stringConstant
			string = self._getStringVal()
			self.writeString(string)


		elif tokenType == "IDENTIFIER":     # varName
			var_name = self._getIdentifier()
			if var_name in self.localDict:
				var_kind = self.localDict[var_name][1]
			if var_name in self.globalDict:
				var_kind = self.globalDict[var_name][1]


			# Is it an array?
			self._writeVarPush(var_name)
			if self._tokenMatchesSymbol('['):   # '[' expression']'
				self._getSymbol() # '['
				self.writePush("POINTER", 1) # Save the current THAT pointer
				self.writePop("TEMP", 0)	# into TEMP0.
				self.compileExpression()
				# Adding the expression to the previously loaded base pointer:
				self.writeArithmetic('+')
				self.writePop("POINTER", 1)
				self.writePush("THAT", 0) # Deferefencing into TEMP1.
				self.writePop("TEMP", 1)
				# Re-establish THAT pointer.
				self.writePush("TEMP", 0)
				self.writePop("POINTER", 1)

				self.writePush("TEMP", 1) # Push result.
				self._getSymbol() # ']'

			# Is it a subroutine call?
			elif self._tokenMatchesSymbol('('): # '(' expression ')'
				self._writeSubroutineCall(var_name)
			# Is it a method call?
			elif self._tokenMatchesSymbol('.'):
				self._writeSubroutineCall(var_name)

			#else:
				#self._writeVarPush(var_name)

		elif self._tokenMatchesSymbol('('): # '(' Expression ')'
			self._getSymbol() # '('
			exp = self.compileExpression()
			self._getSymbol() # ')'

		elif self._tokenIsUnaryOperator():  # unaryOp term
			symbol = self._getSymbol()
			self.compileTerm()
			if symbol == '-':
				symbol = 'neg'
			self.writeArithmetic(symbol)

	def compileExpressionList(self):
		self._getSymbol() # '('

		number_of_expressions = 0
		# While there are expressions...
		while not self._tokenMatchesSymbol(')'):
			exp = self.compileExpression()
			number_of_expressions += 1

			if self._tokenMatchesSymbol(','):
				self._getSymbol()

		self._getSymbol() # ')'
		return number_of_expressions

	# --- PRIVATE functions --- #
	def _getKeyword(self):
		keyword = self.mytokens.keyWord()
		self.mytokens.advance()
		return keyword

	def _getIdentifier(self):
		identifier = self.mytokens.identifier()
		self.mytokens.advance()
		return identifier

	def _getSymbol(self):
		symbol = self.mytokens.symbol()
		self.mytokens.advance()
		return symbol

	def _getIntVal(self):
		int_val = self.mytokens.intVal()
		self.mytokens.advance()
		return int_val

	def _getStringVal(self):
		string_val = self.mytokens.stringVal()
		self.mytokens.advance()
		return string_val

	def _getType(self):
		if self._tokenIsPrimitiveType():
			return self._getKeyword()
		else:
			return self._getIdentifier()

	def _tokenIsKeyword(self):
		return self.mytokens.tokenType() == "KEYWORD"

	def _tokenIsSymbol(self):
		return self.mytokens.tokenType() == "SYMBOL"

	def _tokenMatchesSymbol(self, symbol):
		return self._tokenIsSymbol() and self.mytokens.symbol() == symbol

	def _tokenMatchesKeyword(self, kw):
		return self._tokenIsKeyword() and self.mytokens.keyWord() == kw

	def _tokenIsOperator(self):
		return(self._tokenIsSymbol() and
			   self.mytokens.symbol() in ['+', '-', '*', '/', '&', '|',
											'<', '>', '='])
	def _tokenIsUnaryOperator(self):
		return(self._tokenIsSymbol() and
			   self.mytokens.symbol() in ['-', '~'])

	def _tokenIsPrimitiveType(self):
		return(self._tokenIsKeyword() and
			   self.mytokens.keyWord() in ["INT", "CHAR", "BOOLEAN", "VOID"])

	def _tokenIsKeywordConstant(self):
		return(self._tokenIsKeyword() and
			   self.mytokens.keyWord() in ["TRUE", "FALSE", "NULL", "THIS"])

	def _defineVar(self, name, varType, kind):
		var_kind = "NONE"
		if name in self.localDict:
			var_kind = self.localDict[name][1]
		if name in self.globalDict:
			var_kind = self.globalDict[name][1]

		if var_kind == "NONE":
			self.define(name, varType, kind)

	def _writeVarPush(self, var_name):
		''' Writes the operations to push a variable depending on its kind. '''
		var_kind = "NONE"
		if var_name in self.localDict:
			var_kind = self.localDict[var_name][1]
		if var_name in self.globalDict:
			var_kind = self.globalDict[var_name][1]

		if var_kind == "NONE":
			return

		var_index = ""
		if var_name in self.localDict:
			var_index = self.localDict[var_name][2]
		if var_name in self.globalDict:
			var_index = self.globalDict[var_name][2]
			
		if var_kind == "FIELD":
			self.writePush("THIS", var_index)
		elif var_kind == "STATIC":
			self.writePush("STATIC", var_index)
		elif var_kind == "LOCAL":
			self.writePush("LOCAL", var_index)
		elif var_kind == "ARG":
			self.writePush("ARGUMENT", var_index)

	def _writeVarPop(self, var_name):
		''' Writes the operations to pop a variable depending on its kind. '''
		var_kind = "NONE"
		if var_name in self.localDict:
			var_kind = self.localDict[var_name][1]
		if var_name in self.globalDict:
			var_kind = self.globalDict[var_name][1]

		if var_kind == "NONE":
			return

		var_index = ""
		if var_name in self.localDict:
			var_index = self.localDict[var_name][2]
		if var_name in self.globalDict:
			var_index = self.globalDict[var_name][2]

		if var_kind == "FIELD":
			self.writePop("THIS", var_index)
		elif var_kind == "STATIC":
			self.writePop("STATIC", var_index)
		elif var_kind == "LOCAL":
			self.writePop("LOCAL", var_index)
		elif var_kind == "ARG":
			self.writePop("ARGUMENT", var_index)

	def _writeSubroutineCall(self, name, returns_void = False):
		call_name = ""
		method_name = ""
		push_pointer = False
		kind = ""
		t= ""

		if self._tokenMatchesSymbol('.'): 	# Method call.
			self._getSymbol()     # '.'
			method_name = self._getIdentifier()

		if method_name == "":
			# Implicit class, equivalent to "self.method()".
			# Appending the current/local class name to the function,
			# and pushing the "this" pointer.
			push_pointer = True
			self.writePush("POINTER", 0)
			call_name = "%s.%s" % (self._class_name, name)
		else:
			if name in self.localDict:
				kind = self.localDict[name][1]
			if name in self.globalDict:
				kind = self.globalDict[name][1]

			if kind == "NONE": # "name" is a class: call it directly.
				call_name = "%s.%s" % (name, method_name)
			else:
				if name in self.localDict:
					t= self.localDict[name][0]
				if name in self.globalDict:
					t = self.globalDict[name][0] # Get the variable's class.
				call_name = "%s.%s" % (t, method_name)
				push_pointer = True # Push the location to which the variable points.
				self._writeVarPush(name)

		number_of_parameters = self.compileExpressionList()

		if push_pointer:
			number_of_parameters +=1

		self.writeCall(call_name, number_of_parameters)

		if returns_void: # Void functions return 0. We ignore that value.
			self.writePop("TEMP", 0)

def main():
        myFile = sys.argv[1]
        compileFile(myFile)

def compileFile(myPath):
	print("Compiling........")
	JacktoVM(myPath, repExtension(myPath))


def repExtension(myinput):
	return myinput.replace(".jack", ".vm") #replaces the extension

if __name__ == '__main__':
	main()