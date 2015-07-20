$(document).ready(function() {
    // $('#aws-data-table').DataTable();
    // $('#example').DataTable();

    var url_list=window.location.pathname.split('/')
    var device_id=url_list[url_list.length-1]
    // alert(url_list[url_list.length-1]);

	$('#aws-data-table').DataTable( {
		processing: true,
	    serverSide: true,
	    ajax: {
	        url: '/ajax_view_aws_timeseries/'+device_id,
	        // type:'POST'
	    }
	} );


	// var chart = c3.generate({
	//     bindto: '#chart',
	//     data: {
	//       columns: [
	//         ['data1', 30, 200, 100, 400, 150, 250],
	//         ['data2', 50, 20, 10, 40, 15, 25]
	//       ]
	//     }
	// });

	// alert(device_id);
	graph_data = $.ajax({
		// method:'POST',
		url: '/ajax_graph_aws_timeseries/'+device_id,
	}).done(function(response){

		// alert(typeof(response));

		// alert(response.slice(1,response.length-1));

		// alert(JSON.parse(response));

		var chart = c3.generate({
			bindto:'#chart',
		    data: {
		        json: JSON.parse(response),
		        keys: {
		            x: '1',
		            value: ['2']
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


	// var chart = c3.generate({
	// 	bindto: '#chart',
	//     data: {
	//         x: 'x',
	// //        xFormat: '%Y%m%d', // 'xFormat' can be used as custom format of 'x'
	//         columns: [
	//             ['x', '2013-01-01', '2013-01-02', '2013-01-03', '2013-01-04', '2013-01-05', '2013-01-06'],
	// //            ['x', '20130101', '20130102', '20130103', '20130104', '20130105', '20130106'],
	//             ['data1', 30, 200, 100, 400, 150, 250],
	//             // ['data2', 130, 340, 200, 500, 250, 350]
	//         ]
	//     },
	//     axis: {
	//         x: {
	//             type: 'timeseries',
	//             tick: {
	//                 format: '%Y-%m-%d'
	//             }
	//         }
	//     }
	// });

	// setTimeout(function () {
	//     chart.load({
	//         columns: [
	//             ['data3', 400, 500, 450, 700, 600, 500]
	//         ]
	//     });
	// }, 1000);



} );