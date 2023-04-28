<?php

# Class for all program arguments, with methods to their parsing, checking and printing(for debug)
class Arguments{
    var $directory = "/.";
    var $parse_script = "parse.php";
    var $int_script = "interpret.py";
    var $jex = "/pub/courses/ipp/jexamxml";
    var $recursive = false;
    var $parse_only = false;
    var $int_only = false;
    var $no_clean = false;

    function take_arguments(){
        $longopts = array("help", "directory::", "recursive", "parse-script::", "int-script::",
            "parse-only", "int-only", "jexampath::", "noclean");
        $options = getopt("",$longopts);
        GLOBAL $argc;
        GLOBAL $argv;

        if (in_array("--directory=", $argv)){
            $options += array("directory="=>"");
        }
        if (in_array("--parse-script=", $argv)){
            $options += array("parse-script="=>"");
        }
        if (in_array("--int-script=", $argv)){
            $options += array("int-script="=>"");
        }
        if (in_array("--jexampath=", $argv)){
            $options += array("jexampath="=>"");
        }

        if ($argc != count($options) + 1){
            error_log("Program arguments error, wrong number of arguments");
            exit(10);
        }
        if (in_array("--jexampath", $argv) or in_array("--int-script", $argv) or
            in_array("--parse-script", $argv) or in_array("--directory", $argv)){
            error_log("Program arguments error, wrong argument");
            exit(10);
        }

        if (array_key_exists("help", $options)){
            if ($argc != 2){
                error_log("Program arguments error, argument help cannot be combined with any other arguments");
                exit(10);
            }
            echo "Usage: php test.php [--help] [--directory=path] [--recursive] [--parse-script=file] [--int-script=file] [--parse-only] [--int-only]
                                        [--jexampath=file] [--noclean]\n";
            echo "\t --directory - specifies the path to the directory with the test cases, default value is the current directory\n";
            echo "\t --recursive - when set on all of the directories will be recursively searched for test cases\n";
            echo "\t --parse-script - specifies the parse file, default value is \"parse.php\" in current directory\n";
            echo "\t --int-script - specifies the interpret file, default value is \"interpret.py\" in current directory\n";
            echo "\t --parse-only - runs only the parse tests, cannot be combined with int-only or int-script\n";
            echo "\t --int-only - runs only the interpret tests, cannot be combined with parse-only, parse-script or jexamxml argument\n";
            echo "\t --jexampath - specifies the jexamxml file for comparing xml files, default value is \"/pub/courses/ipp/jexamxml\" \n";
            echo "\t --noclean - when set on temporary files created during tests won't be deleted\n";
            echo "\t --help - printing this help, cannot be combined with other arguments\n";
            exit(0);
        }
        if (array_key_exists("directory", $options)){
            $this->directory = $options["directory"];
        }
        if (array_key_exists("recursive", $options)){
            $this->recursive = true;
        }
        if (array_key_exists("parse-script", $options)){
            $this->parse_script = $options["parse-script"];
        }
        if (array_key_exists("int-script", $options)){
            $this->int_script = $options["int-script"];
        }
        if (array_key_exists("parse-only", $options)){
            if (array_key_exists("int-only", $options) or array_key_exists("int-script", $options)){
                error_log("Program arguments error, incompatible arguments");
                exit(10);
            }
            $this->parse_only = true;
        }
        if (array_key_exists("int-only", $options)){
            if (array_key_exists("parse-only", $options) or array_key_exists("parse-script", $options) or
                array_key_exists("jexampath", $options)){
                error_log("Program arguments error, incompatible arguments");
                exit(10);
            }
            $this->int_only = true;
        }
        if (array_key_exists("jexampath", $options)){
            $this->jex = $options["jexampath"];
        }
        if (array_key_exists("noclean", $options)){
            $this->no_clean = true;
        }
    }

    function check_args(){
        if (!file_exists($this->directory) or !is_readable($this->directory)){
            error_log("Couldn't open the test directory");
            exit(41);
        }
        if (!$this->int_only) {
            if (!file_exists($this->parse_script) or !is_readable($this->directory)) {
                error_log("Couldn't open the parse file");
                exit(41);
            }
            if ($this->parse_only){
                if (!file_exists($this->jex) or !is_readable($this->directory)) {
                    error_log("Couldn't open the jexamxml file");
                    exit(41);
                }
            }
        }
        if (!$this->parse_only){
            if (!file_exists($this->int_script) or !is_readable($this->directory)){
                error_log("Couldn't open the interpret file");
                exit(41);
            }
        }
    }

