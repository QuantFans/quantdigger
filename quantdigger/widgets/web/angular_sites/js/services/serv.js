// 确保ajax提交能通过安全验证。
function getCookie(name) {
	var cookieValue = null;
	if (document.cookie && document.cookie != '') {
		var cookies = document.cookie.split(';');
		for (var i = 0; i < cookies.length; i++) {
			var cookie = jQuery.trim(cookies[i]);
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) == (name + '=')) {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
};
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
// 登录后刷新，这个设置发挥作用。
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});
//
app.factory('UserService', ['Restangular', function(Restangular) {
}]);

app.constant('AUTH_EVENTS', {
	loginSuccess: 'auth-login-success',
	loginFailed: 'auth-login-failed',
	logoutSuccess: 'auth-logout-success',
	sessionTimeout: 'auth-session-timeout',
	notAuthenticated: 'auth-not-authenticated',
	notAuthorized: 'auth-not-authorized'
});

/** 角色控制，与服务器对应。 */
app.constant('USER_ROLES', {
	all: '*',
	admin: 'admin',
	editor: 'editor',
    user: 'user',
	guest: 'guest'
});

/** 会话服务, 用于保持会话ID。 */
app.service('Session', function() {
	this.create = function(sessionId, userId, userRole) {
		this.id = sessionId;    // int
		this.userId = userId;       // int
		this.userRole = userRole;     // str
	};
	this.destroy = function() {
		this.id = null;
		this.userId = null;
		this.userRole = null;
	};
	return this;
});


/** 验证服务。 */
app.factory('AuthService', function($http, Session) {
	var authService = {};
	/** 登录验证 */
	authService.login = function(credentials) {
		$http.defaults.headers.post['X-CSRFToken'] = getCookie("csrftoken");
        // 设置ajax 的安全标志, 登录后csrf标志会改变.
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                    xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
                }
            }
        });
		return $http
			.post('/accounts/api/login/', $.param(credentials))
			.then(function(res) {
				Session.create(res.data.id, res.data.user.id,
					res.data.user.role);
				return res.data.user;
			});
	};

	authService.logout = function() {
        $http.defaults.headers.post['X-CSRFToken'] = getCookie("csrftoken");
		return $http
			.post('/accounts/api/logout/')
			.then(function(res) {
				return true;
			});
	};

	authService.isAuthenticated = function() {
		return !!Session.userId;
	};
	/** 授权验证 */
	authService.isAuthorized = function(authorizedRoles) {
		if (!angular.isArray(authorizedRoles)) {
			authorizedRoles = [authorizedRoles];
		}
		return (authService.isAuthenticated() &&
			authorizedRoles.indexOf(Session.userRole) !== -1);
	};
	return authService;
});
