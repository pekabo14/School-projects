<?php

/**
 * IPP projekt: wordControl.php
 * Autor: Peter Kapicak (xkapic02)
 * Skola: VUT FIT Brno 
*/

    class ControlWords {

        private $wordToControl = "";

        /**
         * Nastavenie slova pre kontrolu 
         */
        public function setWord($word) {
            $this->wordToControl = $word;
        }
        
        /**
         * Kontrola, ci je slovo premenna 
         */
        public function varCheck() {
            $regex = '/^[G,L,T]F@[-,$-&,*,_,a-zA-Z][-,$-&,*,_,a-zA-Z0-9]*$/';

            if ( preg_match( $regex, $this->wordToControl, $match ) == 0 ) {
                exit(PARSE_ERR);
            }
        }


        /**
         * Kontrola, ci je slovo hodnota 
         */
        public function valueCheck() {
            $varRegex = '/^[G,L,T]F@[-,$-&,*,_,a-zA-Z][-,$-&,*,_,a-zA-Z0-9]*$/';

            if ( preg_match( '/^int@\S*/', $this->wordToControl, $match ) == 0 ) {
                if ( preg_match( '/^bool@(true|false)/', $this->wordToControl, $match ) == 0 ) {
                    if ( preg_match( '/^string@(?!.*\\\\[^[0-9]])(?:\p{L}|\d|[[:print:]])*(?<!(\\\\[0-9]{0})|(\\\\[0-9]{1})|(\\\\[0-9]{2})|(\\\\))$/u', $this->wordToControl, $match ) == 0 ) {
                        return PARSE_ERR;
                    }   
                }
            }
        } // end function

        /**
         * Kontrola, ci je navestie
         */
        public function labelCheck() {
            $regex = '/^[-,$-&,*,_,a-zA-Z][-,$-&,*,_,a-zA-Z0-9]*$/';

            if ( preg_match( $regex, $this->wordToControl, $match ) == 0 ) {
                exit(PARSE_ERR);
            }
        }

        /**
         * Kontrola, ci je slovo datovy typ 
         */
        public function typeCheck() {
            if ( strcmp($this->wordToControl, 'int') != 0 ) {
                if ( strcmp($this->wordToControl, 'string') != 0 ) {
                    if ( strcmp($this->wordToControl, 'bool') != 0 ) {
                        exit(PARSE_ERR);
                    }   
                }
            }
        } // end function
    }
?>