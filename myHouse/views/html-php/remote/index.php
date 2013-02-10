<?php

error_reporting(E_ALL ^ E_NOTICE);
ini_set('display_errors', 1);
session_start();

require("offer.class.php");
require("filters.class.php");


$offers = json_decode(file_get_contents("profile.case-valide.json"));

$localStatuses = @json_decode(@file_get_contents("localStatuses.json"));
if(!$localStatuses){
	$localStatuses = new stdClass();
}


?>

<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en">
<head>
	<title>myHouse</title>
	<META http-equiv=Content-Type content="text/html; charset=UTF-8"/>
	
	<style type='text/css'> @import url('index.css'); </style>
	
	<style type='text/css'> 
            @media screen and (max-device-width: 1024px){
                div.offer .operations{
                    margin-top: 4em;
                }
            }
	</style>
	
	
</head>
<body>


<?php
$filters = new index_filters();
$filters->setOffers($offers, $localStatuses);
$filters->setFilters(Array(
    'rpp' =>    ($_GET['rpp']?(int)$_GET['rpp']:25),
    'pg' =>     (int)$_GET['pg'],
    'status' => (string)$_GET['status'],
    'text' =>   (string)$_GET['text'],
));
$filters->filterOffers();
    
require("index.header.php");


$filteredOffers = array_slice($filters->getFilteredOffers(), $filters->getFilters()->rpp*$filters->getFilters()->pg, $filters->getFilters()->rpp);

foreach($filteredOffers as $offer){
    $offObj = new offer($offer, $localStatuses->{$offer->id});
    $offObj->render();
} // foreach

?>

<script src="http://ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>

<script>
	/**
	 * Mark an element with a new status
	*/
	function mark(elm, status){
		var id = $(elm).parents("div.offer").attr('data-id');
		$(elm).parents("div.offer").addClass('loading');
		
		jQuery.get('ajax.php', { 'id':id, 'status':status }, function(response){
			$(elm).parents("div.offer").replaceWith(response);
		});
	}
</script>

</body>
</html>
