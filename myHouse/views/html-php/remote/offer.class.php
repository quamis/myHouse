<?php

class offer{
    protected $offer = null;
    protected $localStatus = null;
    public function __construct($offer, $localStatus){
        $this->offer = $offer;
        $this->localStatus = $localStatus;
    }

    static function cleanArr($arr){
        foreach($arr as $k=>$v){
            if(!$v){
                unset($arr[$k]);
            }
        }

        return $arr;
    }

    public function getDescriptionFull(){
        return implode(". ", Array($this->offer->location, $this->offer->description));
    }
    
    public function getDescription(){
        return $this->offer->description;
    }
    public function setDescription($desc){
        $this->offer->description = $desc;
    }
    
    public function getId(){
        return $this->offer->id;
    }

    public function getStatus(){
        return ($this->localStatus!==null?$this->localStatus:$this->offer->userStatus);
    }
    
    public function setStatus($newStatus){
        $localStatuses = @json_decode(@file_get_contents("localStatuses.json"));
        if(!$localStatuses){
        	$localStatuses = new stdClass();
        }
        
        $localStatuses->{$this->getId()} = $newStatus;
        file_put_contents("localStatuses.json", json_encode($localStatuses));
        
        $this->offer->userStatus = $newStatus;
    }

    public function hasStatus($status){
        $thisStatus = $this->getStatus();
        $statuses = explode("-", $thisStatus);
        return ($status==$thisStatus || $status==$statuses[0]);
    }

    public function render(){
        $offer = $this->offer;
        $id = $offer->id;
        $status = $this->getStatus();

        $data01 = Array();
        $data01['location'] = $offer->location;
        $data01['year_built'] = $offer->year_built;
        $data01['surface_total'] = $offer->surface_total;
        $data01['surface_built'] = $offer->surface_built;
        $data01['price_per_mp_built'] = $offer->price_per_mp_built;
        $data01['price_per_mp_surface'] = $offer->price_per_mp_surface;
        $data01['rooms'] = $offer->rooms;
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
        <span class='price'>{$offer->price}</span>
        <span class='data01'>{$data01_str}</span>
        <span class='category'>{$offer->category}</span>
        <div></div>
        <span class='status'><span class='shadowed'>{$status}</span></span>
        <span class='description'>{$offer->description}</span>
        <a target="_blank" href="{$offer->url}">{$offer->url}</a>
        <span class='date addDate'>{$offer->addDate}</span>
        <span class='date updateDate'>{$offer->updateDate}</span>
        <div class='extraData-contacts'>{$contacts_str}</div>
DATA;


        echo "<div class='operations suggestedStatus-{$offer->suggestedStatus}'>";
        switch($status){
            case 'hide':
                echo <<<DATA
                    <button class="back hide" onClick="mark(this, '');"><span>&#x21E6;</span></button>
                    <button class="hide hide-badArea" onClick="mark(this, 'hide-badArea');">bad area</button>
                    <button class="hide hide-badConstruction" onClick="mark(this, 'hide-badConstruction');">bad constr.</button>
                    <button class="hide hide-badPayment" onClick="mark(this, 'hide-badPayment');">bad payment</button>
                    <button class="hide hide-auto" onClick="mark(this, 'hide-auto');">bad auto</button>
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

            case 'mark':
            case 'mark-01':
            case 'mark-02':
            case 'mark-03':
            case 'mark-04':
                echo <<<DATA
                    <button class="back None" onClick="mark(this, '');"><span>&#x21E6;</span></button>
                    <button class="mark-01" onClick="mark(this, 'mark-01');"><span>&#x2295;</span></button>
                    <button class="mark-02" onClick="mark(this, 'mark-02');"><span>&#x2299;</span></button>
                    <button class="mark-03" onClick="mark(this, 'mark-03');"><span>&#x229E;</span></button>
                    <button class="mark-04" onClick="mark(this, 'mark-04');"><span>&#x22A1;</span></button>
DATA;
                break;

            case '':        // None
                echo <<<DATA
                    <button class="todo" onClick="mark(this, 'todo');">todo</button>
                    <button class="checked" onClick="mark(this, 'checked');">checked</button>
                    <button class="hide" onClick="mark(this, 'hide');">hide</button>
                    <button class="mark-01" onClick="mark(this, 'mark-01');"><span>&#x2295;</span></button>
DATA;
                break;

            default:
                echo <<<DATA
DATA;
        } // switch

        echo "<span class='id'>{$id}</span>";
        echo "</div>";  // close the operations div

        // close the offer div
        echo "</div>";
    }
}
