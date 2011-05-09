
/*alphabets for digits*/
digit_alpha_dict = {'0': 'A', '1': 'B', '2': 'C', '3': 'D', '4': 'E', '5': 'F', '6': 'G', '7': 'H', '8': 'I', '9': 'J', '10': 'K' };

function showHide(id) {
$(id).toggle('fast');
}
	
function submitForm(formid) {
	$(formid).submit();
	return false;
}

/* Numeric only control handler
http://stackoverflow.com/questions/995183/how-to-allow-only-numeric-0-9-in-html-inputbox-using-jquery
*/
jQuery.fn.ForceNumericOnly =
function()
{
    return this.each(function()
    {
	$(this).keydown(function(e)
	{
	    var key = e.charCode || e.keyCode || 0;
	    /* allow backspace, tab, delete, arrows, numbers and keypad numbers ONLY */
	    return (
		key == 8 || 
		key == 9 ||
		key == 46 ||
		(key >= 37 && key <= 40) ||
		(key >= 48 && key <= 57) ||
		(key >= 96 && key <= 105));
	})
    })
};	
	
/* attach datepicker to field */	
$(document).ready(function() {
	$("#datepicker").datepicker();
	
	$('#cost_per_mile_pound').ForceNumericOnly();		
	$('#cost_per_mile_pence').ForceNumericOnly();
	$('#other_expenses_charges_pound').ForceNumericOnly();
	$('#other_expenses_charges_pence').ForceNumericOnly();
	$('#other_no_passengers').ForceNumericOnly();
	$('#other_passenger_miles').ForceNumericOnly();			

	/* tooltips */
	$('#login-tip').qtip({
		 content: "Click on Login button to login into TripFiles using your google login. If you don't have a google login, you can register one for free by clicking on this button.", 
		style: 'dark', 
		position: {
		      corner: {
			 target: 'bottomLeft',
			 tooltip: 'topRight'
		      }
		   }		 
	      });
	      
	$('#register-tip').qtip({
		 content: "TripFiles registration is free during our Beta testing. Please register to save your trips and get mileage reports. ", 
		style: 'dark', 
		position: {
		      corner: {
			 target: 'bottomLeft',
			 tooltip: 'topRight'
		      }
		   }		 
	      });

	$('#account-tip').qtip({
		 content: "Click Account button to update your account details. ", 
		style: 'dark', 
		position: {
		      corner: {
			 target: 'bottomLeft',
			 tooltip: 'topRight'
		      }
		   }		 
	      });
	      
	$('#getmiles-tip').qtip({
		 content: "Click this button to calculate mileage and update the map for the postcodes/addresses entered. ", 
		style: 'dark', 
		position: {
		      corner: {
			 target: 'bottomRight',
			 tooltip: 'topLeft'
		      }
		   }		 
	      });
	$('#gettotal-tip').qtip({
		 content: "Click this button to update total miles if you manually changed the miles above. ", 
		style: 'dark', 
		position: {
		      corner: {
			 target: 'bottomRight',
			 tooltip: 'topLeft'
		      }
		   }		 
	      });

	$('#tripForm input[name="input0"]').qtip({
		 content: "Enter Postcode or address. If precise address is not known, you can enter the town  name and later drag the pin on the map to the proper location.", 
		style: 'dark', 
		position: {
		      corner: {
			 target: 'bottomRight',
			 tooltip: 'topLeft'
		      }
		   }		 
	      });
	   

	$('#cleartrip-tip').qtip({
		 content: "Clears the details above so that you can create a new trip.", 
		style: 'dark', 
		position: {
		      corner: {
			 target: 'bottomRight',
			 tooltip: 'topLeft'
		      }
		   }		 
	      });


try{
/*app_notification */
    setAppNotification('');
}catch(err) {
}

});

function setAppNotification(note_json) {
	/* handles notifications set by app when page is first loaded */
	var note = '';
	var note_type='';
	
	if(note_json.length <1) {
		note_json = $('#app_notification').html();
		if(note_json.length <1) {
			return;
		}
	}
	
	var json_obj = $.parseJSON(note_json);
	
	if(json_obj.app_notification.length > 0) {
		note = json_obj.app_notification;
		note_type = json_obj.app_notification_type;
	}

	if (note.length > 0) { 
		$('#app_notification').removeClass('notification_type');
		$('#app_notification').removeClass('app_error');		
		$('#app_notification').addClass(note_type);
		$('#app_notification').html(note).show(); //.delay(3000).fadeOut(800);
		}
}




