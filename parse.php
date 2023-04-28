<?php
/**
 * File name:       parse.php
 * Project:         Lexical and syntactical analysis of IPPcode22, first IPP project
 * Author:          Veronika Molnárová (xmolna08)
 * Date:            4.3.2022
 **/

/**
 * Class for token of the input code., with its value and type.
 * TYPE = [ EOF, EOL, VAR, CSTRING, CINT, CBOOL, CNIL (constants), OTHER ]
 * In cases of EOF and EOL value of the token is empty.
 **/
class Token
{
var $type = "";
var $value = "";
}

// global variable, which saves the found EOL in case it cannot be returned because of another token
$save = "";

/**
 * Function get_token:  Takes characters from the opened stream passed as an argument (expected to be stdin),
 *                       returns a token. Ignores whitespaces and comments
 **/
function get_token($stdin){
    $tok = new Token;
    $tmp = "";
    $empty = 1;
    $comment = 0;

    global $save;
    if ($save == "EOL"){       // EOL was found last time together with another token, return EOL
        $save = "";
        $tok->type = "EOL";
        return $tok;
    }

    while (false !== ($c = fgetc($stdin))) {
        if (($comment == 1) and $c != "\n"){ // eating comments
            continue;
        }
        if ($c == '#'){ // start of the comment
            $comment = 1;
            continue;
        }

        if (($empty == 1) && ctype_space($c)){  // eating whitespaces before the start of the word
            if ($c == "\n"){
                $tok->type = "EOL";
                break;
            }
            continue;
        }
        if (($empty == 0) and ctype_space($c)){ // end of the word
            if ($c == "\n"){
                $save = "EOL";
            }
            break;
        }

        $tmp .= $c;
        $empty = 0;
    }

    if ($tmp == "" && feof($stdin)){
        $tok->type = "EOF";
    }
    elseif($tok->type == "") {
        if (strpos($tmp, '@') !== false) { // matching regexes to each data type
            if (preg_match('/^(LF|TF|GF)@[a-zA-Z_$&%*!?-][0-9a-zA-Z_$&%*!?-]*$/', $tmp)) {
                $tok->type = "VAR";
            } elseif (preg_match('/^nil@nil$/', $tmp)) {
                $tok->type = "CNIL";
            } elseif (preg_match('/^bool@(true|false)$/', $tmp)) {
                $tok->type = "CBOOL";
            } elseif (preg_match('/^int@([+-]?[0-9]+)|(0[xX][0-9a-fA-F]+)|(0[oO][0-7]+)$/', $tmp)) {
                $tok->type = "CINT";
            } elseif (preg_match('/^string@((\\\[0-9]{3})|[^#\\\])*$/', $tmp)) {
                $tok->type = "CSTRING";
            } else {
                error_log("Error in lexical analysis");
                exit(23);
            }
        }
        else {  // could be header, label, type or operation code
            $tok->type = "OTHER";
        }
    }

    $tok->value = $tmp;
    return $tok;
}

/**
 * Function arg_var:    Takes a token and checks whether it is a variable, else returns an error.
 **/
function arg_var($stdin, $xml, $instr, $ord){
    $token = get_token($stdin); //<var>
    if ($token->type != "VAR"){
        error_log("Wrong argument");
        exit(23);
    }

    $val = $token->value;
    $val = str_replace('&', "&amp;",$val);  // replaces special characters for xml
    xml_arg($xml, $instr, "var", "arg".$ord, $val); // creates a xml argument
}

/**
 * Function arg_symb:    Takes a token and checks whether it is a symbol (could be a variable or constant),
 *                        else returns an error.
 **/
function arg_symb($stdin, $xml, $instr, $ord){
    $token = get_token($stdin); //<symb>
    if ($token->type != "VAR" && $token->type[0] != "C"){
        error_log("Wrong argument");
        exit(23);
    }

    //takes the type of the token (var or the type of constant)
    ($token->type == "VAR")?$type = strtolower($token->type):$type = strtolower(substr($token->type, 1));
    // takes the value of the token (value of the constant or the whole name with frame)
    ($token->type == "VAR")?$val = $token->value:$val = substr($token->value, strpos($token->value, '@')+1);

    // replaces special characters for xml
    $val = str_replace('&', "&amp;",$val);
    $val = str_replace('<', "&lt;",$val);
    $val = str_replace('>', "&gt;",$val);

    xml_arg($xml, $instr, $type, "arg".$ord, $val); // creates a xml argument
}

/**
 * Function arg_label:    Takes a token and checks whether it is a label, else returns an error.
 **/
function arg_label($stdin, $xml, $instr, $ord){
    $token = get_token($stdin); //<label>
    if (!preg_match('/^[a-zA-Z_$&%*!?-][0-9a-zA-Z_$&%*!?-]*$/', $token->value)) {
        error_log("Wrong argument");
        exit(23);
    }

    $val = $token->value;
    $val = str_replace('&', "&amp;",$val);  // replace special characters for xml
    xml_arg($xml, $instr, "label", "arg".$ord, $val);   // creates a xml argument
}

/**
 * Function arg_type:    Takes a token and checks whether it is a type, else returns an error.
 **/
