<?php

error_reporting(E_ALL ^ E_NOTICE);
ini_set('display_errors', 1);
session_start();

require("offer.class.php");
require("filters.class.php");

$_SESSION['source'] = ($_GET['source']?$_GET['source']:$_SESSION['source']);
if(!$_SESSION['source']){
    $_SESSION['source'] = 'case-vile';
}
$offers = json_decode(file_get_contents("profile.{$_SESSION['source']}.json"));

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

$autoFilters = Array(
    'case-vile' => Array(
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Pantelimon comuna" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "comuna Pantelimon" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "BOLINTIN Deal" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Clinceni" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Calugareni" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Moara Vlasiei" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Constanța," ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Corbeanca," ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "TARTASESTI," ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "BERCENI comuna" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Dambovita" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Tamadau" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "BUSTENI" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Domnesti" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Dragomiresti" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "ADUNATII Copaceni" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Chiajna" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "BUTURUGENI" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "CIOROGARLA" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "CORNETU" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Vidra" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "DARVARI" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Ilfov" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Comuna Berceni" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Berceni Comuna" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "BRAGADIRU" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Titu" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "VALEA Doftanei" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Campina" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Brebu" ),
    
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "ANDRONACHE" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Rahova" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Teius" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Margeanului" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Luica" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Voluntari" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "MIHAILESTI" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Buftea Crevedia" ),
    
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Ialomita" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Brasov" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Vrancea" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Calarasi" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Focsani" ),
    
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "Apartament" ),
        array( 'onStatus'=>Array(''), 'newStatus'=>'hide-auto', 'text' => "[0-9]+km de (Bucuresti|buc|centru)" ),
    ),
);



$filters = new index_filters();
$filters->setOffers($offers, $localStatuses);
$filters->setFilters(Array(
    'rpp' =>    ($_GET['rpp']?(int)$_GET['rpp']:25),
    'pg' =>     (int)$_GET['pg'],
    'status' => (string)$_GET['status'],
    'text' =>   (string)$_GET['text'],
    'source' => $_SESSION['source'],
    'autofilter' => (array)$autoFilters[$_SESSION['source']],
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
