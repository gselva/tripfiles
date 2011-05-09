/* google maps display */	  
var rendererOptions = {
	draggable: true
};
var directionsDisplay = new google.maps.DirectionsRenderer(rendererOptions);;
var directionsService = new google.maps.DirectionsService();
var map, geocoder;

var uk = new google.maps.LatLng(52.762892,-2.120361);

function initialize() {
	geocoder = new google.maps.Geocoder();
	
	var myOptions = {
	  zoom: 7,
	  mapTypeId: google.maps.MapTypeId.ROADMAP,
	  center: uk
	};
	
	map = new google.maps.Map(document.getElementById("map_canvas"), myOptions);
	directionsDisplay.setMap(map);
	
	directionsDisplay.setPanel(document.getElementById("directionsPanel"));

	google.maps.event.addListener(directionsDisplay, 'directions_changed', function() {
	  computeTotalDistance(directionsDisplay.directions);
	});
	
	/* Try W3C Geolocation (Preferred)*/
	if(navigator.geolocation) {
		browserSupportFlag = true;
		navigator.geolocation.getCurrentPosition(function(position) {
		initialLocation = new google.maps.LatLng(position.coords.latitude,position.coords.longitude);
		map.setCenter(initialLocation);
		}, function() {
			handleNoGeolocation(browserSupportFlag);
		});
	} else {
		browserSupportFlag = false;
		handleNoGeolocation(browserSupportFlag);
	}
	
	function handleNoGeolocation(errorFlag) {
		if (errorFlag == true) {
			initialLocation = uk;
		} else {
			initialLocation = uk;
		}
		map.setCenter(initialLocation);
	}

	$('#app_panel').hide().delay(450).fadeIn(400);
	
}

function recalcRoute() {
	var values = {};
	var param = [];
	
	$('.waypoint_input input:visible').each(
	function(j, elem) {
		var fieldname = $(elem).attr('name');
		var fieldvalue = $(elem).attr('value');
		validateWaypoint(fieldvalue, fieldname);
		values[fieldname] = fieldvalue;
		param.push(fieldvalue)
	} 
	);
	
	calcRoute(param);
}
	
function calcRoute(locations) {
	start = "London";
	end = "London";
	if (locations.length > 1) {
		start = locations[0];
		end = locations[locations.length-1];
	} else {
		return;
	}
	
	var inbetweens = []
	for (i = 1; i < locations.length-1; i++) {
		inbetweens.push({location: locations[i]});
	}
	
	var request = {
		origin: start,
		destination: end,
		waypoints: inbetweens,
		travelMode: google.maps.DirectionsTravelMode.DRIVING,
		unitSystem: google.maps.DirectionsUnitSystem.IMPERIAL
	};
	
	directionsService.route(request, function(response, status) {
		if (status == google.maps.DirectionsStatus.OK) {
			directionsDisplay.setDirections(response);
			$('#directionsPanel').attr('isvalid', '1');			
		} else {
			$('#directionsPanel').attr('isvalid', '0');
		}
	});
}
		 
function computeTotalDistance(result) {
	var total_meters = 0;
	var myroute = result.routes[0];
	for (i = 0; i < myroute.legs.length; i++) {
	  total_meters = total_meters + myroute.legs[i].distance.value;
	  var legindex = i+1;
	  var legstr = '#waypoint_leg'+legindex;
	  var distance_miles = (myroute.legs[i].distance.value * 0.000621371192).toFixed(1);
	  var distancehtml = "<input type='text' name='leg"
					+legindex+"' class='leg-hidden-input' id='leg"+legindex
					+"' value='"
					+distance_miles+"' size=2 />";
		$(legstr).html(distancehtml);
	}
	
	var milestotal = (total_meters * 0.000621371192).toFixed(1);
	$('#total_miles').attr('value', milestotal); 
}   
		  
		  
function removeNotification() {
	$('#app_notification').remove();
}


function removeWaypoint(windex) {
	var waypoint='#waypoint'+windex;
	var values = [];
	var visible_count = $('.waypoint_input input:visible').length;

	//save the values before pushing down
	$('.waypoint_input input:visible').each(
		function(i, elem) {
			if(i>windex) {
				values.push($(elem).attr('value'));						
			}
		}
		
	);
	//console.log(values);
	
	//hide address box at the bottom
	if(visible_count<11) {
		$('#waypoint'+(visible_count-1)).hide();
	}
	
	//push the saved values down by one
	var values_index = 0;
	$('.waypoint_input input:visible').each(
		function(j, elem) {
			if(j>=(windex)) {
				$(elem).attr('value', values[values_index]);	
				values_index = values_index +1;
			} 
		}
		
	);
}
		 

