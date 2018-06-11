# Projekt do predmetu IPP (VUT FIT)
# Autor: Peter Kapicak (xkapic02)

import sys
import xml.etree.ElementTree as ET
import instrList
import lexicalControl
import re

class LexSynControl:
    opcodeCounter = 1
    progList = []

    def __init__(self, filename):
        self.file = filename
        self.tree = ET.parse(self.file)
        self.root = self.tree.getroot()
    
    def progControl(self):
        if self.root.tag != "program":
            sys.stderr.write('CHYBA: Korenovy element nie je "program"\n')
            sys.exit(31)
        else:
            # kontrola atributu korenoveho elementu
            if len(self.root.attrib) > 3:
                sys.stderr.write('CHYBA: Nespravny pocet atributov korenoveho elementu\n')
                sys.exit(31)
            else:
                if len(self.root.attrib) == 2:
                    if 'name' in self.root.attrib or 'description' in self.root.attrib:
                        pass
                    else:
                        sys.stderr.write('CHYBA: Nespravny pocet atributov korenoveho elementu\n')
                        sys.exit(31)
                if len(self.root.attrib) == 3:
                    if 'name' in self.root.attrib and 'description' in self.root.attrib:
                        pass
                    else:
                        sys.stderr.write('CHYBA: Nespravny pocet atributov korenoveho elementu\n')
                        sys.exit(31)

            if "language" not in self.root.attrib or self.root.attrib['language'] != "IPPcode18":
                sys.stderr.write('CHYBA: Nespravny atribut korenoveho elementu\n')
                sys.exit(31)

            self.__instrElemCheck()
        return self.progList

    def __instrElemCheck(self):

        instr = {}
        toSaveInstr = {}

        for child in self.root:
            if child.tag != "instruction":
                sys.stderr.write('CHYBA: Element korenoveho elementu "program" nie je "instruction"\n')
                sys.exit(31)
            else:
                if len(child.attrib) != 2:
                    sys.stderr.write('CHYBA: Nespravny pocet atributov elementu "instruction"\n')
                    sys.exit(31)

                if "order" not in child.attrib or "opcode" not in child.attrib:
                    sys.stderr.write('CHYBA: Nespravny atribut elementu "instruction"\n')
                    sys.exit(31)

                if child.attrib['order'] != str(self.opcodeCounter):
                    sys.stderr.write('CHYBA: Nespravna hodnota atributu elementu "instruction"\n')
                    sys.exit(31)
                else:
                    self.opcodeCounter += 1
                
                instr = self.__opcodeControl(child.attrib['opcode'])
                toSaveInstr['opcode'] = instr['opcode']

            arg1 = False
            arg2 = False
            arg3 = False   
            for arg in child:
                if arg.tag != "arg1" and arg.tag != "arg2" and arg.tag != "arg3":
                    sys.stderr.write('CHYBA: Nespravny element\n')
                    sys.exit(31)
                else:
                    if arg.tag == "arg1":
                        arg1 = True
                    elif arg.tag == "arg2":
                        arg2 = True
                    elif arg.tag == "arg3":
                        arg3 = True

                    if arg.tag not in instr:
                        sys.stderr.write('CHYBA: Zly pocet argumentov\n')
                        sys.exit(31)
                    if "type" not in arg.attrib or len(arg.attrib) != 1:
                        sys.stderr.write('CHYBA: Nespravna hodnota atributu elementu "arg"\n')
                        sys.exit(31)
                    
                    regex = r"^(int|bool|string|label|type|var)$"
                    
                    if not re.match(regex,arg.attrib['type']):
                        sys.stderr.write('CHYBA: Nespravna hodnota atributu elementu "arg"\n')
                        sys.exit(32)
                    
                    if arg.text is not None:
                        if arg.attrib['type'] == 'int' and instr[arg.tag] == 'symbol':
                            result = lexicalControl.symbolControl(arg.text,arg.attrib['type'])
                            if result != 'int':
                                sys.stderr.write('CHYBA: Nespravna hodnota atributu elementu "arg"\n')
                                sys.exit(32)
                            toSaveInstr[arg.tag] = ('int',arg.text)

                        elif arg.attrib['type'] == 'bool' and instr[arg.tag] == 'symbol':
                            result = lexicalControl.symbolControl(arg.text,arg.attrib['type'])
                            if result != 'bool':
                                sys.stderr.write('CHYBA: Nespravna hodnota atributu elementu "arg"\n')
                                sys.exit(32)
                            toSaveInstr[arg.tag] = ('bool',arg.text)

                        elif arg.attrib['type'] == 'string' and instr[arg.tag] == 'symbol':
                            result = lexicalControl.symbolControl(arg.text,arg.attrib['type'])
                            if result != 'string':
                                sys.stderr.write('CHYBA: Nespravna hodnota atributu elementu "arg"\n')
                                sys.exit(32)
            
                            toSaveInstr[arg.tag] = ('string',arg.text)

                        elif arg.attrib['type'] == 'var' and (instr[arg.tag] == 'var' or instr[arg.tag] == 'symbol'):
                            lexicalControl.varControl(arg.text)
                            toSaveInstr[arg.tag] = ('var',arg.text)

                        elif arg.attrib['type'] == 'label' and instr[arg.tag] == 'label':
                            lexicalControl.labelControl(arg.text)
                            toSaveInstr['label'] = arg.text

                        elif arg.attrib['type'] == 'type' and instr[arg.tag] == 'type':
                            lexicalControl.typeControl(arg.text)
                            toSaveInstr['type'] = arg.text

                    else:    
                        if arg.attrib['type'] == 'int':
                            toSaveInstr[arg.tag] = ('int', 0)
                        elif arg.attrib['type'] == 'bool':
                            toSaveInstr[arg.tag] = ('bool','false')
                        elif arg.attrib['type'] == 'string':
                            toSaveInstr[arg.tag] = ('string','')
                        else:
                            sys.stderr.write('CHYBA: Ziadny text elementu "arg"\n')
                            sys.exit(31)

            if len(instr)-1 == 3 : # 3 argumenty minus operacany kod
                if arg1 and arg2 and arg3:
                    pass
                else:
                    sys.stderr.write('CHYBA: Nespravny pocet argumentov instrukcie00\n')
                    sys.exit(32)

            if len(instr)-1 == 2:
                if arg1 and arg2 and not arg3:
                    pass
                else:
                    sys.stderr.write('CHYBA: Nespravny pocet argumentov instrukcie0\n')
                    sys.exit(32)

            if len(instr)-1 == 1:
                if arg1 and not arg2 and not arg3:
                    pass
                else:
                    sys.stderr.write('CHYBA: Nespravny pocet argumentov instrukcie1\n')
                    sys.exit(32)

            if len(instr)-1 == 0:
                if not arg1 and not arg2 and not arg3:
                    pass
                else:
                    sys.stderr.write('CHYBA: Nespravny pocet argumentov instrukcie2\n')
                    sys.exit(32)
            if toSaveInstr['opcode'] == 'LABEL':
                toSaveInstr['order'] = child.attrib['order']   
            self.progList.append(toSaveInstr.copy())
            toSaveInstr.clear()    
                
    def __opcodeControl(self, opcode):
        for opName in instrList.instructions:
            if opName['opcode'] == opcode:
                return opName
        sys.stderr.write('CHYBA: Operacny kod instrukcie neexistuje\n')
        sys.exit(32)
