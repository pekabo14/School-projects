<?php
/*
    * IPP projekt: parse.php
    * Autor: Peter Kapicak (xkapic02)
    * Skola: VUT FIT Brno 
*/

    define('END_LINE', 'end of the line');// pre kontrolu ci je 1 instrukci na 1 riadku 

    // navratove hodnoty pri chybach 
    define('PARSE_ERR', 21);  
    define('ARG_ERR', 10);
    define('FILE_ERR', 12);  

    // pomocme retazce na urcenie poradia vypisu statistik do suboru
    define('LOC', "loc");
    define('COMMENTS', "comments");

    include 'src_parse/keyWords.php';
    include 'src_parse/lexical.php';
    include 'src_parse/wordControl.php';

//=================================== Kontrola argumentov ======================================================
    $paramCnt = 1; // pretoze prvy argument je nazov skriptu
    $loc = false;
    $comments = false;
    $statistic = false;
    // pole a index pre zapamatanie poradia vypisu statistik do suboru
    $list = array();
    $listcnt = 0;

    $longopt = array('stats::');
    $stat = array();
    $stat = getopt('stats::', $longopt);
    
    while ( $paramCnt < $argc ) {
        if ( strcmp($argv[$paramCnt], '--help') == 0 ) {
            if ( $argc != 2 ) {// jeden argument prikazoveho riadku 
                exit(ARG_ERR);        
            }
            else {
                echo "      =======================================================================\n";
                echo "      /       Skript typu filter (parse.php v jazyku PHP5.6) nacita         /\n";
                echo "      /          zo standartneho vstupu zdrojovy kod v jazyku               /\n";
                echo "      /      IPPcode18, skontroluje lexikalnu a syntakticku spravnost       /\n";
                echo "      /   kodu a vypise na standartny vystup XML reprezentaciu programu.    /\n";
                echo "      =======================================================================\n";
                exit(0);
            }
        }
        elseif ( strcmp($argv[$paramCnt], '--loc') == 0 ) {
            if ( $loc ) {
                error_log('ERROR: Multiple --loc');
                exit(ARG_ERR);
            }
            if ( $listcnt < 2 ) {
                $list[$listcnt] = LOC;
                $listcnt++;
            }
            $loc = true;
        }
        elseif ( strcmp($argv[$paramCnt], '--comments') == 0 ) {
            if ( $comments ) {
                error_log('ERROR: Multiple --comments');
                exit(ARG_ERR);
            }
            if ( $listcnt < 2 ) {
                $list[$listcnt] = COMMENTS;
                $listcnt++;
            }
            $comments = true;
        }
        elseif ( preg_match('/^--stats=/', $argv[$paramCnt]) != 0 ) {
            if ( !empty($stat) ) {
                if ( $statistic ) {
                    error_log('ERROR: Multiple --stats');
                    exit(ARG_ERR);
                }
                $statistic = true;
            }
            else {
                error_log('ERROR: Missing filename');
                exit(FILE_ERR);
            }
        }
        else {
            error_log('ERROR: Wrong arguments');
            exit(10);
        }
        $paramCnt++;
    }
    if ( $loc || $comments ) {
        if ( !$statistic ) {
            error_log('ERROR: Missing --stats argument');
            exit(ARG_ERR);
        }
    }
//==================================== Analyza zdrojoveho kodu ===================================================
    $lexical = new Lexical();
    $wordControl = new ControlWords();
    $programXML = new DOMDocument('1.0', 'UTF-8');
    $programXML->formatOutput = true;

    $locCounter = 0;// pre ukladanie poctu riadkov instrukcii

    // nacitanie a rozdelenie vstupu na riadky
    $input = file_get_contents('php://stdin');
    $line = preg_split('/[\r?\n]/', $input);
    
    $lexical->setLine($line[0]); // prvy riadok vstupu musi byt hlavicka '.IPPcode18'
    $lexical->removeComments();
    $lexical->splitLine();