    function print_args(){
        echo "Directory: " . $this->directory . "\n";
        echo "Parse_scr: " . $this->parse_script . "\n";
        echo "Int_scr: " . $this->int_script . "\n";
        echo "Jex: " . $this->jex . "\n";
        echo "Recursive: " . $this->recursive . "\n";
        echo "parse-only: " . $this->parse_only . "\n";
        echo "int-only: " . $this->int_only . "\n";
        echo "no_clean: " . $this->no_clean . "\n";
    }
}

# Creates the css styles for final html page with test results
function create_html_styles($dom){
    $css_text = '';
    $css_text .= 'body{width:80%;margin:auto;margin-top:50px;text-align:center;}';
    $css_text .= '#configuration_table{border:1px solid #ececec;width: 35%;margin:8px;float: left;margin-left:10%;margin-right:15px;}';
    $css_text .= '#configuration_table th{border:1px solid #ececec;padding:5px;}';
    $css_text .= '#configuration_table td{border:1px solid #ececec;padding:5px;}';

    $css_text .= '#result_table{border:1px solid #ececec;width: 40%;margin:8px;float: left;margin-left:15px;margin-right:auto;margin-top:5%;margin-bottom:auto;}';
    $css_text .= '#result_table th{border:1px solid #ececec;padding:5px;}';
    $css_text .= '#result_table td{border:1px solid #ececec;padding:5px;}';

    $css_text .= '#test_table{border:1px solid #ececec;width: 90%;margin-left:auto;margin-right:auto;border-collapse: collapse;margin-top:10px;margin-bottom:10px;}';
    $css_text .= '#test_table th{padding:5px;}';
    $css_text .= '#test_table td{padding:5px;}';

    $css_text .= '#directory_header{background-color: #F4F4F4;background-color: #9DCEEF;border:1px solid #ececec;border-collapse: collapse;}';
    $css_text .= '#test_header{background-color: #E2EDF5;border:1px solid #ececec;border-collapse: collapse;}';
    $css_text .= '#test_fail{color: #FB0008;font-weight: bold;}';
    $css_text .= '#test_pass{color: #29E136;font-weight: bold;}';
    $css_text .= '#result{font-size: 200%;}';

    $style = $dom->createElement('style', $css_text);
    $domAttribute = $dom->createAttribute('type');//Create the new attribute 'type'
    $domAttribute->value = 'text/css';//Add value to attribute
    $style->appendChild($domAttribute);//Add the attribute to the style tag
    $dom->appendChild($style);//Add the style tag to document
}

# Creates tan element for configuration table for html page
function create_config_part($dom, $table, $text, $value){
    $tr = $dom->createElement('tr');
    $table->appendChild($tr);
    $th = $dom->createElement('th', $text);
    $tr->appendChild($th);
    $td = $dom->createElement('td', $value);
    $tr->appendChild($td);
}

# Creates the configuration table for html page
function html_configuration($dom, $args){
    $table = $dom->createElement('table');
    $tableAttribute = $dom->createAttribute('id');
    $tableAttribute->value = 'configuration_table';
    $table->appendChild($tableAttribute);
    $dom->appendChild($table);

    create_config_part($dom, $table, "Parse script:", $args->parse_script);

    create_config_part($dom, $table, "Interpret script:", $args->int_script);

    create_config_part($dom, $table, "Jexamxml script:", $args->jex);

    if ($args->parse_only){
        $tmp = "True";
    }
    else{
        $tmp = "False";
    }
    create_config_part($dom, $table, "Parse-only:", $tmp);

    if ($args->int_only){
        $tmp = "True";
    }
    else{
        $tmp = "False";
    }
    create_config_part($dom, $table, "Interpret-only:", $tmp);

    if ($args->recursive){
        $tmp = "True";
    }
    else{
        $tmp = "False";
    }
    create_config_part($dom, $table, "Recursive:", $tmp);

    if ($args->no_clean){
        $tmp = "True";
    }
    else{
        $tmp = "False";
    }
    create_config_part($dom, $table, "No clean:", $tmp);
}

