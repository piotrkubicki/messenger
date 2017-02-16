$(document).ready(function() {
  var profile = {};

  $(document).on('click', '#invite-friend-btn', function(e) {
    e.preventDefault(); 
    var username = $('#invite-friend-username').val();
    self = $(this);
    
    $('body').append('<div class="spinner-overlay"><div class="spinner"></div>');

    if (username != '') { 
      var request = {
        username : username
      }

      $.ajax({
        type: 'POST',
        url: '/users/' + $('#user-id').val() + '/friends/add/',
        data: JSON.stringify(request),
        contentType: 'application/json;charset=UTF-8',
        success: function(result) {
          $('#invite-friend-username').val('');
          $('body').append('<div class="alert alert-success inf active">' + result.message + '</div>');
          
          setTimeout(function() {
            $('.inf').first().removeClass('active');
          }, 3000);
        },
        error: function() {
          $('body').append('<div class="alert alert-danger inf active">Something goes wrong. Try again later.</div>');
        
          setTimeout(function() {
            $('.inf').first().removeClass('active');
          }, 3000);
        }
      })
      .always(function() {
        $('.spinner-overlay').remove();
      });
    }
  });

  $(document).on('click', '#confirm-friend-request, #reject-friend-request, #block-user', function(e) {
    e.preventDefault();
    self = $(this);
    modal = self.parent('.modal');

    $('body').append('<div class="spinner-overlay"><div class="spinner"></div></div>');

    var response = {
      request_id : $('#friend-request-id').data('request'),
      user_id : $('#request-user-id').data('user-id'),
      answer : self.data('answer')
    }
    
    $(this).closest('.modal').modal('toggle');
    
    $.ajax({
      type: 'POST',
      url: '/users/' + $('#user-id').val() + '/friends/add/response/',
      data: JSON.stringify(response),
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        $('body').append('<div class="alert alert-success inf active">' + result.message + '</div>');
        
        setTimeout(function() {
          $('.inf').first().removeClass('active');
        }, 3000);
      },
      error: function() {
        $('body').append('<div class="alert alert-danger inf active">Something goes wrong. Try again later.</div>');
        
        setTimeout(function() {
          $('.inf').first().removeClass('active');
        }, 3000);
      }
    })
    .always(function() {
      $('.spinner-overlay').remove();
    });
  });
  
  $(document).on('click', '.friend-entry > button', function(e) {
    e.preventDefault();
    var username = $(this).data('username'); 
    $('#invite-friend-username').val(username);
    $('#invite-friend-btn').trigger('click');
  });

  $(document).on('click', '#profile-update-btn', function(e) {
    e.preventDefault();
    $('body').append('<div class="spinner-overlay"><div class="spinner"></div</div>');

    profile.first_name = $('#first-name').val();
    profile.last_name = $('#last-name').val();
    profile.day = $('#day').val();
    profile.month = $('#month').val();
    profile.year = $('#year').val();

    $('#profile').modal('toggle');
    console.log(profile);
    if (profile.avatar != undefined) {
      var a = profile.avatar.split(',', 2);
      profile.avatar = a[1];
    } else {
      profile.avatar = '';
    }
    
    $.ajax({
      type: 'POST',
      url: '/users/' + $('#user-id').val() + '/profile/update',
      data: JSON.stringify(profile),
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        $('body').append('<div class="alert alert-success inf active">Profile updated successfuly</div>');
        
        setTimeout(function() {
          $('.inf').first().removeClass('active');
        }, 3000);
      },
      error: function() {
        $('body').append('<div class="alert alert-danger inf active">Something goes wrong. Try again later.</div>');
        
        setTimeout(function() {
          $('.inf').first().removeClass('active');
        }, 3000);
      }
    })
    .always(function() {
      $('.spinner-overlay').remove();
      profile = {}
    });
  });

  $(document).on('click', '#friend-search-btn', function(e) {
    e.preventDefault();
    $('body').append('<div class="spinner-overlay"><div class="spinner"></div></div>');
 
    $('#friends-box').html('');

    var friend = {
      first_name : $('#friend-first-name').val(),
      last_name : $('#friend-last-name').val(),
      username : $('#friend-username').val(),
      day : $('#friend-day').val(),
      month : $('#friend-month').val(),
      year : $('#friend-year').val()
    }

    $.ajax({
      type: 'POST',
      url: '/users/' + $('#user-id').val() + '/friends/search/', 
      data: JSON.stringify(friend),
      contentType: 'application/json;charset=UTF-8',
      success: function(result) {
        $('#friends-box').append(result.friends); 
      }
    })
    .always(function() {
      $('.spinner-overlay').remove();
    });

  });

  $(document).on('animationend', '.inf', function(e) {
    if (e.originalEvent.animationName == 'slideUpInf') {
      $(this).remove();
    }
  });

  $(document).on('click', 'button#load-file', function(e) {
    e.preventDefault();
    self = $(this);

    var input = document.getElementById('user-photo');
    file = input.files[0];

    fr = new FileReader();
    fr.onload = function() {
      profile.avatar = fr.result
      input.value = '';
    }

    fr.readAsDataURL(file);
  });
});
