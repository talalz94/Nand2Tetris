import sys
import os

#Help taken to understand the system arguments
#Logic understood and syntax help taken from Michael Ries Youtube videos, projects on Github and Nand2tetris project forums

KEYWORDS = ["CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT","BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO", "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"]
SYMBOLS = ['(', ')', '[', ']', '{', '}', ',', ';', '=', '.', '+', '-', '*', '/', '&', '|', '~', '<', '>']
WHITE_SPACE = [' ', '\n', '\t']
Type1 = ["STATIC", "FIELD"]
Type2 = ["CONSTRUCTOR", "FUNCTION","METHOD", "VOID"]
Type3 = ["TRUE", "FALSE", "NULL", "THIS"]
Type4 = ["INT", "CHAR", "BOOLEAN", "VOID"]
Op1 = ['+', '-', '*', '/', '&', '|','<', '>', '=']
Op2 = ['-', '~']

#Takes in a jack file and assigns tokens to each character or set of characters
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
		while self._tokenIsKeyword() and self.mytokens.keyWord() == "VAR":
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

		if self.mytokens.tokenType() == "SYMBOL" and self.mytokens.symbol() == '.':
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

		if self._tokenIsKeyword() and self.mytokens.keyWord() == "ELSE":
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

def main():
        myFile = sys.argv[1]
        compileFile(myFile)

def compileFile(myPath):
	print("Compiling........")
	JackCompilationEngine(myPath, repExtension(myPath))


def repExtension(myinput):
	return myinput.replace(".jack", ".xml") #replaces the extension

if __name__ == '__main__':
	main()
