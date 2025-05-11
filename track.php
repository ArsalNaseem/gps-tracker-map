<?php
$lat = $_GET['lat'] ?? null;
$lon = $_GET['lon'] ?? null;

if ($lat && $lon) {
    $file = fopen("track.csv", "a");
    fputcsv($file, [$lat, $lon], ",", '"', "\\"); // Fixed escape warning
    fclose($file);
    echo "OK";
} else {
    echo "Missing lat or lon parameters.";
}
?>
