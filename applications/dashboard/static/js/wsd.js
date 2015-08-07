$(document).ready(function() {


	// in order to check if we are on the correct page!
    var url_list=window.location.pathname.split('/')
	    // var device_id=url_list[url_list.length-1]
	    // alert(url_list[url_list.length-1]);



    if (url_list[1]==='device') {

    	// Get the device ID from the url
		var device_id=url_list[2]


		// ###################################
		// For viewing the data with datatables
		// ###################################

		$.ajax({
		    url: '/ajax_get_device_field_names/'+device_id,
		    dataType: "json",
		})
			.done( function ( json ) {

		        var table = $('#aws-data-table').dataTable( {
					processing: true,
				    serverSide: true,
				    scrollY: 300,
	                stateSave:true,
	                // order:[[1,'desc']],
	                scrollCollapse:false,
				 	ajax:'/ajax_view_aws_timeseries/'+device_id,
					columns:json
				});

		    }); // end datatables for device page



		// ###################################
		// For graphing the data with C3.js
		// ###################################

		graph_data = $.ajax({
			// method:'POST',
			url: '/ajax_graph_aws_timeseries/'+device_id,
		}).done(function(response){

			var chart = c3.generate({
				bindto:'#chart',
			    data: {
			        json: JSON.parse(response)['data'],
			        keys: {
			            x: 'timestamp',
			            value: JSON.parse(response)['column_names'],
			        }
			    },

			    axis: {
			        x: {
			            type: 'category',
						tick: {
							count:10,
						    rotate: 75,
						    multiline: false
						},
						height: 130
			        }
			    }
			});

			return response;

		}); // end graphing for device page

	} // End if for device page

} );