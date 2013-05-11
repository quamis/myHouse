<?php

session_start();

require("offer.class.php");

$offers = json_decode(file_get_contents("profile.{$_SESSION['source']}.json"));

$id = $_GET['id'];
$status = $_GET['status'];

foreach($offers as $offer){
	if($id == $offer->id){
		$offObj = new offer($offer, $status);
		$offObj->setStatus($status);
		$offObj->render();
		
		break;
	}
}
