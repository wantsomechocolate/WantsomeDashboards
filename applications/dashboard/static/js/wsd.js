$(document).ready(function() {

    var url_list=window.location.pathname.split('/')
    var device_id=url_list[url_list.length-1]
    // alert(url_list[url_list.length-1]);

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
	    	{
	    		"data":"cumulative_electric_usage_kwh",
	    		"defaultContent": "",
	    	},
	    	{
	    		"data":"001EC600229C_1__4",
	    		"defaultContent": "",
	    	},
	    ]
	} );



	// alert(device_id);
	graph_data = $.ajax({
		// method:'POST',
		url: '/ajax_graph_aws_timeseries/'+device_id,
	}).done(function(response){

		var chart = c3.generate({
			bindto:'#chart',
		    data: {
		        json: JSON.parse(response),
		        keys: {
		            x: 'timestamp',
		            value: ['cumulative_electric_usage_kwh','001EC600229C_1__4','001EC600229C_1__113']
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