<?php
require("offer.class.php");

$offers = json_decode(file_get_contents("profile.case-valide.json"));

$localStatuses = @json_decode(@file_get_contents("localStatuses.json"));
if(!$localStatuses){
	$localStatuses = new stdClass();
}

$id = $_GET['id'];
$status = $_GET['status'];

$localStatuses->{$id} = $status;

file_put_contents("localStatuses.json", json_encode($localStatuses));

foreach($offers as $offer){
	if($id == $offer->id){
		$offObj = new offer($offer, $status);
		$offObj->render();
		
		break;
	}
}