# Creates the result table for html page
function html_test_results($dom){
    GLOBAL $test_count;
    GLOBAL $test_passed;
    if ($test_count == 0){
        $result = 0;
    }
    else{
        $result = round($test_passed/$test_count*100);
    }
    $table = $dom->createElement('table');
    $tableAttribute = $dom->createAttribute('id');
    $tableAttribute->value = 'result_table';
    $table->appendChild($tableAttribute);
    $dom->appendChild($table);

    $tr_1 = $dom->createElement('tr');
    $table->appendChild($tr_1);
    $tr_2 = $dom->createElement('tr');
    $table->appendChild($tr_2);
    $tr_3 = $dom->createElement('tr');
    $table->appendChild($tr_3);
    $th = $dom->createElement('th', $result . "%");
    $thAttribute = $dom->createAttribute('rowspan');
    $thAttribute->value = '3';
    $th->appendChild($thAttribute);
    $tableAttribute = $dom->createAttribute('id');
    $tableAttribute->value = 'result';
    $th->appendChild($tableAttribute);
    $tr_1->appendChild($th);

    $th = $dom->createElement('th', "Overall:");
    $tr_1->appendChild($th);
    $th = $dom->createElement('th', $test_count);
    $tr_1->appendChild($th);

    $th = $dom->createElement('th', "Passed:");
    $tr_2->appendChild($th);
    $th = $dom->createElement('th', $test_passed);
    $tr_2->appendChild($th);

    $th = $dom->createElement('th', "Failed:");
    $tr_3->appendChild($th);
    $th = $dom->createElement('th', $test_count - $test_passed);
    $tr_3->appendChild($th);
}

# Creates the test cases table
function create_table($dom, $directory){
    $table = $dom->createElement('table');
    $tableAttribute = $dom->createAttribute('id');
    $tableAttribute->value = 'test_table';
    $table->appendChild($tableAttribute);

    $tr = $dom->createElement('tr');
    $tableAttribute = $dom->createAttribute('id');
    $tableAttribute->value = 'directory_header';
    $tr->appendChild($tableAttribute);
    $table->appendChild($tr);
    $th = $dom->createElement('th', "Directory:");
    $tr->appendChild($th);
    $th = $dom->createElement('th', $directory);
    $tr->appendChild($th);
    $td = $dom->createElement('td');
    $tr->appendChild($td);
    $td = $dom->createElement('td');
    $tr->appendChild($td);
    $td = $dom->createElement('td');
    $tr->appendChild($td);
    $td = $dom->createElement('td');
    $tr->appendChild($td);

    return $table;
}

# Creates the header for each test case in test case table for html page
function add_table_header($dom, $table, $number, $test_case){
    //Add new row
    $tr = $dom->createElement('tr');
    $tableAttribute = $dom->createAttribute('id');
    $tableAttribute->value = 'test_header';
    $tr->appendChild($tableAttribute);
    $table->appendChild($tr);

    //Add new column
    $th = $dom->createElement('th', $number);
    $tr->appendChild($th);

    $th = $dom->createElement('th', "Test case:");
    $tr->appendChild($th);
    $td = $dom->createElement('td', $test_case);
    $tr->appendChild($td);
    $td = $dom->createElement('td');
    $tr->appendChild($td);
    $td = $dom->createElement('td');
    $tr->appendChild($td);
    $td = $dom->createElement('td');
    $tr->appendChild($td);
}

