$(function() {
  $('.list-group-item').on('click', function() {
    $('.glyphicon', this)
      .toggleClass('glyphicon-chevron-right')
      .toggleClass('glyphicon-chevron-down');
  }),
  $('button').on('click', function(event) {
    event.stopPropagation(); // stop bubble-up into anchor tag
    var controls = $(event.target).closest('a').attr('href'); // "#ctrl-2-1-43" --> args['ctrl', 2, 1, 43]
    $.ajax({
        type: "POST",
        data: {
            csrfmiddlewaretoken: $('input:hidden#csrftoken').val(),
            controls: controls,
            response: $(event.target).text(),
        },
        dataType: "json",
        success: function(data) { alert(data); },
        failure: function(msg) { alert(msg); }
    });
    console.log(args.length);
  });
});
