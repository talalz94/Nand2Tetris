import sys
import string
from pathlib import Path
import os
import re
import glob


#Runs all the ".vm" files in the directory where this file is present!

class Parser(object):


    def __init__(self, fname):
        # Opens the vm file for reading
        with open(fname) as f: 
            self.lines = f.readlines()

        # Converts the content of the file into a list of lines
        self.lines = [x.strip() for x in self.lines]

        #Keeps track of current line.
        self.currentline=-1

    #Command Types stored in a dictionary
    cmdtype = {'push':'C_PUSH', 'pop':'C_POP', 'add':'C_ARITHMETIC', 'sub':'C_ARITHMETIC', 'neg':'C_ARITHMETIC',
                             'eq' :'C_ARITHMETIC', 'gt' :'C_ARITHMETIC', 'lt' :'C_ARITHMETIC',
                             'and':'C_ARITHMETIC', 'or' :'C_ARITHMETIC', 'not':'C_ARITHMETIC',
                             'call':'C_CALL',      'return':'C_RETURN',  'function':'C_FUNCTION',
                             'label':'C_LABEL',    'goto':'C_GOTO',      'if-goto':'C_IF'
                              }

    arg2types = ['C_PUSH', 'C_POP', 'C_FUNCTION', 'C_CALL']
    

    # Checks whether there are more commands to execute
    def hasMoreCommands(self):

        return ((self.currentline ) < (len(self.lines)- 1))


    # Makes the next command the current command
    def advance(self):


            if self.hasMoreCommands():

                self.currentline += 1

                
   
            if (self.commandCheck(self.lines[self.currentline])):
                
                self.advance()


    # Returns the type of command based on the first word of the VM instruction
    def commandType(self):

       
        if (len(self.lines[self.currentline].split())) == 1:
            
            return self.cmdtype[(self.lines[self.currentline])]

        else:
            
            return self.cmdtype[(self.lines[self.currentline].split(' ', 1)[0])]

        pass


    # Returns the first argument of the command    
    def arg1(self):
        if self.commandType()!= 'C_RETURN':
            if self.commandType() == 'C_ARITHMETIC':
                    return (self.lines[self.currentline])
            else:
                return self.lines[self.currentline].split(' ', 2)[1]

    # Returns the second argument of the instruction
    def arg2(self):

        if self.commandType() in self.arg2types:

            return self.lines[self.currentline].split(' ', 3)[2]

    # Returns the first two commands of the code 
    def arg3(self):
        if self.commandType()!= 'C_RETURN':
            if self.commandType() != 'C_ARITHMETIC':
                return (str.rsplit(self.lines[self.currentline], ' ', 1))

        


    #Clears comments, blank lines and errors.
    def commandCheck(self,command):

        return ((command.split(' ', 1)[0]) not in self.cmdtype)
        
