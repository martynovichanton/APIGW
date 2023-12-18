$(document).ready(function(){
    $("#tableLog").hide();

    var device = "localhost:8000";
    
    $(".tokensbtn").click(function(){
        var btnID = $(this).prop("id");
        var confirmResult = confirm("Confirm " + btnID + "?");

        if (confirmResult){
            var ts = new Date();
            $("button").prop("disabled",true);
            $('#actionLog').append($(this).prop("id") + " - " + ts + "\n");

            $('#log').empty();
            var user = document.getElementById("user").value;
            var pass = document.getElementById("pass").value;
            $.ajax({
                url: "http://" + device + "/f5api/" + btnID,
                type: "GET",
                headers: {
                    "Content-Type": "application/json",
                    "user": user,
                    "password": pass
                }
            }).then(function(data) {
                $('#log').append(JSON.stringify(data, null, 4));
                $('#log').append("\n");
                $("button").prop("disabled",false);
            });
        }
    });

    $(".commandsbtn").click(function(){
        var btnID = $(this).prop("id");
        var confirmResult = confirm("Confirm " + btnID + "?");

        if (confirmResult){
            var ts = new Date();
            $("button").prop("disabled",true);
            $('#actionLog').append($(this).prop("id") + " - " + ts + "\n");

            $('#log').empty();
            var token = document.getElementById("token").value;
            $.ajax({
                url: "http://" + device + "/f5api/" + btnID,
                type: "PATCH",
                headers: {
                    "Content-Type": "application/json",
                    "token": token
                }
            }).then(function(data) {
                $('#log').append(JSON.stringify(data, null, 4));
                $('#log').append("\n");
                $("button").prop("disabled",false);
            });
        }
    });

    $(".statsbtn").click(function(){
        var btnID = $(this).prop("id");
        var confirmResult = confirm("Confirm " + btnID + "?");

        if (confirmResult){
            var statsURL = btnID.replace("_stats", "_show_stats");
            var configURL = btnID.replace("_stats", "_show_config")
            var ts = new Date();
            $("button").prop("disabled",true);
            $('#actionLog').append($(this).prop("id") + " - " + ts + "\n");

            $("#tableLog").hide();
            $('#tableLog tbody').empty();
            $('#log').empty();

            var token = document.getElementById("token").value;
            $.when(
                $.ajax({
                    url: "http://" + device + "/f5api/" + statsURL,
                    type: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        "token": token
                    }}), 
                $.ajax({
                    url: "http://" + device + "/f5api/" + configURL,
                    type: "GET",
                    headers: {
                        "Content-Type": "application/json",
                        "token": token
                    }})
            ).then(function (stats, configs) {
                $('#log').empty();

                $('#log').append(JSON.stringify(stats[0], null, 4));
                $('#log').append("\n\n\n\n");
                $('#log').append("****************************************************************");
                $('#log').append("\n\n\n\n");
                $('#log').append(JSON.stringify(configs[0], null, 4));
                $('#log').append("\n");

                // var table = `
                //     <table class="table table-sm" id="tableLog"> 
                //         <thead> 
                //             <th>Pool Name</th>
                //             <th>IP</th> 
                //             <th>Node Name</th>
                //             <th>Availability</th>
                //             <th>Enabled</th>
                //             <th>Conns</th>
                //             <th>Prio</th>
                //         </thead>
                //         <tbody>
                //         </tbody>
                //     </table> 
                // `
                // if ($("#tableLog").length <= 0){
                //     $('#cards').append(table);
                // }
                
                stats[0]["dataset"].forEach(function (pool_stat, pool_index) {
                    //var member_index = 0;
                    for (var entry in pool_stat.entries){
                        var pool_name = pool_stat["entries"][entry]["nestedStats"]["entries"]["poolName"]["description"];
                        var addr = pool_stat["entries"][entry]["nestedStats"]["entries"]["addr"]["description"];
                        var node_name = pool_stat["entries"][entry]["nestedStats"]["entries"]["nodeName"]["description"];
                        var availability_status = pool_stat["entries"][entry]["nestedStats"]["entries"]["status.availabilityState"]["description"];
                        var enabled_state = pool_stat["entries"][entry]["nestedStats"]["entries"]["status.enabledState"]["description"];
                        var port = pool_stat["entries"][entry]["nestedStats"]["entries"]["port"]["value"];
                        var conns = pool_stat["entries"][entry]["nestedStats"]["entries"]["serverside.curConns"]["value"];
                        var prio = 0;
                        
                        //member_index++;
                        //var row = '<tr><td>' + pool_name + '</td><td>' + addr + '</td><td>' + node_name + '</td><td>' + availability_status + '</td><td>' + enabled_state + '</td><td class="active">' + conns + '</td><td>' + configs[0][pool_index]["items"][member_index]["priorityGroup"] + '</td></tr>';

                        //find the pool member config fullPath with the name:port from stats member
                        //from config:
                        //"fullPath":"/Partition01/srv-site-1:443"
                        //from stats;
                        // "nodeName":{
                        //     "description":"/Partition01/srv-site-1"
                        //  }
                        //"port":{
                        //  "value":443
                        // }
                        configs[0]["dataset"][pool_index]["items"].forEach(function (member_config, index) {
                            if(node_name + ":" + port == member_config["fullPath"]){
                                prio = member_config["priorityGroup"];
                            }
                        });
                    
                        var row = '<tr><td>' + pool_name + '</td><td>' + addr + '</td><td>' + node_name + '</td><td>' + availability_status + '</td><td>' + enabled_state + '</td><td>' + conns + '</td><td>' + prio + '</td></tr>';
                        
                        $('#tableLog tbody').append(row);
                    }
                });

                addColor();
                $("#tableLog").show();
                $("button").prop("disabled",false);
            });
        }
    });

    $('#tableLog').on('click', 'td', function() {
        var tablelog = document.getElementById('tableLog');
        var cells = tablelog.getElementsByTagName('td');
        var rowId = this.parentNode.rowIndex;
        var rowsNotSelected = tablelog.getElementsByTagName('tr');
        for (var row = 0; row < rowsNotSelected.length; row++) {
            rowsNotSelected[row].classList.remove("rowSelected");
        }
        var rowSelected = tablelog.getElementsByTagName('tr')[rowId];
        rowSelected.className = "rowSelected";
        msg = 'Poolname: ' + rowSelected.cells[0].innerHTML;
        msg += '\nIP: ' + rowSelected.cells[1].innerHTML;
        msg += '\nNodename: ' + rowSelected.cells[2].innerHTML;
        msg += '\nAvailability: ' + rowSelected.cells[3].innerHTML;
        msg += '\nEnabled: ' + rowSelected.cells[4].innerHTML;
        msg += '\nConns: ' + rowSelected.cells[5].innerHTML;
        msg += '\nPrio: ' + rowSelected.cells[6].innerHTML;
        msg += '\nclicked: ' + this.innerHTML;
        console.log(msg);
    });

    function addColor(){
        //color connections
        $("#tableLog tr td:nth-child(6)").each(function(){
            var cellValue = $(this).text();
            if(cellValue > 0){
                $(this).addClass("activeConns");
            }
        });

        //color enabled
        $("#tableLog tr td:nth-child(5)").each(function(){
            var cellValue = $(this).text();
            if(cellValue.includes("disabled")){
                $(this).addClass("disabledMember");
            }
        });

        //color availability
        $("#tableLog tr td:nth-child(4)").each(function(){
            var cellValue = $(this).text();
            if(cellValue.includes("offline")){
                $(this).addClass("offlineMember");
            }
        });
    }

    //highlight_row();
    // function highlight_row() {
    //     var table = document.getElementById('display-table');
    //     var cells = table.getElementsByTagName('td');
    //     for (var i = 0; i < cells.length; i++) {
    //         var cell = cells[i];
    //         cell.onclick = function () {
    //             var rowId = this.parentNode.rowIndex;
    //             var rowsNotSelected = table.getElementsByTagName('tr');
    //             for (var row = 0; row < rowsNotSelected.length; row++) {
    //                 rowsNotSelected[row].classList.remove("rowSelected");
    //                 rowsNotSelected[row].classList.remove('selected');
    //             }
    //             var rowSelected = table.getElementsByTagName('tr')[rowId];
    //             rowSelected.className = "rowSelected";
    //             rowSelected.className += " selected";
    //             msg = 'ID: ' + rowSelected.cells[0].innerHTML;
    //             msg += '\nName: ' + rowSelected.cells[1].innerHTML;
    //             msg += '\nClicked: ' + this.innerHTML;
    //             console.log(msg);
    //         }
    //     }
    // }
    //static table example
    // <table id="display-table" class="table">
    //     <thead>
    //         <th>ID</th>
    //         <th>Company</th>
    //     </thead>
    //     <tbody>
    //         <tr>
    //             <td>100</td>
    //             <td>Abc</td>
    //         </tr>
    //         <tr>
    //             <td>101</td>
    //             <td>Def</td>
    //         </tr>
    //         <tr>
    //             <td>102</td>
    //             <td>Ghi</td>
    //         </tr>
    //     </tbody>
    // </table>
});