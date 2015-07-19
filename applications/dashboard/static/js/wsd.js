$(document).ready(function() {
    // $('#aws-data-table').DataTable();
    // $('#example').DataTable();

	$('#aws-data-table').DataTable( {
		processing: true,
	    serverSide: true,
	    ajax: {
	        url: '/ajax_view_aws_timeseries/001EC600229C_250',
	        type:'POST'
	    }
	} );

} );