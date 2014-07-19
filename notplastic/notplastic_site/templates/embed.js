(function () {

  var EMBED_CONTENT = {{embed_content|tojson|safe}};

  var scriptName = "embed"; //name of this script, used to get reference to own tag
  var jQuery; //noconflict reference to jquery
  var jqueryPath = "http://ajax.googleapis.com/ajax/libs/jquery/1.11.1/jquery.min.js";
  var jqueryVersion = "1.11.1";
  var scriptTag; //reference to the html script tag
  var embedGUID = (function() {
                     function s4() {
                       return Math.floor((1 + Math.random()) * 0x10000)
                                  .toString(16)
                                  .substring(1);
                     }
                     return function() {
                       return s4() + s4() + s4() + s4() +
                         s4() + s4() + s4() + s4();
                     };
                   })()();

  /******** Get reference to self (scriptTag) *********/
  var allScripts = document.getElementsByTagName('script');
  var targetScripts = [];
  for (var i in allScripts) {
    var name = allScripts[i].src;
    if(name && name.indexOf(scriptName) > 0)
      targetScripts.push(allScripts[i]);
  }

  scriptTag = targetScripts[targetScripts.length - 1];

  /******** helper function to load external scripts *********/
  function loadScript(src, onLoad) {
    var script_tag = document.createElement('script');
    script_tag.setAttribute("type", "text/javascript");
    script_tag.setAttribute("src", src);

    if (script_tag.readyState) {
      script_tag.onreadystatechange = function () {
        if (this.readyState == 'complete' || this.readyState == 'loaded') {
          onLoad();
        }
      };
    } else {
      script_tag.onload = onLoad;
    }
    (document.getElementsByTagName("head")[0] || document.documentElement).appendChild(script_tag);
  }

  /******** helper function to load external css *********/
  function loadCss(href) {
    var link_tag = document.createElement('link');
    link_tag.setAttribute("type", "text/css");
    link_tag.setAttribute("rel", "stylesheet");
    link_tag.setAttribute("href", href);
    (document.getElementsByTagName("head")[0] || document.documentElement).appendChild(link_tag);
  }

  /******** load jquery into 'jQuery' variable then call main ********/
  if (window.jQuery === undefined || window.jQuery.fn.jquery !== jqueryVersion) {
    loadScript(jqueryPath, initjQuery);
  } else {
    initjQuery();
  }

  function initjQuery() {
    jQuery = window.jQuery.noConflict(true);
    main();
  }

  /******** starting point for your widget ********/
  function main() {
    //your widget code goes here
    jQuery(document).ready(function ($) {
      //loadCss("{{url_for('notplastic_site.static', filename='css/embed.css', _external=True)}}");
      loadScript("{{url_for('notplastic_site.session_init', _external=True)}}" + "?_ref=" + encodeURIComponent(window.location.origin) + "&_embedGUID=" + encodeURIComponent(embedGUID),
        function() {
        jQuery(scriptTag).after(EMBED_CONTENT);
        jQuery('#notplastic-embed-container form input[name=download_code]')
          .on('input',
            function() {
              jQuery(this)
                .siblings('input[type=submit]')
                .prop('disabled',
                  jQuery(this).val().length < 6);
            });

        jQuery('#notplastic-embed-container form').submit(function(event) {
          event.preventDefault();

          if (jQuery('input[type=submit]', this).prop('disabled')) return false;

          jQuery
            .ajax({
              url: jQuery(this).attr('action'),
              data: jQuery(this).serialize(),
              xhrFields: {
                withCredentials: true
              },
              crossDomain: true,
              type: 'post',
              statusCode: {
                404: function(jqXHR) {
                  // no existe el codigo
                  console.log(404);
                },
                400: function(jqXHR) {
                  // bad request
                  console.log(400);
                },
                410: function(jqXHR) {
                  // no hay mas downloads disponibles
                },
                429: function(jqXHR) {
                  // too many requests
                }
              }
            })
            .always(function(data) {
            console.log(data);
          });
        });
      });
      //example script load
      //loadScript("http://example.com/anotherscript.js", function() { /* loaded */ });
    });
  }
})();
