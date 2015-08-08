

/* Formatting function for row details - modify as you need */
function format ( d ) {

    // `d` is the original data object for the row

	child_rows='<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'

	for (property in d){
		// alert(property+' '+d[property]);
		child_rows+='<tr>'+'<td>'+property+':</td>'+'<td>'+d[property]+'</td>'+'</tr>'
	}

	child_rows+='</table>';

    return child_rows
}


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





// There will be an ajax function that takes the table name and returns
// The core columns names for the table
// The data for the table
// table settings?

// The ajax function that will do this is called
// ajax_aws_table/tablename

// it takes an argument which is the tablename in aws

// The argument comes from the url, which will be called
// aws_table/tablename



	// ###############################################
	// General Code for Viewing AWS data in datatables
	// ###############################################

    var table = $('#example').DataTable( {
        ajax: "/ajax_das_list",
        columns: [
            {
                "className":      'details-control',
                "orderable":      false,
                "data":           null,
                "defaultContent": '',
            },
            { 
            	"data": "LOOPNAME",
            	"defaultContent": '',
            },
            { 
            	"data": "serial_number",
            },
            { 
            	"data": "UPTIME",
            	"defaultContent": '',
            },
            { 
            	"data": "ACQUISUITEVERSION",
            	"defaultContent": '',
            },
        ],
        order: [[1, 'asc']]
    } );
     
    // Add event listener for opening and closing details
    $('#example tbody').on('click', 'td.details-control', function () {
        var tr = $(this).closest('tr');
        var row = table.row( tr );
 
        if ( row.child.isShown() ) {
            // This row is already open - close it
            row.child.hide();
            tr.removeClass('shown');
        }
        else {
            // Open this row
            row.child( format(row.data()) ).show();
            tr.addClass('shown');
        }
    } );












} ); // End document ready