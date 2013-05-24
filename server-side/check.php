<?php
header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0, post-check=0, pre-check=0");
header("Pragma: no-cache");

$IMG = array('on' => 'vpn-on.jpg', 'off' => 'vpn-off.jpg');
?>
<html>
	<head>
		<meta http-equiv="refresh" content="5">
	</head>
	<body>
	<img src="/check/<?php if ( $_SERVER['REMOTE_ADDR'] == "171.33.130.90" ) {
	        echo $IMG["on"];
		}
		else {
		        echo $IMG["off"];
		}
		?>">
		<p style='font-family:sans-serif;margin-top:10px;margin-left:300px;font-size:12pt'>
		Your IP address is: <?= $_SERVER['REMOTE_ADDR'] ?> (<?php 
		echo preg_replace("/GeoIP Country Edition: /", "", shell_exec("geoiplookup " . $_SERVER['REMOTE_ADDR'])); 
		?>)
		</p>
		</body>
<html>