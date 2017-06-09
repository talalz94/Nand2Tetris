import sys
import os

#The logic for this code if pretty much already given in the project guideline and lecture slides.
#I am not well aware regarding the Object oriented syntax in python so a lot of the code has been made by taking help from the internet and peers who know about they syntax

class Parser(object):
    def __init__(self, filename):
        file = open(filename, 'r')
        self.file = file.readlines()
        self.command = ''
        self.current_line = 0
    
    def check(self):
        if bool(self.file) == True:
            return True
        pass

    def next(self):
        if self.check()== True:    
            self.command = self.file.pop(0).strip()

    def commandType(self):
        if self.command[0] == "@":
            return 0 #for A command
        elif self.command[0] == "(":
            return 1 #for L command
        else:
            return 2 #for C command

    def symbol(self):
        if self.command[0] =="@":
            return self.command[1:]
        elif self.command[0] == "(":
            return self.command[1:-1]
        else:
            return "null"

    def dest(self):
        if self.commandType() == 2:
            if '=' in self.command:
                a = self.command.find('=')
                return self.command[:a]
            else:
                return "null"

    def comp(self):
        if self.commandType() == 2:
            a = self.command.find('=')
            b = self.command.find(';')
           
            if a!=-1 and b == -1:
                return self.command[a+1:]
            elif a== -1 and b!=-1:
                return self.command[:b]
            elif a!= -1 and b!=-1:
                return self.command[a+1:b]
            

    def jump(self):
        if self.commandType() == 2:
            if ';' in self.command:
                a = self.command.find(';')
                return self.command[a+1:a+4]
            else:
                return "null"
    
class Binary(object):
    
    def __init__(self):
        #all the codes are given in the book Chapter 6
        self.dest_codes={"null":"000","M":"001","D":"010","MD":"011", 
                    "A":"100","AM":"101","AD":"110","AMD":"111"} 
        self.comp_codes = {'0':'0101010', '1':'0111111', '-1':'0111010', 'D':'0001100',
            'A':'0110000', '!D':'0001101', '!A':'0110001', '-D':'0001111',
            '-A':'0110011', 'D+1':'0011111','A+1':'0110111','D-1':'0001110',
            'A-1':'0110010','D+A':'0000010','D-A':'0010011','A-D':'0000111',
            'D&A':'0000000','D|A':'0010101','M':'1110000', '!M':'1110001',
            '-M':'1110011', 'M+1':'1110111','M-1':'1110010','D+M':'1000010',
            'D-M':'1010011','M-D':'1000111','D&M':'1000000', 'D|M':'1010101'}
        self.jump_codes = {'null':'000', 'JGT':'001', 'JEQ':'010', 'JGE':'011',
                      'JLT':'100', 'JNE':'101', 'JLE':'110', 'JMP':'111'}


    def dest(self, mnemonic):
        return self.dest_codes[mnemonic]

    def comp(self, mnemonic):
        return self.comp_codes[mnemonic]

    def jump(self, mnemonic):
        return self.jump_codes[mnemonic]


class SymbolTable(object):
    #all the codes are given in the book Chapter 6
    def __init__(self):
        self.Table = {'SP': 0, 'LCL':1, 'ARG':2, 'THIS':3, 'THAT':4,
            'R0':0, 'R1':1, 'R2':2, 'R3':3, 'R4':4, 'R5':5, 'R6':6, 'R7':7,
            'R8':8, 'R9':9, 'R10':10, 'R11':11, 'R12':12, 'R13':13, 'R14':14,
            'R15':15, 'SCREEN':16384, 'KBD':24576}

    def add(self, symbol, address):
        self.Table[symbol] = address


    def inTable(self, symbol):
        return symbol in self.Table


    def getAddress(self, symbol):
        
        return self.Table.get(symbol)


def main():
    a = ""
    counter = -1
    index = 16
    filename = input("Enter filename:")
    myfile = open(filename,"r")
    tempname = filename[:-4] + "temp.txt"
    tempfile = open(tempname , "w")
    for line in myfile:
        a = ""
        for letter in line:
            if letter != '\t' and letter != ' ':
                a = a + letter
        i = 0
        if '/' in a:
            n = a.find('/')
            a = a.replace(a[n:], '\n')
        while i < len(a) and a[0] != '\n':
            tempfile.write(a[i])
            i = i + 1
    
    tempfile.close()
    myfile.close()
    table = SymbolTable()
    parser = Parser(tempname)
    code = Binary()
    while parser.check()==True:
        parser.next()
        counter = counter + 1
        if parser.commandType()==1:
            table.add(parser.symbol(),counter)
            counter = counter - 1         
    final = ""      
    parser = Parser(tempname)    
    
    position = 16
    hacknew = filename[:-4] + ".hack"
    hackfile = open(hacknew,"w")
    while parser.check()==True:
        parser.next()
        if parser.commandType()==2:
            dest = code.dest(parser.dest())
            comp = code.comp(parser.comp())
            jump = code.jump(parser.jump())
            final = "111" + comp + dest + jump
            hackfile.write(final + "\n")
            
        elif parser.commandType()==0:
            if table.inTable(parser.symbol())==True:
                
                x = bin(int(table.getAddress(parser.symbol())))[2:]
            else:
                if parser.symbol().isdigit()==True:
                    x = bin(int(parser.symbol()))[2:]
                else:
                    if table.inTable(parser.symbol()) == False:
                        table.add(parser.symbol(),position)
                        x = bin(position)[2:]
                        position = position + 1
                    else:
                        x =bin(table.getAddress(parser.symbol()))[2:]
                
            hackfile.write(x.zfill(16) + "\n")
            
    hackfile.close()
    os.remove(tempname)
    
if __name__ == "__main__":
    main()

