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

  $('#notplastic-payment-form input[name=amount]').on('input',
    function() {
      console.log(      $(this)
        .siblings('output'));
      $(this)
        .siblings('output')
        .val($(this).val());

    });


});