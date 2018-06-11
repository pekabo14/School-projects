<?php

/**
 * IPP projekt: keyWords.php
 * Autor: Peter Kapicak (xkapic02)
 * Skola: VUT FIT Brno 
*/

    // constant array of key words
    const KEY_WORDS = array(
        array('MOVE',       'VARIABLE', 'SYMBOL' ),
        array('CREATEFRAME'),
        array('PUSHFRAME'), 
        array('POPFRAME'),
        array('DEFVAR',     'VARIABLE'), 
        array('CALL',       'LABEL'), 
        array('RETURN'),
        array('PUSHS',      'SYMBOL'), 
        array('POPS',       'VARIABLE'), 
        array('ADD',        'VARIABLE', 'SYMBOL', 'SYMBOL'),
        array('SUB',        'VARIABLE', 'SYMBOL', 'SYMBOL'), 
        array('MUL',        'VARIABLE', 'SYMBOL', 'SYMBOL'), 
        array('IDIV',       'VARIABLE', 'SYMBOL', 'SYMBOL'), 
        array('LT',         'VARIABLE', 'SYMBOL', 'SYMBOL'),
        array('GT',         'VARIABLE', 'SYMBOL', 'SYMBOL'), 
        array('EQ',         'VARIABLE', 'SYMBOL', 'SYMBOL'), 
        array('AND',        'VARIABLE', 'SYMBOL', 'SYMBOL'), 
        array('OR',         'VARIABLE', 'SYMBOL', 'SYMBOL'), 
        array('NOT',        'VARIABLE', 'SYMBOL'),
        array('INT2CHAR',   'VARIABLE', 'SYMBOL'), 
        array('STRI2INT',   'VARIABLE', 'SYMBOL', 'SYMBOL'), 
        array('READ',       'VARIABLE', 'TYPE'),
        array('WRITE',      'SYMBOL'), 
        array('CONCAT',     'VARIABLE', 'SYMBOL', 'SYMBOL'), 
        array('STRLEN',     'VARIABLE', 'SYMBOL'),
        array('GETCHAR',    'VARIABLE', 'SYMBOL', 'SYMBOL'), 
        array('SETCHAR',    'VARIABLE', 'SYMBOL', 'SYMBOL'), 
        array('TYPE',       'VARIABLE', 'SYMBOL'),
        array('LABEL',      'LABEL'), 
        array('JUMP',       'LABEL'), 
        array('JUMPIFEQ',   'LABEL',    'SYMBOL', 'SYMBOL'), 
        array('JUMPIFNEQ',  'LABEL',    'SYMBOL', 'SYMBOL'), 
        array('DPRINT',     'SYMBOL'), 
        array('BREAK')
    );

    
?>