# Creates the result for each test case in test case table for html page
function add_table_result($dom, $table, $result, $info, $got, $should_get){
    //Add new row
    $tr = $dom->createElement('tr');
    $table->appendChild($tr);

    //Add new column
    $td = $dom->createElement('th');
    $tr->appendChild($td);

    $td = $dom->createElement('td', $info);
    $tr->appendChild($td);
    $td = $dom->createElement('td');
    $tr->appendChild($td);

    $th = $dom->createElement('th', "Result:");
    $tr->appendChild($th);
    $td = $dom->createElement('td', $result);
    if ($result == "PASS"){
        $tableAttribute = $dom->createAttribute('id');
        $tableAttribute->value = 'test_pass';
        $td->appendChild($tableAttribute);
    }
    else{
        $tableAttribute = $dom->createAttribute('id');
        $tableAttribute->value = 'test_fail';
        $td->appendChild($tableAttribute);
    }
    $tr->appendChild($td);
    $td = $dom->createElement('td');
    $tr->appendChild($td);

    $tr = $dom->createElement('tr');
    $table->appendChild($tr);

    $td = $dom->createElement('td');
    $tr->appendChild($td);

    if (strpos($info, 'Return codes') !== false){
        $th = $dom->createElement('th', "Obtained result:");
        $tr->appendChild($th);
        $td = $dom->createElement('td', $got);
        $tr->appendChild($td);

        $td = $dom->createElement('td');
        $tr->appendChild($td);
        $th = $dom->createElement('th', "Expected result:");
        $tr->appendChild($th);
        $td = $dom->createElement('td', $should_get);
        $tr->appendChild($td);
    }
}

# Checks the test case file if they are created and readable, else actions are taken
function check_files($src, $in, $out, $rc){
    if (!is_readable($src)){
        error_log("Can't open source file");
        exit(11);
    }
    if (!is_file($in)){
        $file = fopen($in, 'w');
        fclose($file);
    }
    else{
        if (!is_readable($in)){
            error_log("Can't open input file");
            exit(11);
        }
    }
    if (!is_file($out)){
        $file = fopen($out, 'w');
        fclose($file);
    }
    else{
        if (!is_readable($out)){
            error_log("Can't open output file");
            exit(11);
        }
    }
    if (!is_file($rc)){
        $file = fopen($rc, 'w');
        fwrite($file, "0");
        fclose($file);
    }
    else{
        if (!is_readable($rc)){
            error_log("Can't open return code file");
            exit(11);
        }
    }
}

# Runs the parse-only tests with checking the return value and output with jexamxml file
function parse_only($result, $rc, $jex, $out_tmp, $out, $options, $dom, $table){
    $return_code = file_get_contents($rc);
    GLOBAL $test_passed;
    if ($result != $return_code){
        add_table_result($dom, $table, "FAIL", "Return codes are different", $result, $return_code);
        return;
    }
    elseif($result != 0){
        add_table_result($dom, $table, "PASS", "Return codes are the same", $result, $return_code);
        $test_passed += 1;
        return;
    }

    if (exec("java -jar " . $jex . " " . $out_tmp . " " . $out . " " . $options,
            $helper) === false){
        error_log("Inner error while exec");
        exit(99);
    }

    if (in_array("Error(s)! See log file", $helper)){
        unlink($out_tmp . ".log");
        add_table_result($dom, $table, "FAIL", "Wrong xml format", "", "");
    }
    else if (in_array("Two files are not identical", $helper)){
        add_table_result($dom, $table, "FAIL", "Outputs are different", "", "");
    }
    else{
        add_table_result($dom, $table, "PASS", "Outputs are the same", "", "");
        $test_passed += 1;
    }
}

# Base of the parse tests, runs the tests with expecting interpret tests to be done next,
# checks only the return value whether the test should continue
function parse_test($file_base, $args, $dom, $table){
    $src = $file_base . ".src";
    $out = $file_base . ".out";
    $out_tmp = $file_base . ".out_tmp";
    $rc = $file_base . ".rc";
    check_files($src, $file_base . ".in", $out, $rc);

    $helper = explode("/", $args->jex);
    $options = substr($args->jex, 0, strpos($args->jex, end($helper))) . "options";
    if ($args->parse_only && !is_readable($options)){
        error_log("Can't open options file for jexamxml");
        exit(11);
    }

    if (exec("php8.1 ". $args->parse_script . "<" . $src . " >" . $out_tmp,
        $pass,$result) === false){
        error_log("Inner error while exec");
        exit(99);
    }
    GLOBAL $test_passed;

    if ($args->parse_only){
        parse_only($result, $rc, $args->jex, $out_tmp, $out, $options, $dom, $table);
        if (!$args->no_clean){
            unlink($out_tmp);
        }
        return 0;
    }
    else if (!$args->int_only) {
        $return_code = file_get_contents($rc);
        if ($result != 0) {
            if ($result != $return_code) {
                add_table_result($dom, $table, "FAIL", "Return codes are different", $result, $return_code);
            }
            else {
                add_table_result($dom, $table, "PASS", "Return codes are the same", $result, $return_code);
                $test_passed += 1;
            }
            if (!$args->no_clean){
                unlink($out_tmp);
            }
            return 0;
        }
    }
    return 1;
}

