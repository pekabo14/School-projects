<?php

/**
 * IPP projekt: lexical.php
 * Autor: Peter Kapicak (xkapic02)
 * Skola: VUT FIT Brno 
*/

    class Lexical {
        private $wCounter = 0;
        private $words = array();
        private $line = "";
        private $commentCounter = 0;
        
        /**
         * Nastavenie riadku pre dalsie spracovanie 
         */
        public function setLine($line) {
            $this->line = $line;
        }

        /**
         * Vracia pocet komentarov v zdrojovom texte 
         */
        public function getCommentsCnt() {
            return $this->commentCounter;
        }

        /**
         * Rozdelenie riadku na slova 
         */
        public function splitLine() {
            $this->words = preg_split('/[\' \',\t]+/', $this->line);
        }

        /**
         * Vymazanie komentarov 
         */
        public function removeComments() {
            $tmpLine = $this->line;
            $this->line = preg_replace('/[#].*/', "", $tmpLine);

            if ( strcmp($tmpLine, $this->line) != 0 ) {
                $this->commentCounter++;
            }
        }

        /**
         * Vracia jedno slovo z pola, ktore obsahuje jeden riadok  
         */
        public function getWord() {
            while ( isset( $this->words[$this->wCounter] ) ) {
                $wr = $this->words[$this->wCounter];
                $this->wCounter++;
                return $wr;
            }
            if ( !isset( $this->words[$this->wCounter] ) ) {
                $this->wCounter = 0;
                return END_LINE;
            }
        }
    }
?>