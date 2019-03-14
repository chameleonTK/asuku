<?php

	$fp = fsockopen("localhost", 1888, $errno, $errstr, 30);
	if (!$fp) {
	    echo "$errstr ($errno)<br />\n";
	} else {


	$out = $_POST['question'];
	fwrite($fp, $out);
	echo fgets($fp, 3000);
	fclose($fp);
}


?>
