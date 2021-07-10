grammar tlcp;

/////////////////////////////////////////////////////////////////////
// Parser rules 
/////////////////////////////////////////////////////////////////////

config              : families? block ;

block               : familyStatement* ;
familyStatement     : (familyName '@')* statement ;
statement           : oneOf
                    | tlcStatement
                    ;

families            : '#FAMILIES' '(' (familyName (',' familyName)*)? ')' ;
familyName          : IDENT ;

oneOf               : '#ONE_OF' option+ '#END' ;
option              : '#OPTION' '(' optionName ')' block ;
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