function addWaypoint(windex) {
	var waypoint='#waypoint'+windex;
	var values = [];
	var visible_count = $('.waypoint_input input:visible').length;

	//save the values before pushing down
	$('.waypoint_input input:visible').each(
		function(i, elem) {
			if(i>windex) {
				values.push($(elem).attr('value'));						
			}
		}
		
	);

	//show a new address box at the bottom
	if(visible_count<10) {
		$('#waypoint'+visible_count).show();
	}
	
	//push the saved values down by one
	var values_index = 0;
	$('.waypoint_input input:visible').each(
		function(j, elem) {
			if(j==(windex+1)) {
				$(elem).attr('value', '');
			}
			if(j>(windex+1)) {
				$(elem).attr('value', values[values_index]);	
				values_index = values_index +1;
			} 
		}
		
	);

}

		
function clearTrip() {
	$('#datepicker').val('');
	$('#triplabel').val('');
	$('#total_miles').val('');
	$('#directionsPanel').hide();
	$('#trip_key').remove();
	
	$('#label_parking_expenses').val('');
	$('#other_expenses_charges_pound').val('');
	$('#other_expenses_charges_pence').val('');
	$('#other_no_passengers').val('');
	$('#other_passenger_miles').val('');
	
	
	
	$('.waypoint_input input').each(
		function(j, elem) {
				$(elem).attr('value', '');	
		}		
	);
	

}
		


function validateField(name, value) {
	var re = /^\d*$/;
	var name_re = /cost|other/;
	if (name_re.test(name)) {
		if(!re.test(value)) {
			return false;
		}
	} 
	
	if(name==='tripdate') {
		if(value.length != 10) {
			$('#datepicker').css("border","1px solid red");
            var notification = '{"app_notification": "Please pick a date for the trip", "app_notification_type": "app_error"}';
		    setAppNotification(notification);
			return false;
		} else {
			$('#datepicker').css("border","1px solid green");
		}
	}
	
	if (name==='cost_per_mile_pence') {
		value = value.replace(/^\s+|\s+$/g, '') ;
		if(!re.test(value)) {
			return false;
		}
	} 
	
	return true;
}

function validateWaypoint(address, elementId) {
	geocoder.geocode({'address': address }, function(results, status) {
	var elemstr = '#'+elementId;
	switch(status) {
		case google.maps.GeocoderStatus.OK:
			/* $(elemstr).val(results[0].formatted_address); */
			$(elemstr).removeAttr('style');			
			$(elemstr).attr('isvalid', '1');
			$('#app_notification').empty().hide();
			break;
		case google.maps.GeocoderStatus.ZERO_RESULTS:
			$(elemstr).css("border","1px solid red");
			$(elemstr).attr('isvalid', '0');
			var notification = '{"app_notification": "Incorrect date/addresses. Please correct the fields marked red above.", "app_notification_type": "app_error"}';			
			setAppNotification(notification);			
			break;
		default:
			/* $(elemstr).css("border","1px solid red"); */
			$(elemstr).attr('isvalid', '0');
			var notification = '{"app_notification": "Incorrect date/addresses. Please correct the fields marked red above.", "app_notification_type": "app_error"}';			
			setAppNotification(notification);			
			break;
		}
	});
	return true; 
}  

function waypointsValidated(delay, timeout) {
	var directionsValid = $('#directionsPanel').attr('isvalid');
	if(directionsValid=='1') {
		return true;
	}
	
	return false;
}


function saveTrip() {
	var values = {};
	var isvalid = true;
	$.each($('#tripForm').serializeArray(), function(i, field) {
		var re = /input|leg|tripdate|triplabel|trip_key|cost|other|label|mode|total_miles/;
		if(re.test(field.name)) {
			var field_id = '#'+field.name; 
			$(field_id).removeAttr('style');	
			
			if (validateField(field.name, field.value)) {
				values[field.name] = field.value;
			} else {
				if(field.name==='tripdate') {
					$('date_input').css('border","1px solid red');
				} else {
					$(field_id).css('border","1px solid red');
				}
				isvalid = false;
			}
		}
	});
	
	
	if (!isvalid) {
		setAppNotification({"app_notification": "Incorrect value entered for optional fields. Please correct fields marked red and try again.", 
						"app_notification_type": "app_error"});
		return false;
	} else {
		$('#app_notification').empty().hide();		
	}

	
	var saveurl = "http://"+window.location.hostname+"/save"

	if (window.location.hostname == 'localhost'  || window.location.hostname == '192.168.1.66'
		|| window.location.hostname == '192.168.1.69') {
		saveurl = "http://"+window.location.hostname+":8080/save"			
	}
	
	/* save the trip */
	$.ajax({
	  type: 'POST',
	  url: saveurl,
	  data: values,
	  beforeSend:function(){
	    /* this is where we append a loading image */
	    $('#app_notification').html('<div class="loading"><p>Saving .. <img src="/images/loading.gif" alt="Saving..." /></p></div>').show();
	  },
	  success:function(data){
		setAppNotification(data);
	  },
	  error:function(){
	    setAppNotification({
	    "app_notification": "We have a minor glitch in saving your trip. Please try again in a few moments",
	    "app_notification_type": "app_error"}
	    );
	  }
	});	
}

