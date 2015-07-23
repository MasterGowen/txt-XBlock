function TxtXBlockEdit(runtime, element) {

var question_editor = CodeMirror.fromTextArea(elementDOM.querySelector('#question-area'), {
		mode: "text/html",
		tabMode: "indent",
		lineNumbers: true
	});

var keywords_editor = CodeMirror.fromTextArea(elementDOM.querySelector('#question-area'), {
		mode: "text/html",
		tabMode: "indent",
		lineNumbers: true
	});

    $(element).find('.save-button').bind('click', function() {
		var handlerUrl = runtime.handlerUrl(element, 'studio_submit'),
			data = {
				display_name: $(element).find('input[name=display_name]').val(),
				question: question_editor.getValue(),
				weight: $(element).find('input[name=weight]').val(),
				correct_answer: $(element).find('input[id=correct_answer]').val(),
				max_attempts: $(element).find('input[name=max_attempts]').val(),
				keywords: keywords_editor.getValue(),
                grading_threshold: $(element).find('textarea[id=grading_threshold-area]').val(),
			};

		$.post(handlerUrl, JSON.stringify(data)).done(function(response) {
			window.location.reload(false);
		});
	});
	$(element).find('.cancel-button').bind('click', function() {
		runtime.notify('cancel', {});
	});
}