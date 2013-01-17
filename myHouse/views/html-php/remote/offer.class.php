<?php

class offer{
	protected $offer = null;
	protected $localStatus = null;
	public function __construct($offer, $localStatus){
		$this->offer = $offer;
		$this->localStatus = $localStatus;
	}
	
	public function render(){
		$this->render_02();
	}
	
	static function cleanArr($arr){
		foreach($arr as $k=>$v){
			if(!$v){
				unset($arr[$k]);
			}
		}
		
		return $arr;
	}

	/*
	public function render_01(){
		$offer = new stdClass();
		$offer->data = new stdClass();
		$offer->data01 = new stdClass();
		$offer->contacts = new stdClass();
		$offer->data->id = "a1b2c3";
		$offer->data->status = "todo";
		$offer->data->category = "ctg";
		$offer->data->text = "text";
		$offer->data->href = "http://www.google.ro";
		$offer->data->addDate = "2000-01-01";
		$offer->data->updateDate = "2000-01-01";
		
		
		$offer->data01->location = "loc";
		$offer->data01->year_built = "1900";
		$offer->data01->surface_total = "15";
		$offer->data01->surface_built = "10";
		$offer->data01->price_per_mp_built = "5";
		$offer->data01->price_per_mp_surface = "4.5";
		$offer->data01->rooms = "2";
		$offer->data->status = "todo";
		
		$offer->contacts->phone = Array('1234', '345',);
		$offer->contacts->misc = Array('x@y');

		$o = $this->offer;
		$this->offer = $offer;
		$ret = $this->render_02();
		$this->offer = $o;
		return $ret;
	}
	*/
	
	public function getStatus(){
		return ($this->localStatus!==null?$this->localStatus:$this->offer->data->status);
	}
	public function hasStatus($status){
		$thisStatus = $this->getStatus();
		$statuses = explode("-", $thisStatus);
		return ($status==$thisStatus || $status==$statuses[0]);
	}
	
	public function render_02(){
		$offer = $this->offer;
		$id = $offer->data->id;
		$status = $this->getStatus();
		
		$data01 = Array();
		$data01['location'] = $offer->data01->location;
		$data01['year_built'] = $offer->data01->year_built;
		$data01['surface_total'] = $offer->data01->surface_total;
		$data01['surface_built'] = $offer->data01->surface_built;
		$data01['price_per_mp_built'] = $offer->data01->price_per_mp_built;
		$data01['price_per_mp_surface'] = $offer->data01->price_per_mp_surface;
		$data01['rooms'] = $offer->data01->rooms;
		$data01_str = "<span>" . implode("</span>, <span>", self::cleanArr($data01)) . "</span>";
		
		$contactsArr = Array();
		$contactsArr_str = Array();
		foreach($offer->contacts as $type=>$contactsList){
			$contactsArr[$type] = Array();
			foreach($contactsList as $c){
				$contactsArr[$type][] = $c;
			}
			
			$arr = self::cleanArr($contactsArr[$type]);
			if($arr){
				$contactsArr_str[$type] = "<span class='{$type}'>" . implode("</span>, <span class='{$type}'>", $arr) . "</span>";
			}
		}
		$contacts_str = implode(", ", $contactsArr_str);
		
		$domId = md5($id);
		echo <<<DATA
		<div class='offer {$status}' data-id='{$id}'>
			<span class='price'>{$offer->data->price}</span>
			<span class='data01'>{$data01_str}</span>
			<span class='category'>{$offer->data->category}</span>
			<div></div>
			<span class='status'><span class='shadowed'>{$status}</span></span>
			<span class='description'>{$offer->data->text}</span>
			<a target="_blank" href="{$offer->data->href}">{$offer->data->href}</a>
			<span class='date addDate'>{$offer->data->addDate}</span>
			<span class='date updateDate'>{$offer->data->updateDate}</span>
			<div class='extraData-contacts'>{$contacts_str}</div>
DATA;


		echo "<div class='operations'>";
		switch($status){
                    case 'hide':
                        echo <<<DATA
						<button class="back hide" onClick="mark(this, '');"><span>&#x21E6;</span></button>
                        <button class="hide hide-badArea" onClick="mark(this, 'hide-badArea');">bad area</button>
                        <button class="hide hide-badConstruction" onClick="mark(this, 'hide-badConstruction');">bad constr.</button>
                        <button class="hide hide-badPayment" onClick="mark(this, 'hide-badPayment');">bad payment</button>
DATA;
                    break;
                        
                    case 'todo':
                        echo <<<DATA
                        <button class="back None" onClick="mark(this, '');"><span>&#x21E6;</span></button>
                        <button class="todo todo-call" onClick="mark(this, 'todo-call');">todo:call</button>
                        <button class="todo todo-talk" onClick="mark(this, 'todo-talk');">todo:talk</button>
                        <button class="todo todo-view" onClick="mark(this, 'todo-view');">todo:view</button>
DATA;
                    break;
                    
                    case 'todo-call':
                    case 'todo-talk':
                    case 'todo-view':
                        echo <<<DATA
                        <button class="back todo" onClick="mark(this, 'todo');"><span>&#x21E6;</span></button>
DATA;
                    break;
                        
                    
                    case 'checked':
                        echo <<<DATA
                        <button class="back None" onClick="mark(this, '');"><span>&#x21E6;</span></button>
                        <button class="checked-ok" onClick="mark(this, 'checked-ok');">ok</button>
                        <button class="checked-notok" onClick="mark(this, 'checked-notok');">not ok</button>
DATA;
                    break;
                    
                    case 'checked-ok':
                    case 'checked-notok':
                        echo <<<DATA
                        <button class="back checked" onClick="mark(this, 'checked');"><span>&#x21E6;</span></button>
DATA;
                        break;
                        
                    case '':        // None
                        echo <<<DATA
                        <button class="todo" onClick="mark(this, 'todo');">todo</button>
                        <button class="checked" onClick="mark(this, 'checked');">checked</button>
                        <button class="hide" onClick="mark(this, 'hide');">hide</button>
DATA;
                    break;
                        
                    default:
                        echo <<<DATA
DATA;
		} // switch
		
		echo "<span class='id'>{$id}</span>";
		echo "</div>";	// close the operations div
		
		// close the offer div
		echo "</div>";
	}
}