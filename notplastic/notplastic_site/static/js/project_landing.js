/* jshint undef: true, unused: true */
/* global $, _, console, window */

window.mercadopago_callback = function(transaction_result) {
  alert("TODO");
};

$(function() {

  $('#notplastic-download-form input[name=download_code]')
    .on('input',
      function() {
        $(this)
          .siblings('input[type=submit]')
          .prop('disabled',
            $(this).val().length < 6);
      });

  var sliderInputHandler = function() {
      $(this)
        .siblings('output')
        .val($(this).val());
  };

  $('#notplastic-payment-form input[name=amount]').on('input',
    sliderInputHandler);

  $.proxy(sliderInputHandler, $('#notplastic-payment-form input[name=amount]').get(0))();





});