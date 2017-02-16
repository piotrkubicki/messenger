$(document).ready(function() {
  var socket = io.connect('http://' + document.domain + ':' + location.port);
  
  socket.on('private message', function(response) {
    if ($('.sidebar-list > ul > li > a#' + response.sender_id).length) {
      if ($('#msg-box > div#' + response.sender_id).length) {
        $('#msg-box > div#' + response.sender_id).append(response.message);
        $('#msg-box > div#' + response.sender_id).scrollTop($('#msg-box > div#' + response.sender_id)[0].scrollHeight);
     
        if ($('#msg-box > div#' + response.sender_id).hasClass('active') == false) {
          $('.sidebar-list > ul > li > a#' + response.sender_id).closest('li').addClass('unseen-msg');
        } else {
          emit('message seen', response.sender_id);
        }
      } else {
        $('.sidebar-list > ul > li > a#' + response.sender_id).closest('li').addClass('unseen-msg');
      }
    }
    else {
      if ($('#msg-box > div#' + response.reciever_id).length) {
        $('#msg-box > div#' + response.reciever_id).append(response.message);
        $('#msg-box > div#' + response.reciever_id).scrollTop($('#msg-box > div#' + response.reciever_id)[0].scrollHeight);
     
        if ($('#msg-box > div#' + response.reciever_id).hasClass('active') == false) {
          $('.sidebar-list > ul > li > a#' + response.reciever_id).closest('li').addClass('unseen-msg');
        } else {
          emit('message seen', response.reciever_id);
        }
      } else {
        $('.sidebar-list > ul > li > a#' + response.reciever_id).closest('li').addClass('unseen-msg');
      }
    }
  });

  socket.on('friend request', function(response, data) {
    var friend_request = $('body').find('.friend-request-conf');
    
    if (!friend_request.length) {
      $('#msg-box').append(response);
      $('#friend-request-confirmation-' + data).modal({
        backdrop: 'static',
        keyboard: false
      });
    }
  });

  socket.on('friend request answer', function(response, friend_button, friend) {
    if (response.answer) {
      $('#friends-list').append(friend_button);
      $('#friends-list').find('#' + friend).closest('li').slideDown();
      socket.emit('join private room', (friend));
    }
  });

  socket.on('app error', function(response) { 
    $('body').append('<div class="alert alert-danger inf active">' + response.message + '</div>');
    
    setTimeout(function() {
      $('.inf').first().removeClass('active');
    }, 3000);
  });

  $(document).on('click', '#msg-send', function() {
   
    var message = {
      user_id : $('#msg-box-nav > .nav > li.active').attr('id'),
      msg : $('#msg-msg').val()
    }

    socket.emit('private message', message);
    $('#msg-msg').val('');
  });

  $(document).on('hide.bs.modal', '.friend-request-conf', function(e) {
    setTimeout(function() {
      $(e.target).remove();
    }, 1000);
  });

  $(document).on('click', '#msg-box-nav > .nav > li', function(e) {
    e.preventDefault();
    var friend_id = $(this).attr('id');

    $('.sidebar-list > ul > li > a#' + friend_id).closest('li').removeClass('unseen-msg');
    
    $('#msg-box-nav > .nav').find('li').removeClass('active');
    $('#msg-box').children('div').removeClass('active');

    $(this).addClass('active');
    $('#msg-box').children('div#' + friend_id).addClass('active');
  });

  $(document).on('click', '#msg-box-nav > .nav > li > a > i', function(e) {
    e.stopPropagation();
    var friend_id = $(this).closest('li').attr('id');
    
    $('#msg-box > div#' + friend_id).remove();
    $(this).closest('li').remove();

    $('#msg-box-nav > .nav > li').first().trigger('click');
  });

  $('#msg-msg').keyup(function(e) {
    if (e.which == 13) {
      $('#msg-send').trigger('click');
    }
  });
});
