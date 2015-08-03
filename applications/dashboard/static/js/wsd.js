$(document).ready(function() {

    var url_list=window.location.pathname.split('/')
    var device_id=url_list[url_list.length-1]
    // alert(url_list[url_list.length-1]);


    table_data = $.ajax({
    	url:'ajax_get_device_field_names/'+device_id,
    }).done(function(field_names_list){
    	alert(JSON.parse(field_names_list));
    })


	$('#aws-data-table').DataTable( {
		processing: true,
	    serverSide: true,
	    ajax: {
	        url: '/ajax_view_aws_timeseries/'+device_id,
	        // type:'POST'
	    },
	    "columns":[
	    	{"data":"timeseriesname"},
	    	{"data":"timestamp"},
	    	// {
	    	// 	"data":"cumulative_electric_usage_kwh",
	    	// 	"defaultContent": "",
	    	// },
	    	{
	    		"data":"001EC600229C_1__4",
	    		"defaultContent": "",
	    	},
	    ]
	} );



	// aasdf
	var table = $('#aws-data-table').DataTable( {
		processing: true,
	    serverSide: true,
	    ajax: {
	        url: '/ajax_view_aws_timeseries/'+device_id,
	    },
	} );

	table.columns=table.ajax.json()['fieldnames']
	// asdf




	// alert(device_id);
	graph_data = $.ajax({
		// method:'POST',
		url: '/ajax_graph_aws_timeseries/'+device_id,
	}).done(function(response){

		// json_response=JSON.parse(response)
		// alert(json_response['column_names'])

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

	});



	// var chart = c3.generate({
	//     data: {
	//         json: [[
	//             '2014-01-01',
	//             200,
	//             200,
	//             400
	//         ], [
	//             '2014-01-02',
	//             100,
	//             300,
	//             400
	//         ], [
	//             '2014-01-03',
	//             300,
	//             200,
	//             500
	//         ], [
	//             '2014-01-04',
	//             400,
	//             100,
	//             500
	//         ]],
	//         keys: {
	//             x: '1',
	//             value: ['2']
	//         }
	//     },
	//     axis: {
	//         x: {
	//             type: 'timeseries',
	//             tick: {
	//                 format: function (x) {
	//                     return x.getFullYear();
	//                 }
	//             }
	//         }
	//     }
	// });


} );