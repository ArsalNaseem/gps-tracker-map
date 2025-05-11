<?php
$lat = $_GET['lat'];
$lng = $_GET['lng'];

$file = fopen("location.json", "w");
$data = array("lat" => $lat, "lng" => $lng);
fwrite($file, json_encode($data));
fclose($file);

echo "Location updated successfully!";
?>
