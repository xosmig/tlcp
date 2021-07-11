grammar tlcp;

/////////////////////////////////////////////////////////////////////
// Parser rules 
/////////////////////////////////////////////////////////////////////

config              : families? block EOF ;

block               : familyStatement* ;
familyStatement     : (familyName '@')* statement ;
statement           : blockWIthBeginEnd
                    | oneOf
                    | tlcStatement
                    ;

blockWIthBeginEnd   : BEGIN block END ;

families            : FAMILIES familyName+  ;
familyName          : IDENT ;

oneOf               : (ONE_OF | ONE_OF_WITH_SUBFOLDERS) option+ END ;
option              : OPTION '(' optionName ')' block ;
optionName          : IDENT ;

tlcStatement        : TLC_SINGULAR_KW IDENT
                    | TLC_PLURAL_KW IDENT*
                    | TLC_CONSTANT_KW (replacement | assignment)*
                    | CHECK_DEADLOCK_KW BOOLEAN
                    ;
replacement         : IDENT '<-' ('[' anyIdent ']')? identValue ;
assignment          : IDENT '=' identValue ;
identValue          : anyIdent
                    | NUMBER
                    | STRING
                    | BOOLEAN
                    | valueSet
                    | intRange
                    ;
valueSet            : emptySet | '{' identValue (',' identValue)* '}' ;
emptySet            : '{' '}' ;
intRange            : (IDENT|NUMBER) '..' (IDENT|NUMBER) ;

anyIdent            : tlcKeyword
                    | IDENT
                    ;
tlcKeyword          : CHECK_DEADLOCK_KW
                    | TLC_SINGULAR_KW
                    | TLC_PLURAL_KW
                    | TLC_CONSTANT_KW
                    ;


///////////////////////////////////////////////////////////////////// 
// Lexer rules 
/////////////////////////////////////////////////////////////////////

FAMILIES                : '#' F A M I L I E S ;
BEGIN                   : '#' B E G I N ;
END                     : '#' E N D ;
ONE_OF_WITH_SUBFOLDERS  : '#' O N E '_' O F WHITESPACE+ W I T H WHITESPACE+ S U B F O L D E R S;
ONE_OF                  : '#' O N E '_' O F ;
OPTION                  : '#' O P T I O N ;

STRING              : '"' .*? '"' ;
TLCP_COMMAND        : '#' LETTER+ ;
BOOLEAN             : 'TRUE' | 'FALSE' ;
CHECK_DEADLOCK_KW   : 'CHECK_DEADLOCK' ;
TLC_SINGULAR_KW     : 'SPECIFICATION' | 'INIT' | 'NEXT' | 'VIEW' | 'SYMMETRY' ;
TLC_PLURAL_KW       : 'CONSTRAINT' | 'CONSTRAINTS' | 'ACTION-CONSTRAINT' | 'ACTION-CONSTRAINTS'
                    | 'INVARIANT' | 'INVARIANTS' | 'PROPERTY' | 'PROPERTIES'
                    ;
TLC_CONSTANT_KW     : ('CONSTANT' | 'CONSTANTS') ;
IDENT               : (LETTER|DIGIT)* LETTER (LETTER|DIGIT)* ;
NUMBER              : '-'? ([0-9] | [1-9] [0-9]+) ;

LINE_COMMENT        : '\\*' .*? NEWLINE -> channel(2) ;
MLINE_COMMENT       : '(*' .*? '*)' -> channel(2) ;
WHITESPACE          : (' ' | '\t' | NEWLINE) -> channel(2) ;

fragment NEWLINE    : ('\r' '\n' | '\n' | '\r') ;
fragment LETTER     : [a-zA-Z_] ;
fragment DIGIT      : [0-9] ;

fragment A  :  ('a' | 'A');
fragment B  :  ('b' | 'B');
fragment C  :  ('c' | 'C');
fragment D  :  ('d' | 'D');
fragment E  :  ('e' | 'E');
fragment F  :  ('f' | 'F');
fragment G  :  ('g' | 'G');
fragment H  :  ('h' | 'H');
fragment I  :  ('i' | 'I');
fragment J  :  ('j' | 'J');
fragment K  :  ('k' | 'K');
fragment L  :  ('l' | 'L');
fragment M  :  ('m' | 'M');
fragment N  :  ('n' | 'N');
fragment O  :  ('o' | 'O');
fragment P  :  ('p' | 'P');
fragment Q  :  ('q' | 'Q');
fragment R  :  ('r' | 'R');
fragment S  :  ('s' | 'S');
fragment T  :  ('t' | 'T');
fragment U  :  ('u' | 'U');
fragment V  :  ('v' | 'V');
fragment W  :  ('w' | 'W');
fragment X  :  ('x' | 'X');
fragment Y  :  ('y' | 'Y');
fragment Z  :  ('z' | 'Z');
