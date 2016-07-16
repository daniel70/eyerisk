$(function() {
  $('.list-group-item').on('click', function() {
    $('.glyphicon', this)
      .toggleClass('glyphicon-chevron-right')
      .toggleClass('glyphicon-chevron-down');
  }),
  $('snutton').on('click', function(event) { // don't use the general button for this
    event.stopPropagation(); // stop bubble-up into anchor tag
    event.preventDefault();
//    var controls = $(event.target).closest('a').attr('href'); // e.g. "#ctrl-2-1-43"
    var controls = $(event.target).parent().data('id'); // e.g. "#2-1-43"
    var response = $(event.target).text();
    console.log(controls);
    $.ajax({
        type: "POST",
        data: {
            csrfmiddlewaretoken: $('input:hidden#csrftoken').val(),
            controls: controls,
            response: response,
        },
        dataType: "json",
        success: function(data) {
            console.log(data);
            var this_li = $(event.target).closest('.list-group-item');
            var items = this_li.add(this_li.next().find('.list-group-item'));

            items.removeClass('list-group-item-success list-group-item-info list-group-item-warning');
            var newClass = '';
            switch(response) {
                case 'A':
                    newClass = 'list-group-item-success';
                    break;
                case 'M':
                    newClass = 'list-group-item-info';
                    break;
                case 'T':
                    newClass = 'list-group-item-warning';
            }
            items.addClass(newClass);

            // now we need to check if ALL parents of this_li have the same class and, if so, change him as well
            console.log(this_li.closest('.list-group').children('.list-group-item').not());
        },
        failure: function(msg) { console.log(msg); }
    });
  });
});