# Runs the interpret tests checking the return value and outputs
function int_test($file_base, $args, $dom, $table){
    $src = $file_base . ".src";
    $out_tmp = $file_base . ".out_tmp";
    $out = $file_base . ".out";
    $rc = $file_base . ".rc";
    $in = $file_base . ".in";

    if (!$args->parse_only and !$args->int_only){
        $src = $file_base . ".out_tmp";
        $out_tmp = $file_base . ".out_f";
    }
    else{
        check_files($src, $in, $out, $rc);
    }

    if (exec("python3 ". $args->int_script . " --source=" . $src .
        " --input=" . $in . " >" . $out_tmp, $pass,$result) === false){
        error_log("Inner error while exec");
        exit(99);
    }

    $return_code = file_get_contents($rc);
    GLOBAL $test_passed;

    if ($result != $return_code) {
        add_table_result($dom, $table, "FAIL", "Return codes are different", $result, $return_code);
    }
    elseif ($result != 0){
        add_table_result($dom, $table, "PASS", "Return codes are the same", $result, $return_code);
        $test_passed += 1;
    }
    else{
        if (sha1_file($out_tmp) != sha1_file($out)){
            add_table_result($dom, $table, "FAIL", "Outputs are different","", "");
        }
        else{
            add_table_result($dom, $table, "PASS", "Outputs are the same", "", "");
            $test_passed += 1;
        }
    }
    if (!$args->no_clean){
        unlink($out_tmp);
        if (!$args->parse_only and !$args->int_only){
            unlink($src);
        }
    }
}

# Removes the current directory and previous directory from the list of files and returns it
function prep_directory($directory){
    $scan = scandir($directory);
    if (($key = array_search(".", $scan)) !== false) {
        unset($scan[$key]);
    }
    if (($key = array_search("..", $scan)) !== false) {
        unset($scan[$key]);
    }
    return $scan;
}

# Runs the test cases in the directory
function run_files_tests($scan, $directory, $args, $dom, $table){

    foreach($scan as $file) {
        if (is_dir($directory . $file)) {
            if ($args->recursive){
                recursive_run($directory . $file, $args, $dom, $table);
            }
        }
        else if (is_file($directory . $file) ){
            $end = explode(".", $file)[1];
            if ($end != "src"){
                continue;
            }

            $base = explode(".", $file)[0];
            $continue = 1;
            GLOBAL $test_count;
            $test_count += 1;
            add_table_header($dom, $table, $test_count, $base);

            if (!$args->int_only){
                $continue = parse_test($directory . $base, $args, $dom, $table);
            }
            if (!$args->parse_only and $continue){
                int_test($directory . $base, $args, $dom, $table);
            }
        }
    }
}

# Is called when ate recursive flag is on, runs the test in nested directories too
function recursive_run($directory, $args, $dom, $table){
    if (substr($directory, -1) != '/'){
        $directory .= "/";
    }
    $scan = prep_directory($directory);

    $table_new = create_table($dom, $directory);
    $table->appendChild($table_new);
    run_files_tests($scan, $directory, $args, $dom, $table_new);
}

function run_tests($args, $dom){
    if (substr($args->directory, -1) != '/'){
        $args->directory .= "/";
    }
    $scan = prep_directory($args->directory);

    $table = create_table($dom, $args->directory);
    run_files_tests($scan, $args->directory, $args, $dom, $table);
    html_configuration($dom, $args);
    html_test_results($dom);
    $dom->appendChild($table);
}

// ---------------Main-------------------
ini_set('display_errors', 'stderr');
$test_count = 0;
$test_passed = 0;
$args = new Arguments();
$args->take_arguments();
$args->check_args();
$dom = new DOMDocument('1.0');
create_html_styles($dom);
run_tests($args, $dom);
echo $dom->saveHTML(); # prints the html page to the output