function arg_type($stdin, $xml, $instr, $ord){
    $token = get_token($stdin); //<type>
    if (!preg_match('/^(int|string|bool|nil)$/', $token->value)) {
        error_log("Wrong argument");
        exit(23);
    }
    xml_arg($xml, $instr, "type", "arg".$ord, $token->value);   // create a xml argument
}


/**
 * Function xml_instruc:    Add a new element instruction with arguments order and opcode to the xml.
 **/
function xml_instuc($xml, $root, $order, $value){
    $instr = $xml->createElement('instruction');
    $instr->setAttribute("order", $order);
    $instr->setAttribute("opcode", $value);
    $root->appendChild($instr);
    return $instr;
}

/**
 * Function xml_arg:    Add a new element argument with argument type and its value to the xml.
 **/
function xml_arg($xml, $instr, $type, $name, $value){
    $arg = $xml->createElement($name, $value);
    $arg->setAttribute("type", $type);
    $instr->appendChild($arg);
}


// ---------------Main-------------------
ini_set('display_errors', 'stderr');

# taking arguments
if ($argc == 2){
    if ($argv[1] == "--help"){
        echo "Usage: parser.php [--help]\n";
        echo "Take the IPPcode22 on the standard input and checks for lexical and syntax errors.
                Returns XML file of the code on standard output.\n";
        echo "--help -  Printing this help\n";
        exit(0);
    }
    else{
        error_log("Error, unknown argument");
        exit(10);
    }
}
if ($argc > 2){
    error_log("Error, unknown argument");
    exit(10);
}

$stdin = fopen( 'php://stdin', 'r' );

$token = get_token($stdin, $save);
$order = 1;
$state = "HEADER";

// create a xml document
$xml = new DOMDocument('1.0','UTF-8');
$xml->formatOutput = true;
$root = $xml->createElement('program');
$root->setAttribute("language", "IPPcode22");

while($token->type != "EOF"){
    if ($state == "HEADER" && $token->type != "EOL"){
        if (strtoupper($token->value) != ".IPPCODE22"){
            error_log("Wrong header");
            exit(21);
        }
        $xml->appendChild($root);
        $state = "ENDL";
    }
    elseif ($state == "INSTRUC" && $token->type != "EOL"){
        $token->value = strtoupper($token->value);
        switch($token->value){
            case "MOVE": //<var><symb>
            case "INT2CHAR":
            case "STRLEN":
            case "TYPE":
            case "NOT":
                $instr = xml_instuc($xml, $root, $order++, $token->value);
                arg_var($stdin, $xml, $instr, 1);
                arg_symb($stdin, $xml, $instr, 2);
                break;
            case "CREATEFRAME": //none
            case "PUSHFRAME":
            case "POPFRAME":
            case "RETURN":
            case "BREAK":
                $instr = xml_instuc($xml, $root, $order++, $token->value);
                break;
            case "DEFVAR": //<var>
            case "POPS":
                $instr = xml_instuc($xml, $root, $order++, $token->value);
                arg_var($stdin, $xml, $instr, 1);
                break;
            case "PUSHS": //<symb>
            case "WRITE":
            case "EXIT":
            case "DPRINT":
                $instr = xml_instuc($xml, $root, $order++, $token->value);
                arg_symb($stdin, $xml, $instr, 1);
                break;
            case "CALL": //<label>
            case "LABEL":
            case "JUMP":
                $instr = xml_instuc($xml, $root, $order++, $token->value);
                arg_label($stdin, $xml, $instr, 1);
                break;
            case "JUMPIFEQ": //<label><symb1><symb2>
            case "JUMPIFNEQ":
                $instr = xml_instuc($xml, $root, $order++, $token->value);
                arg_label($stdin, $xml, $instr, 1);
                arg_symb($stdin, $xml, $instr, 2);
                arg_symb($stdin, $xml, $instr, 3);
                break;
            case "ADD": //<var><symb1><symb2>
            case "SUB":
            case "MUL":
            case "IDIV":
            case "LT":
            case "GT":
            case "EQ":
            case "AND":
            case "OR":
            case "STRI2INT":
            case "CONCAT":
            case "GETCHAR":
            case "SETCHAR":
                $instr = xml_instuc($xml, $root, $order++, $token->value);
                arg_var($stdin, $xml, $instr, 1);
                arg_symb($stdin, $xml, $instr, 2);
                arg_symb($stdin, $xml, $instr, 3);
                break;
            case "READ": // <var><type>
                $instr = xml_instuc($xml, $root, $order++, $token->value);
                arg_var($stdin, $xml, $instr, 1);
                arg_type($stdin, $xml, $instr, 2);
                break;
            default:
                error_log("Wrong operation code");
                exit(22);
        }
        $state = "ENDL";
    }
    elseif($state == "ENDL"){
        if ($token->type != "EOL"){
            error_log("Missing end of line after the instruction");
            exit(23);
        }
        $state = "INSTRUC";
    }
    $token = get_token($stdin);
}

// print the created xml to stdout
echo $xml->saveXML();
fclose($stdin);
exit(0);