// *********************KONTROLA HLAVICKY IPPcode18*************************************************************
    $word = $lexical->getWord();
    // podmienka ci je prvy riadok vstupu '.IPPcode18'
    if ( strcasecmp( $word, ".IPPcode18" ) != 0 ) {
        exit(PARSE_ERR);
    }   
    else {
        $word = $lexical->getWord();
        if ( $word == NULL ) {// preskocenie prebytocnych bielych znakov
            $word = $lexical->getWord();
        }
        if ( $word != END_LINE ) {
            exit(PARSE_ERR);
        }
        else {// generovanie XML hlavicky a korenoveho elementu
            $program = $programXML->createElement('program');
            $progAttr = $programXML->createAttribute('language');
            $progAttr->value = 'IPPcode18';
                
            $programXML->appendChild($program);
            $program->appendChild($progAttr);
        }

        // *********************KONTROLA INSTRUKCIE*************************************************************
        array_shift($line);// vynechanie prveho riadku zo vstupu (hlavicka .IPPcode18)

        foreach ( $line as $singleLine ) {// preskocenie prazdnych riadkov
            if (ctype_space($singleLine) || $singleLine == '') {
                continue;
            }

            $lexical->setLine($singleLine);
            $lexical->removeComments();
            $lexical->splitLine();

            $word = $lexical->getWord();

            if ( $word == NULL ) {// preskocenie bielych znakov
                while ($word == NULL) {
                    $word = $lexical->getWord();
                }
                if ( $word == END_LINE ) {
                    continue;
                }
            }

            foreach ( KEY_WORDS as $instruction ) {
                if ( strcasecmp( $word, $instruction[0] ) == 0 ) {// prvy prvok pola je klucove slovo
                    $instr = $instruction;

                    static $CountOrder = 1; // cislo instrukcie do generovneho XML suboru
                    $instrXML = $programXML->createElement('instruction');
                    $order = $programXML->createAttribute('order');
                    $order->value = $CountOrder;
                    $instrXML->appendChild($order);

                    $opcode = $programXML->createAttribute('opcode');
                    $opcode->value = $instruction[0];
                    $instrXML->appendChild($opcode);
                    $program->appendChild($instrXML);

                    $CountOrder++;
                    break;       
                }
            }
            if ( !isset($instr) ) { // kontrola ci bolo klucove slovo najdene v poli 
                error_log('ERROR: Instruction does not exist');
                exit(PARSE_ERR);
            }
            
            array_shift($instr);// vymazanie klucoveho slova 
         
            // kontrola argumentov instrukcie
            $arg = 1; // pocitadlo argumentov instrukcie pre XML vystup 
            foreach ($instr as $argument) {
                $elem = 'arg'.$arg;
                $arg++;

                $word = $lexical->getWord();
                $wordControl->setWord($word);

                $operandXML = $programXML->createElement($elem);
                $type = $programXML->createAttribute('type');

                if ( strcmp( $argument, 'VARIABLE' ) == 0 ) { // kontrola argumentu <var>
                    $wordControl->varCheck();

                    $type->value = 'var';
                    $node = $programXML->createTextNode($word);
                    $operandXML->appendChild($type);
                }
                elseif ( strcmp( $argument, 'SYMBOL' ) == 0 ) {
                    // <symbol> moze byt premenna alebo hodnota
                    $result = $wordControl->valueCheck();
                    if ( $result == PARSE_ERR ) {
                        $wordControl->varCheck();

                        $type->value = 'var';
                        $node = $programXML->createTextNode($word);
                        $operandXML->appendChild($type);
                    }
                    else {
                        $res = preg_replace('/^(string|int|bool)@/', "", $word);
                        $dataType = explode('@', $word);

                        $type->value = $dataType[0];
                        $node = $programXML->createTextNode($res);
                        $operandXML->appendChild($type); 
                    }
                    
                }   
                elseif ( strcmp( $argument, 'LABEL' ) == 0 ) {// kontrola argumentu <label>
                    $wordControl->labelCheck();

                    $type->value = 'label';
                    $node = $programXML->createTextNode($word);
                    $operandXML->appendChild($type);
                }
                else {// kontrola argumentu <type>
                    $wordControl->typeCheck();

                    $type->value = 'type';
                    $node = $programXML->createTextNode($word);
                    $operandXML->appendChild($type);
                }
                $operandXML->appendChild($node);
                $instrXML->appendChild($operandXML);
            }

            $word = $lexical->getWord();
            if ( $word == NULL ) {// preskocenie bielych znakov 
                $word = $lexical->getWord();
            }
            if ($word != END_LINE) {
                exit(PARSE_ERR);
            }
            else {
                $locCounter++;
            }
        }
    }
    echo $programXML->saveXML(); // vypis XML suboru na STDOUT

    // kontrola ci bol skript s pozadovanymi argumentami, ak boli zadane 
    if ( $statistic ) {
        if ( $loc || $comments ) {
            $filename = fopen($stat['stats'], 'w+');
            if ( $filename == 0 ) {
                error_log('ERROR: filename was not opened');
                exit(FILE_ERR);
            }
            else {
                // prevod poctu riadkov a komentarov na retazec 
                $strLoc = strval($locCounter);
                $strCom = strval($lexical->getCommentsCnt());

                $strLoc .= "\n";
                $strCom .= "\n";
    
                if ( strcmp($list[0], LOC) == 0 ) {// urcenie poradia vypisu statistik do suboru
                    fwrite($filename, $strLoc);
                    if ( $comments ) {
                        fwrite($filename, $strCom);
                    }
                    fclose($filename);
                }
                else {
                    fwrite($filename, $strCom);
                    if ( $loc ) {
                        fwrite($filename, $strLoc);
                    }
                    fclose($filename);
                }
            }
        }
    }
   
?>