class CodeWriter(object):

    def __init__(self, fname):

        # Opens the output asm file for writing
        self.jmpseq = 0
        self.file = open(((fname.rsplit('.', 1)[0]) + ".asm") ,"w")



    # Dictionary containing all the stack commands.
    
    stackcmd = {'push constant' :  '@T' + '\n'
                                'D=A' + '\n'
                                '@SP' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'M=M+1' + '\n',
             'push argument' :  '@T' + '\n'
                                'D=A' + '\n'
                                '@ARG' + '\n'
                                'A=D+M' + '\n'
                                'D=M' + '\n'
                                '@SP' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'M=M+1' + '\n',
             'push local' :     '@X' + '\n'
                                'D=A' + '\n'
                                '@LCL' + '\n'
                                'A=D+M' + '\n'
                                'D=M' + '\n'
                                '@SP' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'M=M+1' + '\n',
             'push static' :    '@T' + '\n'
                                'D=A' + '\n'
                                '@16' + '\n'
                                'A=D+A' + '\n'
                                'D=M' + '\n'
                                '@SP' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'M=M+1' + '\n',
             'push this' :      '@T' + '\n'
                                'D=A' + '\n'
                                '@THIS' + '\n'
                                'A=D+M' + '\n'
                                'D=M' + '\n'
                                '@SP' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'M=M+1' + '\n',
             'push that' :      '@T' + '\n'
                                'D=A' + '\n'
                                '@THAT' + '\n'
                                'A=D+M' + '\n'
                                'D=M' + '\n'
                                '@SP' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'M=M+1' + '\n',
             'push pointer' :   '@T' + '\n'
                                'D=A' + '\n'
                                '@3' + '\n' 
                                'A=D+A' + '\n'
                                'D=M' + '\n'
                                '@SP' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'M=M+1' + '\n', 
             'push temp' :      '@T' + '\n'
                                'D=A' + '\n'
                                '@5' + '\n'
                                'A=D+A' + '\n'
                                'D=M' + '\n'
                                '@SP' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'M=M+1' + '\n',
             'pop argument' :   '@T' + '\n'
                                'D=A' + '\n'
                                '@ARG' + '\n'
                                'D=D+M' + '\n'
                                '@R5' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'AM=M-1' + '\n'
                                'D=M' + '\n'
                                '@R5' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n',
             'pop local' :      '@T' + '\n'
                                'D=A' + '\n'
                                '@LCL' + '\n'
                                'D=D+M' + '\n'
                                '@R5' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'AM=M-1' + '\n'
                                'D=M' + '\n'
                                '@R5' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n',
             'pop static' :     '@T' + '\n'
                                'D=A' + '\n'
                                '@16' + '\n'
                                'D=D+A' + '\n'
                                '@R5' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'AM=M-1' + '\n'
                                'D=M' + '\n'
                                '@R5' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n',
             'pop this' :       '@T' + '\n'
                                'D=A' + '\n'
                                '@R3' + '\n'
                                'D=D+M' + '\n'
                                '@R5' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'AM=M-1' + '\n'
                                'D=M' + '\n'
                                '@R5' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n',
             'pop that' :       '@T' + '\n'
                                'D=A' + '\n'
                                '@R4' + '\n'
                                'D=D+M' + '\n'
                                '@R5' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'AM=M-1' + '\n'
                                'D=M' + '\n'
                                '@R5' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n',
             'pop pointer' :    '@T' + '\n'
                                'D=A' + '\n'
                                '@3' + '\n'
                                'D=D+A' + '\n'
                                '@R5' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'AM=M-1' + '\n'
                                'D=M' + '\n'
                                '@R5' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n',
             'pop temp' :       '@T' + '\n'
                                'D=A' + '\n'
                                '@5' + '\n'
                                'D=D+A' + '\n'
                                '@R5' + '\n'
                                'M=D' + '\n'
                                '@SP' + '\n'
                                'AM=M-1' + '\n'
                                'D=M' + '\n'
                                '@R5' + '\n'
                                'A=M' + '\n'
                                'M=D' + '\n',
             'add' :    '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'D=M' + '\n'
                        'M=0' + '\n'
                        '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'M=D+M' + '\n'
                        '@SP' + '\n'
                        'M=M+1' + '\n',                                    
             'sub' :    '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'D=M' + '\n'
                        'M=0' + '\n'
                        '@R5' + '\n'
                        'M=D' + '\n'
                        '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'D=M' + '\n'
                        '@R5' + '\n'
                        'D=D-M' + '\n'
                        '@SP' + '\n'
                        'A=M' + '\n'
                        'M=D' + '\n'
                        '@SP' + '\n'
                        'M=M+1' + '\n'
                        '@R5' + '\n'
                        'M=0' + '\n',
             'neg' :    '@32767' + '\n'
                        'D=A' + '\n'
                        '@SP' + '\n'
                        'A=M-1' + '\n'
                        'M=D-M' + '\n'
                        'M=M+1' + '\n',
              'eq' :    '@RUN_J' + '\n'
                        '0;JMP' + '\n'
                        '(TRUE_J)' + '\n'
                        '@SP' + '\n'
                        'A=M' + '\n'
                        'M=-1' + '\n'
                        '@EQ_J' + '\n'
                        '0;JMP' + '\n'
                        '(RUN_J)' + '\n'
                        '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'D=M' + '\n'
                        'M=0' + '\n'
                        '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'D=D-M' + '\n'
                        'M=0' + '\n'
                        '@TRUE_J' + '\n'
                        'D;JEQ' + '\n'
                        '@SP' + '\n'
                        'A=M' + '\n'
                        'M=0' + '\n'
                        '(EQ_J)' + '\n'
                        '@SP' + '\n'
                        'M=M+1' + '\n',
             'gt' :     '@RUN_J' + '\n'
                        '0;JMP' + '\n'
                        '(TRUE_J)' + '\n'
                        '@SP' + '\n'
                        'A=M' + '\n'
                        'M=-1' + '\n'
                        '@EQ_J' + '\n'
                        '0;JMP' + '\n'
                        '(RUN_J)' + '\n'
                        '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'D=M' + '\n'
                        'M=0' + '\n'
                        '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'D=D-M' + '\n'
                        'M=0' + '\n'
                        '@TRUE_J' + '\n'
                        'D;JLT' + '\n'
                        '@SP' + '\n'
                        'A=M' + '\n'
                        'M=0' + '\n'
                        '(EQ_J)' + '\n'
                        '@SP' + '\n'
                        'M=M+1' + '\n',
             'lt' :     '@RUN_J' + '\n'
                        '0;JMP' + '\n'
                        '(TRUE_J)' + '\n'
                        '@SP' + '\n'
                        'A=M' + '\n'
                        'M=-1' + '\n'
                        '@EQ_J' + '\n'
                        '0;JMP' + '\n'
                        '(RUN_J)' + '\n'
                        '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'D=M' + '\n'
                        'M=0' + '\n'
                        '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'D=D-M' + '\n'
                        'M=0' + '\n'
                        '@TRUE_J' + '\n'
                        'D;JGT' + '\n'
                        '@SP' + '\n'
                        'A=M' + '\n'
                        'M=0' + '\n'
                        '(EQ_J)' + '\n'
                        '@SP' + '\n'
                        'M=M+1' + '\n',
             'and' :    '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'D=M' + '\n'
                        'M=0' + '\n'
                        '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'M=D&M' + '\n'
                        '@SP' + '\n'
                        'M=M+1' + '\n',
             'or' :     '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'D=M' + '\n'
                        'M=0' + '\n'
                        '@SP' + '\n'
                        'AM=M-1' + '\n'
                        'M=D|M' + '\n'
                        '@SP' + '\n'
                        'M=M+1' + '\n',
             'not' :    '@SP' + '\n'
                        'A=M-1' + '\n'
                        'M=!M' + '\n'
            }

    

    # Generates the asm code
    def codeGenerator(self, cmdtype, arg1, arg2, arg3):

        if cmdtype == 'C_ARITHMETIC':
            
            self.writeArithmatic(arg1)

        else:
            self.writePushPop(arg3)

            
    # Writes the Arthimatic part of the asm code        
    def writeArithmatic(self, arg1): 

        if arg1 in ['add', 'sub', 'or', 'not', 'and', 'neg']:
                    asmcode = self.stackcmd[arg1]
                    self.file.write(asmcode)
                    
        elif arg1 in ['eq', 'gt', 'lt']:
            asmcode = self.stackcmd[arg1]
            asmcode = string.replace(asmcode, '_J', '_' + str(self.jmpseq))
            self.file.write(asmcode)
            self.jmpseq += 1

    # Writes the Push and Pop equivalent of asm code.        
    def writePushPop(self, arg3):

        if arg3[0] in self.stackcmd:
            asmcode = self.stackcmd[arg3[0]]
            asmcode = str.replace(asmcode, 'T', arg3[1])
            self.file.write(asmcode)
        
    # Writes the end code and closes the file.
    def fileClose(self):
        self.file.write('(END)\n' +\
                    '@END\n' +\
                    '0;JMP')
        self.file.close() 

    



    
def main():

    # Opens up all the ".vm" files in the directory.
    for file in glob.glob("*.vm"):

        
        p=Parser(file)
        d=CodeWriter(file)

        # Runs for all the lines in the ".vm" file.
        while (p.hasMoreCommands() == True):

            p.advance()
            
            d.codeGenerator(p.commandType(), p.arg1(), p.arg2(), p.arg3())

            

    d.fileClose()
    
if __name__ == "__main__":
    main()
