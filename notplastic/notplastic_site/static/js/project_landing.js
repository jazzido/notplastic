/* jshint undef: true, unused: true */
/* global $, _, console, window, Spinner */

$(function() {

  var spinner = new Spinner({
    lines: 9, // The number of lines to draw
    length: 9, // The length of each line
    width: 4, // The line thickness
    radius: 9, // The radius of the inner circle
    corners: 1, // Corner roundness (0..1)
    rotate: 0, // The rotation offset
    direction: 1, // 1: clockwise, -1: counterclockwise
    color: '#000', // #rgb or #rrggbb or array of colors
    speed: 1, // Rounds per second
    trail: 60, // Afterglow percentage
    shadow: false, // Whether to render a shadow
    hwaccel: false, // Whether to use hardware acceleration
    className: 'spinner', // The CSS class to assign to the spinner
    zIndex: 2e9, // The z-index (defaults to 2000000000)
    top: '50%', // Top position relative to parent
    left: '50%' // Left position relative to parent
  }).spin();

  var downloadCodeInputHandler = function() {
    $(this)
      .siblings('button[type=submit], input[type=submit]')
      .prop('disabled',
        $(this).val().length < 6);
  };

  var sliderInputHandler = function() {
      $(this)
        .siblings('output')
        .val($(this).val());
  };

  $('#notplastic-download-form input[name=download_code]')
    .on('input', downloadCodeInputHandler);

  $('#notplastic-payment-form input[name=amount]').on('input',
    sliderInputHandler);

  $.proxy(sliderInputHandler, $('#notplastic-payment-form input[name=amount]').get(0))();
  $.proxy(downloadCodeInputHandler, $('#notplastic-download-form input[name=download_code]').get(0))();

  $('form#notplastic-download-form input[name=download_code]').on('focus', function(event) {
    $('form#notplastic-download-form output').html('');
  });

  $('form#notplastic-download-form').on('submit', function(event) {
    event.preventDefault();
    var msg = '', self = this;
    $.ajax({
      type: 'POST',
      url: $(this).attr('action'),
      data: $(this).serialize(),
      error: function(xhr, status, error) {
        switch(xhr.status) {
          case 404:
          msg = 'El código ingresado es incorrecto';
          break;
          case 400:
          msg = 'Hubo un error. Por favor intentá nuevamente';
          break;
          case 410:
          msg = 'Se superaron la cantidad de descargas permitidas para el código ingresado';
          break;
          case 429:
          msg = 'Demasiados intentos en muy poco tiempo. Volvé a intentar en un rato.';
          break;
        }
        $('output', self).addClass('hilite').html(msg).delay(1500).queue(function(next) { $(this).removeClass('hilite'); next(); });
        $('#notplastic-download-form input[name=download_code]').val('');
        $.proxy(downloadCodeInputHandler, $('#notplastic-download-form input[name=download_code]').get(0))();

      },
      success: function(data, status, xhr) {
        msg = 'Gracias! Está comenzando tu descarga';
        var remainingDls = parseInt(xhr.getResponseHeader('X-Remaining-Downloads'));
        if (remainingDls > 1) {
          msg += '. Este código te permitirá bajar el material hasta ' + (remainingDls-1) + ' ' + (remainingDls == 2 ? 'vez' : 'veces') + ' más';
        }
        $('output', self).addClass('hilite').html(msg).delay(1500).queue(function(next) { $(this).removeClass('hilite'); next(); });
        $('#notplastic-download-form input[name=download_code]').val('');
        $.proxy(downloadCodeInputHandler, $('#notplastic-download-form input[name=download_code]').get(0))();
        window.location.replace(xhr.getResponseHeader('X-Download-URI'));
      }
    });
    return false;
  });

});