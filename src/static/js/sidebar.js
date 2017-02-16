$(document).ready(function() {
  var socket = io.connect('http://' + document.domain + ':' + location.port);
  
  socket.on('friend connect', function(response) {
    $('#friends-list').find('#' + response.user_id).find('i').addClass('fa fa-fire');
    
    if (response.emit) {
      socket.emit('connected friend response', response.user_id);
    }
  });

  socket.on('relog', function(response) {
    $('body').append(response.response);
    $('#relog-form').modal({
      backdrop: 'static',
      keyboard: false
    });
  });

  socket.on('friend disconnect', function(response) {
    $('#friends-list').find('#' + response.user_id).find('i').removeClass('fa fa-fire');
  });

  $(document).on('click', '#friends-list > li > a', function(e) {
    e.preventDefault();
    var friend_id = $(this).attr('id');
    var msg_nav = $('#msg-box-nav > .nav').find('#' + friend_id);

    $(this).closest('li').removeClass('unseen-msg');

    if (msg_nav.length) {
      msg_nav.trigger('click');
    } else {
      $('#msg-box-nav > .nav').append('<li id="' + friend_id + '" class=""><a href="#">' + this.text + ' <i class="fa fa-times-circle"></i></a></li>');
      $('#msg-box').append('<div id="' + friend_id +  '" class=""></div>');
      $('#msg-box-nav > .nav > li#' + friend_id).trigger('click');
      $('#msg-box').children('div#' + friend_id).append('<div class="spinner"></div>');
      $('#msg-msg').prop('disabled', true);
      
      $.ajax({
        type: 'POST',
        url: '/users/' + $('#user-id').val() + '/friends/' + friend_id + '/messages/',
        contentType: 'application/json;charset=UTF-8',
        success: function(result) {
          $('#msg-box > div#' + friend_id).append(result.messages);
          $('#msg-box > div#' + friend_id).scrollTop($('#msg-box > div#' + friend_id)[0].scrollHeight);
          $('#msg-box > div#' + friend_id + ' > .spinner').remove();
          socket.emit('message seen', friend_id);
          $('#msg-msg').prop('disabled', false);
        }
      });
    }
  });

});
