$(function() {
  $('.list-group-item').on('click', function() {
    $('.glyphicon', this)
      .toggleClass('glyphicon-chevron-right')
      .toggleClass('glyphicon-chevron-down');
  })
});

$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
});