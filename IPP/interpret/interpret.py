# Projekt do predmetu IPP (VUT FIT)
# Autor: Peter Kapicak (xkapic02)

import sys
import getopt
import lexsynControl
import re
import codecs

# globalne premenne pre ramce, zasobnik ramcov, zasobik volani, datovy zasobnik, programovy citac a navestia

globalFrame = {}
tempFrame = {'undefined':'undefined'}
localFrameStack = []

labels = {}
callStack = []
dataStack = []
progCounter = 0

# -------------------------------------------------------------------------------------
# ------------------------------  POMOCNE FUNKCIE  ------------------------------------
# -------------------------------------------------------------------------------------
''' Kontrola existencie ramca a premennej
        variable - kontrolovana premenna
        vracia [G,F,T] podla toho, v ktorom ramci sa premenna nachadza, inak chyba
'''
def variableControl(variable):
    global localFrameStack
    global tempFrame
    global globalFrame
    regex = r"^[G,L,T]"
    match = re.match(regex, variable)

    if match.group() == 'L' and len(localFrameStack) > 0:
        if variable in localFrameStack[-1]:
            return 'L'
        else:
            sys.stderr.write('CHYBA: JUMPIFEQ: Premenna neexistuje\n')
            sys.exit(54)

    elif match.group() == 'T' and 'undefined' not in tempFrame:
        if variable in tempFrame:
            return 'T'
        else:
            sys.stderr.write('CHYBA: JUMPIFEQ: Premenna neexistuje\n')
            sys.exit(54)
    elif match.group() == 'G':
        if variable in globalFrame:
            return 'G'
        else:
            sys.stderr.write('CHYBA: JUMPIFEQ: Premenna neexistuje\n')
            sys.exit(54)
    else:
        sys.stderr.write('CHYBA: JUMPIFEQ: Ramec neexistuje\n')
        sys.exit(55)
