function start_long_task() {
	// add task status elements
	div = $('<div class="progress"><div></div><div>...</div><div>&nbsp;</div></div><hr>');
	$('#progress').append(div);

	// send ajax POST request to start background job

	$.ajax({
		type: 'POST',
		url: '/longtask',
		data: $("#input-form").serialize(),
		success: function(data, status, request) {
			status_url = request.getResponseHeader('Location');
			update_progress(status_url, div[0]);
		},
		error: function() {
			alert('Unexpected error');
		}
	});
}

function update_progress(status_url, status_div) {
	// send GET request to status URL
	$.getJSON(status_url, function(data) {
		// update UI
		$(status_div.childNodes[1]).text(data['status']);
		if (data['state'] != 2) {
			// rerun in 2 seconds
			setTimeout(function() {
				update_progress(status_url, status_div);
			}, 2000);
		}
	});
}
$(function() {
	$('#start-bg-job').click(start_long_task);
});