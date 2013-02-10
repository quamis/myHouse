<div class='filters'>
<?php
echo "
<table class='filters'>
    <tr>
        <td>{$filters->view_status()}</td>
        <td>{$filters->view_text()}</td>
        <td>
            <div>{$filters->view_rpp()}</div>
            <div>{$filters->view_pg()}</div>
         </td>
    </tr>
</table>

<div class='stats'>
    <table>
        <tr class='total'>
            <td class='label'>total:</td>
            <td class='int'>{$filters->getTotal()}</td>
        </tr>
    </table>
</div>";

?>
</div>
