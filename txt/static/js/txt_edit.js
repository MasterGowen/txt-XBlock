function TxtXBlockEdit(runtime, element) {

var question_editor = CodeMirror.fromTextArea(element[0].querySelector('#question-area'), {
		mode: "text/html",
		tabMode: "indent",
		lineNumbers: true
	});

var correct_answer_editor = CodeMirror.fromTextArea(element[0].querySelector('#correct_answer'), {
		mode: "text/html",
		tabMode: "indent",
		lineNumbers: true
	});

var keywords_editor = CodeMirror.fromTextArea(element[0].querySelector('#keywords-area'), {
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
				correct_answer: correct_answer_editor.getValue(),
				max_attempts: $(element).find('input[name=max_attempts]').val(),
				keywords: keywords_editor.getValue(),
                grading_threshold: $(element).find('input[name=grading_threshold]').val(),
			};

		$.post(handlerUrl, JSON.stringify(data)).done(function(response) {
			window.location.reload(false);
		});
	});
	$(element).find('.cancel-button').bind('click', function() {
		runtime.notify('cancel', {});
	});
}