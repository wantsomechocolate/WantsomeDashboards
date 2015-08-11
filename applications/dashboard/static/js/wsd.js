

/* Formatting function for row details - modify as you need */
function format ( d, columns ) {

    // `d` is the original data object for the row
    // 'columns' is the column information including title, data (name of key in data dictionary), wether its a core value or not, etc.

    // Populate a list of all the fields that are considered core, remember this is being done on a single row!
    var core_fields=[]

    // Cycle through the columns list (exclude the first one because it is the column for the collapse expand controls)
    for (i=1;i<columns.length;i++) {

    	// if the column is labelled as a core column, that means it should already be in the main column tables
    	// This is excluding those columns and only showing additional information
    	if (columns[i]['core']===true){
    		core_fields.push(columns[i]['data'])
    	}
	    	// for (property in columns[i]){
	    	// 	alert(property+' '+columns[i][property]);
	    	// }
    }

    // Begin making the html to show the extra information
	child_rows='<table cellpadding="5" cellspacing="0" border="0" style="padding-left:50px;">'

	// for each property in the record being clicked
	for (property in d){
		// alert(property+' '+d[property]);

		// if the property is not a core field, aka if the property can not be found in the list of core fields
		// (indexOf returns -1 if not match is found)
		if (core_fields.indexOf(property)===-1){

			// Then add a row to the additional info table
			child_rows+='<tr>'+'<td>'+property+':</td>'+'<td>'+d[property]+'</td>'+'</tr>'

		}
	}

	if (d.serial_number!==null){
		child_rows
	}

	// complete the table for additional information
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
			        },

					selection: {
						draggable: true
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
			    },


			    zoom: {
			        enabled: true
			    },

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

	if (url_list[1]==='aws_table') {

		var table_name=url_list[2]

		// alert('made it');
		// alert(table_name);

		table_data=$.ajax({

		    url: '/ajax_aws_table/'+table_name,
		    dataType: "json",

		}) // end ajax call to set up table

			.done( function ( json ) {

				// alert(json['data']);

			    var table = $('#aws_table').DataTable( {
			        data: json['data'],
			        columns: json['columns'],
			        order: [[1, 'asc']]
			    } );

			    // Add event listener for opening and closing details
			    $('#aws_table tbody').on('click', 'td.details-control', function () {
			        var tr = $(this).closest('tr');
			        var row = table.row( tr );
			 
			        if ( row.child.isShown() ) {
			            // This row is already open - close it
			            row.child.hide();
			            tr.removeClass('shown');
			        }
			        else {
			            // Open this row
			            row.child( format( row.data(), json['columns'] ) ).show();
			            tr.addClass('shown');
			        }

			    } ); // end on event for collapse controls

			}); // end done section for ajax call to setup table




 
	}; // end if clause for checking if page name is aws_table






} ); // End document ready