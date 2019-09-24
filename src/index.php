<!DOCTYPE html>
<html>
    <head>
        <meta charset="utf-8">
	<meta http-equiv="content-language" content="en">
        <title>OntoLex Validator</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <!-- Bootstrap -->
        <link href="bootstrap.min.css" rel="stylesheet" media="screen">
        <link href="validator.css" rel="stylesheet" media="screen">
        <script type="text/javascript" src="jquery-1.7.2.min.js"></script>
    </head>
    <body>
    <div class="container">
<?php

error_reporting(E_ALL);
ini_set('display_errors', '1');

if(array_key_exists('document',$_POST)) {
    $temp = tempnam("/tmp","lexicon");

    $out = fopen($temp,"w");
    fwrite($out,$_POST['document']);
    fclose($out);

    $format = $_POST['format'];
    if($format != "xml" && $format != "turtle") {
        $format = "xml";
    }
    $cmd = "python3 " . getcwd() . "/ontolex-validator.py -f$format -ohtml $temp";
    $descriptorspec = array(
        0 => array("pipe", "r"),
        1 => array("pipe", "w"),
        2 => array("pipe", "w")
    );

    $process = proc_open($cmd, $descriptorspec, $pipes);

    if (is_resource($process)) {
        fclose($pipes[0]);

        $content = stream_get_contents($pipes[1]);
        $errs = stream_get_contents($pipes[2]);
?>
<h1>OntoLex-Lemon Validator</h1>
<h3>You submitted</h3>
<button value="Show/Hide" onclick="javascript:$('#code').toggle();">Show/Hide</button>
<div id="code" style="display:none;">
<pre>
<?php echo htmlspecialchars($_POST['document']); ?>
</pre>
</div>
<h3>Result</h3>
<?php
        echo $content;
        echo $errs;
        fclose($pipes[1]);
    } else {
        header('HTTP/1.0 500 Internal Server Error');
        echo "<h1>500 Internal Server Error</h1>";
        exit();
    }
    unlink($temp);
?>
<?php
    

} else {
?>
<h1>OntoLex-Lemon Validator</h1>


Enter your lexicon here:
<form action="index.php" method="post">
  <input type="radio" name="format" value="xml" checked>RDF/XML</input>
  <input type="radio" name="format" value="turtle">Turtle/N-Triples</input><br/>
  <textarea class="code-textarea" name="document">
<rdf:RDF xmlns:ontolex="http://www.w3.org/ns/lemon/ontolex#"
         xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
         xmlns:lime="http://www.w3.org/ns/lemon/lime#"
         xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#">
    <ontolex:LexicalEntry rdf:about="test">
        <ontolex:canonicalForm>
            <ontolex:Form rdf:about="Form">
                <ontolex:writtenRep xml:lang="en">foo</ontolex:writtenRep>
            </ontolex:Form>
        </ontolex:canonicalForm>
        <lime:language>eng</lime:language>
        <rdfs:label xml:lang="en">foo</rdfs:label>  
    </ontolex:LexicalEntry>
</rdf:RDF>
</textarea><br/>
  <input type="submit" name="submit" value="Validate"/>
</form>

<p><a href="ontolex-validator.py">Download validator</a></p>
<?php
}
?>
    </div>
  </body>
</html>