''' Kontrola ci je <symbol> premenna alebo konstanta
        progList - zoznam instrukcii
        vracia zoznam s dvomi operandmi, inak chyba
'''
def operandsControl(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    symb1 = ()
    symb2 = ()

    if progList[progCounter]['arg2'][0] == 'var':
        result = variableControl(progList[progCounter]['arg2'][1])
        
        if result == 'L':
            symb1 = localFrameStack[-1][progList[progCounter]['arg2'][1]]
        elif result == 'T':
            symb1 = tempFrame[progList[progCounter]['arg2'][1]]
        else:
            symb1 = globalFrame[progList[progCounter]['arg2'][1]]

        if len(symb1) == 0:
            sys.stderr.write('CHYBA: Neinicializovana premenna\n')
            sys.exit(56)
    else:
        symb1 = progList[progCounter]['arg2']

    if progList[progCounter]['arg3'][0] == 'var':
        result = variableControl(progList[progCounter]['arg3'][1])
    
        if result == 'L':
            symb2 = localFrameStack[-1][progList[progCounter]['arg3'][1]]
        elif result == 'T':
            symb2 = tempFrame[progList[progCounter]['arg3'][1]]
        else:
            symb2 = globalFrame[progList[progCounter]['arg3'][1]]

        if len(symb2) == 0:
            sys.stderr.write('CHYBA: Neinicializovana premenna\n')
            sys.exit(56)
    else:
        symb2 = progList[progCounter]['arg3']

    operands = [symb1,symb2]
    return operands
# -------------------------------------------------------------------------------------
#           Funkcie vykonavanie jednotlivych instrukcii jazyka IPPcode18
# -------------------------------------------------------------------------------------

def createFrame(progList):
    global tempFrame
    tempFrame = {}
# -------------------------------------------------------------------------------------
def pushFrame(progList):
    global tempFrame
    global localFrameStack
    if 'undefined' in tempFrame:
        sys.stderr.write('CHYBA: pristup k nedefinovanemu TF\n')
        sys.exit(55)
    else:
        if len(tempFrame) > 0: 
            # nahrada docasneho ramca za lokalny v nazve premennej
            regex = r"^TF"
            for tVar in tempFrame:
                lVar = re.sub(regex, 'LF', tVar)
                tempFrame[lVar] = tempFrame.pop(tVar)
        localFrameStack.append(tempFrame)
        tempFrame = {}
        tempFrame = {'undefined':'undefined'}
# -------------------------------------------------------------------------------------
def popFrame(progList):
    global tempFrame
    global localFrameStack
    if len(localFrameStack) == 0:
        sys.stderr.write('CHYBA: Zasobnik lokalnych ramcov je prazdny\n')
        sys.exit(55)
    else:
        tempFrame = {}
        tempFrame = localFrameStack.pop()
        # nahrada lokalneho ramca za doacany v nazve premennej
        regex = r"^LF"
        for lVar in tempFrame:
            tVar = re.sub(regex, 'TF', lVar)
            tempFrame[tVar] = tempFrame.pop(lVar)
# -------------------------------------------------------------------------------------
def defvarInstr(progList):
    global globalFrame
    global localFrameStack
    global progCounter
    
    isLocal = True
    isTemp = True
    
    if len(localFrameStack) == 0:
        isLocal = False
    if 'undefined' in tempFrame:
        isTemp = False

    regex = r"^[G,L,T]"

    match = re.match(regex, progList[progCounter]['arg1'][1])
    # kontrola existencie ramcov a redefinicie premennej
    if match.group() == 'G':
        if progList[progCounter]['arg1'][1] in globalFrame:
            sys.stderr.write('CHYBA: Redefinicia premennej\n')
            sys.exit(59)
        else:
            globalFrame[progList[progCounter]['arg1'][1]] = ()
    elif match.group() == 'L':
        if isLocal:
            if progList[progCounter]['arg1'][1] in localFrameStack[-1]:
                sys.stderr.write('CHYBA: Redefinicia premennej\n')
                sys.exit(59)
            else:
                localFrameStack[-1][progList[progCounter]['arg1'][1]] = ()
        else:
            sys.stderr.write('CHYBA: Ramec neexistuje\n')
            sys.exit(55)
    elif match.group() == 'T':
        if isTemp:
            if progList[progCounter]['arg1'][1] in tempFrame:
                sys.stderr.write('CHYBA: Redefinicia premennej\n')
                sys.exit(59)
            else:
                tempFrame[progList[progCounter]['arg1'][1]] = ()
        else:
            sys.stderr.write('CHYBA: Ramec neexistuje\n')
            sys.exit(55)
# -------------------------------------------------------------------------------------
def labelInstr(progList):
    pass
# -------------------------------------------------------------------------------------
def jumpInstr(progList):
    global progCounter
    if progList[progCounter]['label'] in labels:
        # treba dekrementovat hodnotu citaca pretoze cyklus na vykonavanie instrukcii inkrementuje citac 
        progCounter = int(labels[progList[progCounter]['label']]) - 1 
    else:
        sys.stderr.write('CHYBA: JUMP: Navestie neexistuje\n')
        sys.exit(52)
# -------------------------------------------------------------------------------------
def compareJumpInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack

    isVar1 = False
    isVar2 = False
    symb1 = ()
    symb2 = ()

    # overenie spravnosti operandov pre porovnanie
    if progList[progCounter]['arg2'][0] == 'var':
        variable1 = progList[progCounter]['arg2'][1]
        result = variableControl(variable1)
        isVar1 = True

        if result == 'G':
            symb1 = globalFrame[variable1]

        elif result == 'L':
            symb1 = localFrameStack[-1][variable1]

        else:
            symb1 = tempFrame[variable1]
        
        if len(symb1) == 0:
            sys.stderr.write('CHYBA: JUMPIFEQ: Neinicializovana premenna\n')
            sys.exit(56)
            

    if progList[progCounter]['arg3'][0] == 'var':
        variable2 = progList[progCounter]['arg3'][1]
        result = variableControl(variable2)
        isVar2 = True

        if result == 'G':
            symb2 = globalFrame[variable2]

        elif result == 'L':
            symb2 = localFrameStack[-1][variable2]

        else:
            symb2 = tempFrame[variable2]

        if len(symb2) == 0:
            sys.stderr.write('CHYBA: JUMPIFEQ: Neinicializovana premenna\n')
            sys.exit(56)

    if not isVar1:
        symb1 = progList[progCounter]['arg2']
    if not isVar2:
        symb2 = progList[progCounter]['arg3']
    
    # kontrola zhodnoti datovy typov porovnavanych hodnot
    if symb1[0] == symb2[0]:
        if progList[progCounter]['opcode'] == 'JUMPIFEQ': # vetva pre JUMPIFEQ
            if symb1[1] == symb2[1]:
                if progList[progCounter]['label'] not in labels:
                    sys.stderr.write('CHYBA: JUMPIFEQ: Navestie neexistuje\n')
                    sys.exit(52)
                progCounter = int(labels[progList[progCounter]['label']]) - 1

        elif progList[progCounter]['opcode'] == 'JUMPIFNEQ':# vetva pre JUMPIFNEQ
            if symb1[1] != symb2[1]:
                if progList[progCounter]['label'] not in labels:
                    sys.stderr.write('CHYBA: JUMPIFEQ: Navestie neexistuje\n')
                    sys.exit(52)
                progCounter = int(labels[progList[progCounter]['label']]) - 1
                
    else:
        sys.stderr.write('CHYBA: JUMPIFEQ: zle typy operandov\n')
        sys.exit(53)
# ------------------------------------------------------------------------------------- 
def moveInstr(progList):
    global globalFrame
    global tempFrame
    global localFrameStack

    symb = ()

    # kontrola operandu, ktory sa mam priradit do premennej
    if progList[progCounter]['arg2'][0] == 'var':
        result = variableControl(progList[progCounter]['arg2'][1])
        if result == 'L':
            symb = localFrameStack[-1][progList[progCounter]['arg2'][1]]
        elif result == 'T':
            symb = tempFrame[progList[progCounter]['arg2'][1]]
        else:
            symb = globalFrame[progList[progCounter]['arg2'][1]]
        if len(symb) == 0:
            sys.stderr.write('CHYBA: MOVE: Neinicializovana premenna\n')
            sys.exit(56)
    else:
        symb = progList[progCounter]['arg2']

    # overenie, ci premenna existuje
    result2 = variableControl(progList[progCounter]['arg1'][1])

    if result2 == 'L':
        localFrameStack[-1][progList[progCounter]['arg1'][1]] = symb
    elif result2 == 'T':
        tempFrame[progList[progCounter]['arg1'][1]] = symb
    else:
        globalFrame[progList[progCounter]['arg1'][1]] = symb 
# ------------------------------------------------------------------------------------- 
def callInstr(progList):
    global progCounter
    global labels
    global callStack

    if progList[progCounter]['label'] not in labels:
        sys.stderr.write('CHYBA: CALL: Navestie neexistuje\n')
        sys.exit(52)
    else:
        callStack.append(progCounter+1)
        progCounter = int(labels[progList[progCounter]['label']]) - 1 # programovy citac sa v cykle inkrementuje, preto -1 aby nepreskocil instrukciu
# -------------------------------------------------------------------------------------
def returnInstr(progList):
    global callStack
    global progCounter

    if len(callStack) == 0:
        sys.stderr.write('CHYBA: RETURN: Zasobnik volani je prazdny\n')
        sys.exit(56)
    progCounter = callStack.pop() -1 # programovy citac sa v cykle inkrementuje, preto -1 aby nepreskocil instrukciu
# -------------------------------------------------------------------------------------
def pushsInstr(progList):
    global globalFrame
    global tempFrame
    global localFrameStack
    global dataStack

    symb = ()

    if progList[progCounter]['arg1'][0] == 'var':
        result = variableControl(progList[progCounter]['arg1'][1])
        if result == 'L':
            symb = localFrameStack[-1][progList[progCounter]['arg1'][1]]
        elif result == 'T':
            symb = tempFrame[progList[progCounter]['arg1'][1]]
        else:
            symb = globalFrame[progList[progCounter]['arg1'][1]]
        if len(symb) == 0:
            sys.stderr.write('CHYBA: PUSHS: Neinicializovana premenna\n')
            sys.exit(56)
    else:
        symb = progList[progCounter]['arg1']

    # ak je operand korektny, tak sa ulozi na vrchol datoveho zasobnika
    dataStack.append(symb)
# -------------------------------------------------------------------------------------
def popsInstr(progList):
    global globalFrame
    global tempFrame
    global localFrameStack
    global dataStack

    result = variableControl(progList[progCounter]['arg1'][1])

    if len(dataStack) == 0:
        sys.stderr.write('CHYBA: POPS: Datovy zasobnik je prazdny\n')
        sys.exit(56)

    # vybratie hodnoty z vrcholu zasobnika a ulozenie do premennej 
    if result == 'L':
        localFrameStack[-1][progList[progCounter]['arg1'][1]] = dataStack.pop()
    elif result == 'T':
        tempFrame[progList[progCounter]['arg1'][1]] = dataStack.pop()
    else:
        globalFrame[progList[progCounter]['arg1'][1]] = dataStack.pop()
# -------------------------------------------------------------------------------------
def binaryOperationInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    operands = operandsControl(progList)

    symb1 = operands[0]
    symb2 = operands[1]

    res = ()
    # operandy musia byt typu int
    if symb1[0] == 'int' and symb2[0] == 'int':
        # instrukcia ADD
        if progList[progCounter]['opcode'] == 'ADD':
            symb1 = ('int', int(symb1[1])+int(symb2[1]))
            res = ('int', int(symb1[1]))
        # instrukcia SUB
        elif progList[progCounter]['opcode'] == 'SUB':
            symb1 = ('int', int(symb1[1])-int(symb2[1]))
            res = ('int', int(symb1[1]))
        # instrukcia MUL
        elif progList[progCounter]['opcode'] == 'MUL':
            symb1 = ('int', int(symb1[1])*int(symb2[1]))
            res = ('int', int(symb1[1]))
        # instrukcia IDIV
        elif progList[progCounter]['opcode'] == 'IDIV':
            if int(symb2[1]) == 0:
                sys.stderr.write('CHYBA: Delenie nulou\n')
                sys.exit(57)

            symb1 = ('int', int(symb1[1])/int(symb2[1]))
            res = ('int', int(symb1[1]))

    else:
        sys.stderr.write('CHYBA: Oba operandy musia byt integer\n')
        sys.exit(53)

    destVar = variableControl(progList[progCounter]['arg1'][1])
    # ulozenie vysledku do premennej
    if destVar == 'L':
        localFrameStack[-1][progList[progCounter]['arg1'][1]] = res
    elif destVar == 'T':
        tempFrame[progList[progCounter]['arg1'][1]] = res
    else:
        globalFrame[progList[progCounter]['arg1'][1]] = res
# -------------------------------------------------------------------------------------
def relationOperationInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    operands = operandsControl(progList)

    symb1 = operands[0]
    symb2 = operands[1]

    isTrue = False # ostava False ak vysledok operacie je nepravdivy, inak True

    # operandy musia mat rovnaky typ
    if symb1[0] == symb2[0]:
        if symb1[0] == 'int' and symb2[0] == 'int':
            if progList[progCounter]['opcode'] == 'LT':
                if int(symb1[1]) < int(symb2[1]):
                    isTrue = True
            elif progList[progCounter]['opcode'] == 'GT':
                if int(symb1[1]) > int(symb2[1]):
                    isTrue = True
            elif progList[progCounter]['opcode'] == 'EQ':
                if int(symb1[1]) == int(symb2[1]):
                    isTrue = True

        elif symb1[0] == 'bool' and symb2[0] == 'bool':
            if progList[progCounter]['opcode'] == 'LT':
                if symb1[1] == 'false' and symb2[1] == 'true':
                    isTrue = True
            elif progList[progCounter]['opcode'] == 'GT':
                if symb1[1] == 'true' and symb2[1] == 'false':
                    isTrue = True
            elif progList[progCounter]['opcode'] == 'EQ':
                if symb1[1] == symb2[1]:
                    isTrue = True

        elif symb1[0] == 'string' and symb2[0] == 'string':
            if progList[progCounter]['opcode'] == 'LT':
                if symb1[1] < symb2[1]:
                    isTrue = True
            elif progList[progCounter]['opcode'] == 'GT':
                if symb1[1] > symb2[1]:
                    isTrue = True
            elif progList[progCounter]['opcode'] == 'EQ':
                if symb1[1] == symb2[1]:
                    isTrue = True
    else:
        sys.stderr.write('CHYBA: Oba operandy musia byt rovnakeho typu\n')
        sys.exit(53)

    # ulozenie vysledku operacie do premennej
    result = variableControl(progList[progCounter]['arg1'][1])
    if result == 'L':
        if isTrue:
            localFrameStack[-1][progList[progCounter]['arg1'][1]] = ('bool','true')
        else:
            localFrameStack[-1][progList[progCounter]['arg1'][1]] = ('bool','false')

    elif result == 'T':
        if isTrue:
            tempFrame[progList[progCounter]['arg1'][1]] = ('bool','true')
        else:
            tempFrame[progList[progCounter]['arg1'][1]] = ('bool','false')

    else:
        if isTrue:
            globalFrame[progList[progCounter]['arg1'][1]] = ('bool','true')
        else:
            globalFrame[progList[progCounter]['arg1'][1]] = ('bool','false')
    
# -------------------------------------------------------------------------------------
def andOrInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    operands = operandsControl(progList)

    symb1 = operands[0]
    symb2 = operands[1]

    # ostava False, ak je vysledok logickej operacie nepravda, inak True
    isTrue = False

    # oba operandy pre logicke operacie musia byt bool
    if symb1[0] == 'bool' and symb2[0] == 'bool':
        # instrukcia AND
        if progList[progCounter]['opcode'] == 'AND':
            if symb1[1] == 'true' and symb2[1] == 'true':
                isTrue = True
        # instrukcia OR
        if progList[progCounter]['opcode'] == 'OR':
            if symb1[1] == 'false' and symb2[1] == 'false':
                pass
            else:
                isTrue = True
    else:
        sys.stderr.write('CHYBA: Oba operandy musia byt rovnakeho typu\n')
        sys.exit(53)

    result = variableControl(progList[progCounter]['arg1'][1])
    if result == 'L':
        if isTrue:
            localFrameStack[-1][progList[progCounter]['arg1'][1]] = ('bool','true')
        else:
            localFrameStack[-1][progList[progCounter]['arg1'][1]] = ('bool','false')

    elif result == 'T':
        if isTrue:
            tempFrame[progList[progCounter]['arg1'][1]] = ('bool','true')
        else:
            tempFrame[progList[progCounter]['arg1'][1]] = ('bool','false')
    else:
        if isTrue:
            globalFrame[progList[progCounter]['arg1'][1]] = ('bool','true')
        else:
            globalFrame[progList[progCounter]['arg1'][1]] = ('bool','false')


# -------------------------------------------------------------------------------------
def notInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    symb1 = ()

    if progList[progCounter]['arg2'][0] == 'var':
        result = variableControl(progList[progCounter]['arg2'][1])
        
        if result == 'L':
            symb1 = localFrameStack[-1][progList[progCounter]['arg2'][1]]
        elif result == 'T':
            symb1 = tempFrame[progList[progCounter]['arg2'][1]]
        else:
            symb1 = globalFrame[progList[progCounter]['arg2'][1]]

        if len(symb1) == 0:
            sys.stderr.write('CHYBA: Neinicializovana premenna\n')
            sys.exit(56)
    else:
        symb1 = progList[progCounter]['arg2']

    if symb1[0] != 'bool':
        sys.stderr.write('CHYBA: Operand musi byt typy bool\n')
        sys.exit(53)

    result = variableControl(progList[progCounter]['arg1'][1])
    if result == 'L':
        if symb1[1] == 'false':
            localFrameStack[-1][progList[progCounter]['arg1'][1]] = ('bool','true')
        else:
            localFrameStack[-1][progList[progCounter]['arg1'][1]] = ('bool','false')

    elif result == 'T':
        if symb1[1] == 'false':
            tempFrame[progList[progCounter]['arg1'][1]] = ('bool','true')
        else:
            tempFrame[progList[progCounter]['arg1'][1]] = ('bool','false')
    else:
        if symb1[1] == 'false':
            globalFrame[progList[progCounter]['arg1'][1]] = ('bool','true')
        else:
            globalFrame[progList[progCounter]['arg1'][1]] = ('bool','false')    
# -------------------------------------------------------------------------------------
def int2CharInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    symb1 = ()

    # kontrola operandov
    if progList[progCounter]['arg2'][0] == 'var':
        result = variableControl(progList[progCounter]['arg2'][1])
        
        if result == 'L':
            symb1 = localFrameStack[-1][progList[progCounter]['arg2'][1]]
        elif result == 'T':
            symb1 = tempFrame[progList[progCounter]['arg2'][1]]
        else:
            symb1 = globalFrame[progList[progCounter]['arg2'][1]]

        if len(symb1) == 0:
            sys.stderr.write('CHYBA: Neinicializovana premenna\n')
            sys.exit(56)
    else:
        symb1 = progList[progCounter]['arg2']

    if symb1[0] != 'int':
        sys.stderr.write('CHYBA: Operand musi byt typy bool\n')
        sys.exit(53)

    # prevod cisla na znak
    toStr = ''
    try:
        toStr = chr(int(symb1[1]))
    except ValueError:
        sys.stderr.write('CHYBA: Nie je validna ordinalna hodnota znaku v Unicode\n')
        sys.exit(58)

    result = variableControl(progList[progCounter]['arg1'][1])
    if result == 'L':
        localFrameStack[-1][progList[progCounter]['arg1'][1]] = ('string',toStr)
    elif result == 'T':
        tempFrame[progList[progCounter]['arg1'][1]] = ('string',toStr)
    else:
        globalFrame[progList[progCounter]['arg1'][1]] = ('string',toStr)  
# -------------------------------------------------------------------------------------
def str2IntInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    operands = operandsControl(progList)

    symb1 = operands[0]
    symb2 = operands[1]

    if symb1[0] != 'string' or symb2[0] != 'int':
        sys.stderr.write('CHYBA: Nespravne typy operandov\n')
        sys.exit(53)

    if len(symb1[1]) <= int(symb2[1]):
        sys.stderr.write('CHYBA: Indexacia mimo retazec\n')
        sys.exit(58)

    toInt = ord(symb1[1][int(symb2[1])])

    result = variableControl(progList[progCounter]['arg1'][1])
    if result == 'L':
        localFrameStack[-1][progList[progCounter]['arg1'][1]] = ('int',toInt)
    elif result == 'T':
        tempFrame[progList[progCounter]['arg1'][1]] = ('int',toInt)
    else:
        globalFrame[progList[progCounter]['arg1'][1]] = ('int',toInt)  
# -------------------------------------------------------------------------------------
def replace(match):
    return chr(int(match.group(1)))
def writeInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    toPrint = ()

    if progList[progCounter]['arg1'][0] == 'var':
        result = variableControl(progList[progCounter]['arg1'][1])
        if result == 'L':
            toPrint = localFrameStack[-1][progList[progCounter]['arg1'][1]]
        elif result == 'T':
            toPrint = tempFrame[progList[progCounter]['arg1'][1]]
        else:
            toPrint = globalFrame[progList[progCounter]['arg1'][1]]

        if len(toPrint) == 0:
            sys.stderr.write('CHYBA: Neinicializovana premenna\n')
            sys.exit(56)
    else:
        toPrint = progList[progCounter]['arg1']

    if toPrint[0] == 'string':
        val = toPrint[1] 
        if (' ' in val) == True or ('#' in val) == True:
            sys.stderr.write('in string is space or #\n')
            sys.exit(32)
        regex = re.compile(r"\\(\d{1,3})")
        new = regex.sub(replace, val)   
        print(new)
    else:
        print(toPrint[1])

# -------------------------------------------------------------------------------------
def concatInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    operands = operandsControl(progList)
    symb1 = operands[0]
    symb2 = operands[1]

    concatRes = ''

    # kontrola spravnosti operandov a ich konkatenacia
    if symb1[0] == 'string' and symb2[0] == 'string':
        concatRes = symb1[1] + symb2[1]
    else:
        sys.stderr.write('CHYBA: Zle typy operandov\n')
        sys.exit(53)

    result = variableControl(progList[progCounter]['arg1'][1])

    if result == 'L':
        localFrameStack[-1][progList[progCounter]['arg1'][1]] = ('string', concatRes)
    elif result == 'T':
        tempFrame[progList[progCounter]['arg1'][1]] = ('string', concatRes)
    else:
        globalFrame[progList[progCounter]['arg1'][1]] = ('string', concatRes)
# -------------------------------------------------------------------------------------
def strlenInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    symb1 = ()
    length = 0

    if progList[progCounter]['arg2'][0] == 'var':
        result = variableControl(progList[progCounter]['arg2'][1])
        
        if result == 'L':
            symb1 = localFrameStack[-1][progList[progCounter]['arg2'][1]]
        elif result == 'T':
            symb1 = tempFrame[progList[progCounter]['arg2'][1]]
        else:
            symb1 = globalFrame[progList[progCounter]['arg2'][1]]

        if len(symb1) == 0:
            sys.stderr.write('CHYBA: Neinicializovana premenna\n')
            sys.exit(56)
    else:
        symb1 = progList[progCounter]['arg2']

    # zistenie dlzky retazca
    if symb1[0] == 'string':
        length = len(symb1[1])
    else:
        sys.stderr.write('CHYBA: Zly typ operandu\n')
        sys.exit(53)

    result = variableControl(progList[progCounter]['arg1'][1])

    if result == 'L':
        localFrameStack[-1][progList[progCounter]['arg1'][1]] = ('int', length)
    elif result == 'T':
        tempFrame[progList[progCounter]['arg1'][1]] = ('int', length)
    else:
        globalFrame[progList[progCounter]['arg1'][1]] = ('int', length)
# -------------------------------------------------------------------------------------
def getCharInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    operands = operandsControl(progList)

    symb1 = operands[0]
    symb2 = operands[1]

    if symb1[0] != 'string' or symb2[0] != 'int':
        sys.stderr.write('CHYBA: Nespravne typy operandov\n')
        sys.exit(53)

    # kontrola indexacie v retazci
    if len(symb1[1]) <= int(symb2[1]) or int(symb2[1]) < 0:
        sys.stderr.write('CHYBA: Indexacia mimo retazec\n')
        sys.exit(58)

    result = variableControl(progList[progCounter]['arg1'][1])

    if result == 'L':
        localFrameStack[-1][progList[progCounter]['arg1'][1]] = ('string', symb1[1][int(symb2[1])])
    elif result == 'T':
        tempFrame[progList[progCounter]['arg1'][1]] = ('string', symb1[1][int(symb2[1])])
    else:
        globalFrame[progList[progCounter]['arg1'][1]] = ('string', symb1[1][int(symb2[1])])
# -------------------------------------------------------------------------------------
def setCharInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    operands = operandsControl(progList)

    variable = progList[progCounter]['arg1']
    result = variableControl(variable[1])

    if result == 'L':
        var = localFrameStack[-1][progList[progCounter]['arg1'][1]]
    elif result == 'T':
        var = tempFrame[progList[progCounter]['arg1'][1]]
    else:
        var = globalFrame[progList[progCounter]['arg1'][1]]

    if len(var) == 0:
        sys.stderr.write('CHYBA: Neinicializovana premenna\n')
        sys.exit(56)

    symb1 = operands[0]
    symb2 = operands[1]

    if symb1[0] != 'int' or symb2[0] != 'string':
        sys.stderr.write('CHYBA: Nespravne typy operandov\n')
        sys.exit(53)

    # kontrola indexacie v retazci 
    if len(var[1]) <= int(symb1[1]) or int(symb1[1]) < 0:
        sys.stderr.write('CHYBA: Indexacia mimo retazec\n')
        sys.exit(58)

    if len(symb2[1]) == 0:
        sys.stderr.write('CHYBA: Prazdny retazec na nahradu\n')
        sys.exit(58)

    res = var[1]
    res.replace(res [int(symb1[1])], symb2[1][0])

    if result == 'L':
        localFrameStack[-1][progList[progCounter]['arg1'][1]] = res
    elif result == 'T':
        tempFrame[progList[progCounter]['arg1'][1]] = res
    else:
        globalFrame[progList[progCounter]['arg1'][1]] = res

# -------------------------------------------------------------------------------------
def typeInstr(progList):
    global globalFrame
    global tempFrame
    global localFrameStack
    global progCounter

    symb = ()
    res = ()

    if progList[progCounter]['arg1'][0] == 'var':
        result = variableControl(progList[progCounter]['arg1'][1])
        if result == 'L':
            symb = localFrameStack[-1][progList[progCounter]['arg1'][1]]
        elif result == 'T':
            symb = tempFrame[progList[progCounter]['arg1'][1]]
        else:
            symb = globalFrame[progList[progCounter]['arg1'][1]]
    else:
        symb = progList[progCounter]['arg1']

    if len(symb) == 0:
        res = ('string', '')
    else:
        res = ('string', symb[0])

    if result == 'L':
        localFrameStack[-1][progList[progCounter]['arg1'][1]] = res
    elif result == 'T':
        tempFrame[progList[progCounter]['arg1'][1]] = res
    else:
        globalFrame[progList[progCounter]['arg1'][1]] = res
# -------------------------------------------------------------------------------------
def readInstr(progList):
    global progCounter
    global globalFrame
    global localFrameStack
    global tempFrame

    symb1 = ()

    inpt = input()
   
    if progList[progCounter]['type'] == 'bool':
        if isinstance(inpt, bool) or inpt == 'true':
            symb1 = ('bool', 'true')
        else:
            symb1 = ('bool', 'false')
    elif progList[progCounter]['type'] == 'string':
        if isinstance(inpt, str):
            symb1 = ('string', inpt)
        else:
            symb1 = ('string', '')
    elif progList[progCounter]['type'] == 'int':
        if inpt.isdigit():
            if isinstance(int(inpt), int):
                symb1 = ('int', int(inpt))
            else:
                symb1 = ('int', 0)
            
        else:
            if (inpt[0] == '-' and inpt[1:].isdigit()):
                if isinstance(int(inpt), int):
                    symb1 = ('int', int(inpt))
                else:
                    symb1 = ('int', 0)
            else:
                symb1 = ('int', 0)


    result = variableControl(progList[progCounter]['arg1'][1])
        
    if result == 'L':
        localFrameStack[-1][progList[progCounter]['arg1'][1]] = symb1
    elif result == 'T':
        tempFrame[progList[progCounter]['arg1'][1]] = symb1
    else:
        globalFrame[progList[progCounter]['arg1'][1]] = symb1
# -------------------------------------------------------------------------------------
def dprintInstr(progList):
    global globalFrame
    global tempFrame
    global localFrameStack

    symb = ()

    if progList[progCounter]['arg1'][0] == 'var':
        result = variableControl(progList[progCounter]['arg1'][1])
        if result == 'L':
            symb = localFrameStack[-1][progList[progCounter]['arg1'][1]]
        elif result == 'T':
            symb = tempFrame[progList[progCounter]['arg1'][1]]
        else:
            symb = globalFrame[progList[progCounter]['arg1'][1]]
    else:
        symb = progList[progCounter]['arg1']

    sys.stderr.write('*************************************\n')
    sys.stderr.write('**********  LADIACI VYPIS  **********\n')
    sys.stderr.write(str(symb))
    sys.stderr.write('\n')
    sys.stderr.write('*************************************\n')
# -------------------------------------------------------------------------------------
def breakInstr(progList):
    global globalFrame
    global tempFrame
    global localFrameStack
    global progCounter

    sys.stderr.write('*************************************\n')
    sys.stderr.write('**********  LADIACI VYPIS  **********\n')
    sys.stderr.write('Pozicia v kode(cislo riadka) = ')  
    sys.stderr.write(str(progCounter+1)) 
    sys.stderr.write('\n')

    sys.stderr.write('OBSAH RAMCOV:\n')

    sys.stderr.write('  Globalny ramec:      ')
    sys.stderr.write(str(globalFrame))
    sys.stderr.write('\n')

    sys.stderr.write('  Docasny ramec ramec: ')
    sys.stderr.write(str(tempFrame))
    sys.stderr.write('\n')

    if len(localFrameStack) == 0:
        sys.stderr.write('  Lokalny ramec neexistuje\n')
    else:
        sys.stderr.write('  Lokalny ramec:       ')
        sys.stderr.write(str(localFrameStack[-1]))
        sys.stderr.write('\n')
    sys.stderr.write('*************************************\n')

# -------------------------------------------------------------------------------------
#       slovnik pre vyber funkcie, ktoru zavolat na zaklade operacneho kodu 
# -------------------------------------------------------------------------------------
callFuncDict = {
    'MOVE':         moveInstr,
    'CREATEFRAME':  createFrame,
    'PUSHFRAME':    pushFrame,
    'POPFRAME':     popFrame,
    'DEFVAR':       defvarInstr,
    'CALL':         callInstr,
    'RETURN':       returnInstr,
    'PUSHS':        pushsInstr,
    'POPS':         popsInstr,
    'ADD':          binaryOperationInstr,
    'SUB':          binaryOperationInstr,
    'MUL':          binaryOperationInstr,
    'IDIV':         binaryOperationInstr,
    'LT':           relationOperationInstr,
    'GT':           relationOperationInstr,
    'EQ':           relationOperationInstr,
    'AND':          andOrInstr,
    'OR':           andOrInstr,
    'NOT':          notInstr,
    'INT2CHAR':     int2CharInstr,
    'STRI2INT':     str2IntInstr,
    'READ':         readInstr,
    'WRITE':        writeInstr,
    'CONCAT':       concatInstr,
    'STRLEN':       strlenInstr,
    'GETCHAR':      getCharInstr,
    'SETCHAR':      setCharInstr,
    'TYPE':         typeInstr,
    'LABEL':        labelInstr,
    'JUMP':         jumpInstr,
    'JUMPIFEQ':     compareJumpInstr,
    'JUMPIFNEQ':    compareJumpInstr,
    'DPRINT':       dprintInstr,
    'BREAK':        breakInstr
}

def main(argv):

    filename = ''
    try:
        opts, args = getopt.getopt(argv,"",["source=", "help"])
    except getopt.GetoptError:
        sys.stderr.write('CHYBA: Zle argumenty\n')
        sys.exit(10)
    for opt, arg in opts:
        if opt == '--help':
            if len(sys.argv) != 2:
                sys.stderr.write('CHYBA: --help musi byt jediny parameter\n')
                sys.exit(10)
            print ('    *************************************************')
            print ('    *    Program nacita XML reprezentaciu programu  *')
            print ('    * zo zadaneho suboru a tento program s vyuzitim *')
            print ('    *         stdin a stdout interpretuje           *')
            print ('    *************************************************')
            sys.exit()
        elif opt in ("--source="):
            filename=arg

    progList = []

    lexSyn = lexsynControl.LexSynControl(filename)
    progList = lexSyn.progControl()

    for i in progList:
        if i['opcode'] == 'LABEL':
            if i['label'] in labels:
                sys.stderr.write('CHYBA: LABEL: Redefinicia navestia\n')
                sys.exit(52)
            else:
                labels[i['label']] = i['order']

    global progCounter
    while (progCounter != len(progList)):
        executeInstr = callFuncDict[progList[progCounter]['opcode']]
        executeInstr(progList)
        progCounter += 1
    
if __name__ == "__main__":
   main(sys.argv[1:])

