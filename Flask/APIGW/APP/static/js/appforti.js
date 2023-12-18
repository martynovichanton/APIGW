$(document).ready(function(){

    var device = "localhost:5000";
    
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
                url: "http://" + device + "/fortiapi/" + btnID,
                type: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                data: JSON.stringify({
                    "user": user,
                    "password": pass
                })
            }).then(function(data) {
                $('#log').append(JSON.stringify(data, null, 4));
                $('#log').append("\n");
                $("button").prop("disabled",false);
            });
        }
    });

    $(".whitelistsite1btn").click(function(){
        var btnID = $(this).prop("id");
        var confirmResult = confirm("Confirm " + btnID + "?");

        if (confirmResult){
            var ts = new Date();
            $("button").prop("disabled",true);
            $('#actionLog').append($(this).prop("id") + " - " + ts + "\n");

            $('#log').empty();
            var token = document.getElementById("token").value;

            var member_list = [];
            var checked_whitelist = [];
            var nameprefix = document.getElementById("nameprefix").value;
            $("input[name='whitelistsite1checkbox']:checked").each(function(){
                checked_whitelist.push($(this).val());
            });
            if (document.getElementById("memberlist").value !== ""){
                member_list = document.getElementById("memberlist").value.split(',');
            }

            $.ajax({
                url: "http://" + device + "/fortiapi/" + btnID,
                type: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                data: JSON.stringify({
                    "memberlist": member_list,
                    "whitelist": checked_whitelist,
                    "nameprefix": nameprefix,
                    "token": token
                })
            }).then(function(data) {
                $('#log').append(JSON.stringify(data, null, 4));
                $('#log').append("\n");
                $("button").prop("disabled",false);
            });
        }
    });

    $(".whitelistsite2btn").click(function(){
        var btnID = $(this).prop("id");
        var confirmResult = confirm("Confirm " + btnID + "?");

        if (confirmResult){
            var ts = new Date();
            $("button").prop("disabled",true);
            $('#actionLog').append($(this).prop("id") + " - " + ts + "\n");

            $('#log').empty();
            var token = document.getElementById("token").value;

            var member_list = [];
            var checked_whitelist = [];
            var nameprefix = document.getElementById("nameprefix").value;
            $("input[name='whitelistsite2checkbox']:checked").each(function(){
                checked_whitelist.push($(this).val());
            });
            if (document.getElementById("memberlist").value !== ""){
                member_list = document.getElementById("memberlist").value.split(',');
            }

            $.ajax({
                url: "http://" + device + "/fortiapi/" + btnID,
                type: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                data: JSON.stringify({
                    "memberlist": member_list,
                    "whitelist": checked_whitelist,
                    "nameprefix": nameprefix,
                    "token": token
                })
            }).then(function(data) {
                $('#log').append(JSON.stringify(data, null, 4));
                $('#log').append("\n");
                $("button").prop("disabled",false);
            });
        }
    });

    $(".installbtn").click(function(){
        var btnID = $(this).prop("id");
        var confirmResult = confirm("Confirm " + btnID + "?");

        if (confirmResult){
            var ts = new Date();
            $("button").prop("disabled",true);
            $('#actionLog').append($(this).prop("id") + " - " + ts + "\n");

            $('#log').empty();
            var token = document.getElementById("token").value;

            $.ajax({
                url: "http://" + device + "/fortiapi/" + btnID,
                type: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                data: JSON.stringify({
                    "token": token
                })
            }).then(function(data) {
                $('#log').append(JSON.stringify(data, null, 4));
                $('#log').append("\n");
                $("button").prop("disabled",false);
            });
        }
    });
});