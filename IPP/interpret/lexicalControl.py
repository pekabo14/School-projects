# Projekt do predmetu IPP (VUT FIT)
# Autor: Peter Kapicak (xkapic02)

import re
import sys


def labelControl(value):
    regex = r"^[-,$-&,*,_,a-zA-Z][-,$-&,*,_,a-zA-Z0-9]*$"
                
    if not re.match(regex,value):
        sys.stderr.write('CHYBA: Nespravna hodnota operandu label\n')
        sys.exit(32)
        
def symbolControl(value, argType):

    if argType == 'var':
        regex = r"^[G,L,T]F@[-,$-&,*,_,a-zA-Z][-,$-&,*,_,a-zA-Z0-9]*$"
        if not re.match(regex,value):
            return 'MISS'
        else:
            return 'var'

    elif argType == 'int':
        regex = r"^[-,+]?[0-9]+$"
        if not re.match(regex,value):
            return 'MISS'
        else:
            return 'int'

    elif argType == 'bool':
        regex = r"^(false|true)$"
        if not re.match(regex,value):
            return 'MISS'
        else:
            return 'bool'

    elif argType == 'string':
        regex = r"([^\s#\\]|\\[0-9]{3})*$"
        if not re.match(regex,value):
            return 'MISS'
        else:
            return 'string'

def varControl(value):
    regex = r"^[G,L,T]F@[-,$-&,*,_,a-zA-Z][-,$-&,*,_,a-zA-Z0-9]*$"
                    
    if not re.match(regex,value):
        sys.stderr.write('CHYBA: Nespravna hodnota operandu var\n')
        sys.exit(32)

def typeControl(value):
    regex = r"^(int|bool|string)$"
                    
    if not re.match(regex,value):
        sys.stderr.write('CHYBA: Nespravna hodnota operandu type\n')
        sys.exit(32)        
        