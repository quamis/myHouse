<?php
/**
ye38j2ju
wt283uo311222
rqua3116 
4c35d31dc0b79
o0o092i1
7eh2rtpj4bus0
*/

require("offer.class.php");

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


<div class='filters'>
<?php
	$rpp = ($_GET['rpp']?(int)$_GET['rpp']:25);
	$pg = (int)$_GET['pg'];
	$status = (string)$_GET['status'];
	
	
	// filter the offers, remove invalid items
	$filteredOffers = Array();
	foreach($offers as $offer){
		$offObj = new offer($offer, $localStatuses->{$offer->id});
		$add = true;
		if($status){
			$add = false;
			$st = ($status=='None'?'':$status);
			if($offObj->hasStatus($st)){
				$add = true;
			}
		}
		if($add){
			$filteredOffers[] = $offer;
		}
	} // foreach



	$totalOffers = count($filteredOffers);
	$rppArr = Array(2, 5, 10, 25, 50, 100, 250, 500, 1000, 10000);
	
	$sel = "<select name='rpp' onChange=\"window.location='?rpp='+$(this).val()+''\">";
	foreach($rppArr as $v){
		$sel.=sprintf("<option %s value='%s'>%s/pag</option>", ($rpp==$v?"selected=selected":""), $v, $v);
	}
	$sel.="</select>";
	echo $sel;
	

	$statuses = Array('None', 'hide', 'todo', 'checked');
	$sel = "<select name='status' onChange=\"window.location='?rpp={$rpp}&status='+$(this).val()+''\">";
	$sel.=sprintf("<option %s value=''>-</option>", ($status==''?"selected=selected":""));
	foreach($statuses as $v){
		$sel.=sprintf("<option %s value='%s'>%s</option>", ($status==$v?"selected=selected":""), $v, $v);
	}
	$sel.="</select>";
	echo $sel;
	
	$totPg = ceil($totalOffers/$rpp);
	$sel = "<select name='pg' onChange=\"window.location='?rpp={$rpp}&status={$status}&pg='+$(this).val()+''\">";
	for($i=0; $i<$totPg; $i++){
		$sel.=sprintf("<option %s value='%s'>pag %s</option>", ($pg==$i?"selected=selected":""), $i, $i+1);
	}
	$sel.="</select>";
	echo $sel;
        
        echo "<div class='stats'>
            <table>
                <tr class='total'>
                    <td class='label'>total:</td>
                    <td class='int'>{$totalOffers}</td>
                </tr>
            </table>
        </div>";
        
?>
</div>

<?php

$filteredOffers = array_slice($filteredOffers, $rpp*$pg, $rpp);

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
