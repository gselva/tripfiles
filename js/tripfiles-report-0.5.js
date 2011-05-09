
        $(document).ready(function() {
                //attach datepicker to field		
		$("#startdatepicker").datepicker();	
                $("#enddatepicker").datepicker();
		
		//select scope change
		$("#select_scope").change(function() {
			$("#select_specific_scope_box").show();
		});
        });


        function printReport() {
                //$('#print-remarks').show();
		/*	var report =  window.open('','ReportWindow','width=1200,height=800');
			var style = '<link type="text/css" rel="stylesheet" href="/stylesheets/report.css" /><link type="text/css" rel="stylesheet" href="/stylesheets/print.css" media="print"/>'
			$('#update_actions').hide();
			var html = '<html><head><title>Print Your Report</title>'+style+'</head><body>'+ $("#report-panel").html()+'</body></html>';
			report.document.open();
			report.document.write(html);
			report.document.close();
			$('#update_actions').show(); */
			
                $("#report-panel").jqprint({ operaSupport: true });
                $('#print-remarks').hide();
        }

	function downloadReport(formid) {
                var start = $('#startdatepicker').val();
                var end = $('#enddatepicker').val();
                if (start.length < 10 || end.length <10) {
                        setAppNotification({
			"app_notification": "Please select dates for report",
			"app_notification_type": "app_error"
			});
                        return false;
                }
		
		$(formid).submit();
		
		return false;		
	}
        function showReport() {
                var start = $('#startdatepicker').val();
                var end = $('#enddatepicker').val();
		var user_email = $('#user_email').val();
                if (start.length < 10 || end.length <10) {
                        setAppNotification({
			"app_notification": "Please select dates for report",
			"app_notification_type": "app_error"
			});
                        return false;
                }
                var reporturl = "http://"+window.location.hostname+"/report"

        if (window.location.hostname == 'localhost' || window.location.hostname == '192.168.1.66'
	|| window.location.hostname == '192.168.1.69') {
                reporturl = "http://"+window.location.hostname+":8080/report"			
        }
        //load the report
        $.ajax({
                type: 'POST',
                url: reporturl,
                data: { 'startdate': start, 'enddate': end, 'user_email': user_email },
                beforeSend:function(){
                        // this is where we append a loading image
                        $('#report-panel').html('<div id="#report-results-box"><img src="/images/loading.gif" alt="Loading..." /></div>');
                },
                success:function(data){
                        // successful request; do something with the data
    
                        $('#report-panel').html(data);
                        $('#report-results-box').fadeIn(1000);
                        $('#print-button').show();
                },
                error:function(){
                        // failed request; give feedback to user
                        $('#report-panel').html('<p class="app_error">We have a minor glitch. Please try again in a few moments. </p>');
                        $('#print-button').hide();
                }
        });	
}

        function modifyTrip(id) {
                var form_trip_key = '#'+id;
                $(form_trip_key).submit();
        }


        function deleteTrip(id) {
                var idstr = '#trip'+id
                //send ajax request to delete		
                var deleteurl = "http://"+window.location.hostname+"/deletetrip"

        if (window.location.hostname == 'localhost' || window.location.hostname == '192.168.1.66'
        	|| window.location.hostname == '192.168.1.69') {
                deleteurl = "http://"+window.location.hostname+":8080/deletetrip"			
        }

        $(idstr).html('<td colspan=9 style="align: center;"><span style="font-size: 2em; font-weight: strong;">Deleting... <img src="/images/loading.gif" alt="Deleting..." /></span></td>').delay(1000).fadeOut(400);

        $.ajax({
                type: 'POST',
                url: deleteurl,
                data: { 'trip_key': id },
                beforeSend:function(){
                        // this is where we append a loading image
                    $(idstr).html('<td colspan=9 style="align: center;"><span style="font-size: 2em; font-weight: strong;">Deleting... <img src="/images/loading.gif" alt="Deleting..." /></span></td>');
                },
                success:function(data){
	                setAppNotification(data);
                    $(idstr).html('<td colspan=9 style="align: center;"><span style="font-size: 2em; font-weight: strong;">Deleted</span></td>').delay(400).fadeOut(1000);
                    },
                    error:function(){
                        // failed request; give feedback to user
                        setAppNotification({
                            "app_notification": "We have a minor glitch. Please try again in a few moments",
                            "app_notification_type": "app_error"
                        });
                        $("#app_notification").show().delay(2000).fadeOut(800);
                    	}
	});			
//update report total
showReport();
}
