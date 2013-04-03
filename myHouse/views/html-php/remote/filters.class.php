<?php

class index_filters{
    protected $offers = Array();
    protected $localStatuses = Array();

    protected $filterdOffers = Array();

    protected $filters = Array();

    function getFilters(){
        $obj = new stdClass();
        foreach($this->filters as $k=>$v){
            $obj->{$k} = $v;
        }

        return $obj;
    }

    function setFilters($filters){
        $this->filters = $filters;
    }

    function setOffers($offers, $localStatuses){
        $this->offers = $offers;
        $this->filterdOffers = Array();
        $this->localStatuses = $localStatuses;
    }

    public function filterOffers(){
        // filter the offers, remove invalid items
        $filteredOffers = Array();
        foreach($this->offers as $offer){
            $offObj = new offer($offer, $this->localStatuses->{$offer->id});
            $add = true;
            
            // this has to be the first one
            if($add && $this->filters['autofilter']){
                $desc = $offObj->getDescriptionFull();
                foreach($this->filters['autofilter'] as $blidx=>$bl){
                    if(in_array($offObj->getStatus(), $bl['onStatus'])){
                        if($offObj->getStatus()!=$bl['newStatus']){
                            if($bl['regex']){
                                $regex = $bl['regex'];
                            }elseif($bl['text']){
                                $regex = "/[^[:alnum:]](?P<match>{$bl['text']})[^[:alnum:]]/ui";
                            }else{
                                throw new Exception("No matching function specified for autofilter[{$blidx}]");
                            }
                            
                            if(preg_match($regex, $desc, $m)){
                                $offObj->setStatus($bl['newStatus']);
                            }
                        }
                    }
                }
            }
            
            
            if($add && $this->filters['status']){
                $add = false;
                $st = ($this->filters['status']=='None'?'':$this->filters['status']);
                if($offObj->hasStatus($st)){
                    $add = true;
                }
            }

            if($add && $this->filters['text']){
                $add = false;

                $filteredField = "description";
                $regex = "";
                $text = $this->filters['text'];

                $textAdvanced = explode(":", $text);
                if($textAdvanced[0] && $textAdvanced[1]){
                    $filteredField = $textAdvanced[0];
                    
                    $text = implode(":", array_slice($textAdvanced, 1));
                }

                if($text[0]=="/"){
                    $regex = $text;    // custom, advanced matcher
                } else {
                    $regex = "/[^[:alnum:]](?P<match>{$text})[^[:alnum:]]/ui";
                }

                switch($filteredField){
                    case 'description':
                        $desc = $offObj->getDescriptionFull();
                        if(preg_match($regex, $desc, $m)){
                            $desc = str_replace($m[0], "<span class='highlight'>{$m[0]}</span>", $desc);
                            $offObj->setDescription($desc);

                            $add = true;
                        }
                    break;
                    
                    case 'status':
                        $desc = $offObj->getStatus();
                        $add = false;
                        if(preg_match($regex, $desc, $m)){
                            $add = true;
                        }
                    break;
                    

                    case 'id':
                        $desc = $offObj->getId();
                        if(preg_match($regex, $desc, $m)){
                            $add = true;
                        }
                    break;

                    default:
                        throw new Exception("Invalid filter field '{$filteredField}' specified");
                }
            }
            
            if($add){
                $filteredOffers[] = $offer;
            }
        } // foreach

        $this->filteredOffers = $filteredOffers;
    }

    function getFilteredOffers(){
        return $this->filteredOffers;
    }

    function getTotal(){
        return count($this->filteredOffers);
    }

    function view_text(){
        $sel = "<input type='text' name='text' value='{$this->filters['text']}' onChange=\"window.location='?rpp={$this->filters['rpp']}&status={$this->filters['status']}&text='+$(this).val()+''\">";
        return $sel;
    }
    function view_status(){
        $statuses = Array('None', 'hide', 'todo', 'todo-call', 'checked', 'mark');
        $sel = "<select name='status' onChange=\"window.location='?rpp={$this->filters['rpp']}&text={$this->filters['text']}&status='+$(this).val()+''\">";
        $sel.=sprintf("<option %s value=''>-</option>", ($this->filters['status']==''?"selected=selected":""));
        foreach($statuses as $v){
            $sel.=sprintf("<option %s value='%s'>%s</option>", ($this->filters['status']==$v?"selected=selected":""), $v, $v);
        }
        $sel.="</select>";
        return $sel;
    }


    function view_rpp(){
        $rppArr = Array(2, 5, 10, 25, 50, 100, 250, 500, 1000, 5000);

        $sel = "<select name='rpp' onChange=\"window.location='?rpp='+$(this).val()+'&status={$this->filters['status']}&text={$this->filters['text']}'\">";
        foreach($rppArr as $v){
            $sel.=sprintf("<option %s value='%s'>%s/pag</option>", ($this->filters['rpp']==$v?"selected=selected":""), $v, $v);
        }
        $sel.="</select>";
        return $sel;
    }
    function view_pg(){
        $totPg = ceil($this->getTotal()/$this->filters['rpp']);
        $sel = "<select name='pg' onChange=\"window.location='?rpp={$this->filters['rpp']}&status={$this->filters['status']}&text={$this->filters['text']}&pg='+$(this).val()+''\">";
        for($i=0; $i<$totPg; $i++){
            $sel.=sprintf("<option %s value='%s'>pag %s</option>", ($this->filters['pg']==$i?"selected=selected":""), $i, $i+1);
        }
        $sel.="</select>";
        return $sel;
    }
}
