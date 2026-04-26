$(document).ready(function() {
    $('#search-form').on('submit', function(e) {
        e.preventDefault();

        var $form = $(this);
        var $btn = $('#search-btn');
        var $resultsContainer = $('#results-container');
        var $resultsContent = $('#results-content');

        // индикатор загрузки
        var originalText = $btn.data('original-text') || 'Искать';
        $btn.prop('disabled', true).html('<span class="loading-spinner"></span> ' + ($btn.data('searching-text') || 'Поиск...'));

        $.ajax({
            url: $form.data('url'),
            type: 'POST',
            data: $form.serialize(),
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            success: function(response) {
                if (response.html) {
                    $resultsContent.html(response.html);
                    $resultsContainer.fadeIn(300);

                    // Скролл к результатам
                    $('html, body').animate({
                        scrollTop: $resultsContainer.offset().top - 80
                    }, 500);
                }
            },
            error: function(xhr) {
                var errorMsg = $btn.data('error-text') || 'Ошибка при выполнении поиска';
                $resultsContent.html('<div class="alert alert-danger">' + errorMsg + '</div>');
                $resultsContainer.fadeIn(300);
            },
            complete: function() {
                $btn.prop('disabled', false).html(originalText);
            }
        });
    });
});