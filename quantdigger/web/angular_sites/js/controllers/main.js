/** 定义全局变量的区域，通常与Body挂钩。 */
app.controller('ApplicationController',
               ['$scope','$rootScope', '$http', 'USER_ROLES','AUTH_EVENTS', 'AuthService', 'Session',
               function ($rootScope, $scope,$http,USER_ROLES,AuthService, AUTH_EVENTS, Session) {
    // 由服务器控制的变量值，当网站由传统方式切换到angular框架的时候用来设置用户是否已经登录。
  	$scope.urlApi="";
  	$scope.imgUrl="";
	$scope.currentUser = null;
	$scope.userRoles = USER_ROLES;
	$scope.isAuthorized = AuthService.isAuthorized;
	$scope.setCurrentUser = function(user) {
		$scope.currentUser = user;
	};
    // 用来控制传统页面的用户验证。
    if (global_user) {
        $scope.currentUser=global_user
        Session.create(0, global_user.id, global_user.role);
        $rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
    };
}]);

/**  登录，注销，注册 */
app.controller('authController',['$scope','$location','$rootScope','$http','AUTH_EVENTS','AuthService',
	function ($scope, $location, $rootScope, $http, AUTH_EVENTS, AuthService) {
	$scope.credentials = {
		username: 'admin',
		password: 'wdj123'
	};
	$scope.user = {
		username: 'wwwwww',
		email: '33830957@qq.com',
		password1: 'wwwwww',
		password2: 'wwwwww',
	};
	$scope.login = function(credentials) {
		console.log(credentials);
		AuthService.login(credentials)
			.then(function(user) {
				$("#login").modal("toggle");
				$scope.setCurrentUser(user);
				$rootScope.$broadcast(AUTH_EVENTS.loginSuccess);
                global_user = user; // mark传统方式的登录。
                /*window.location.href = "/#/index";*/

			}, function() {
				$rootScope.$broadcast(AUTH_EVENTS.loginFailed);
				alert("错误的用户名或密码");
			});
	};

	$scope.logout = function() {
		/// @todo remove Session
		AuthService.logout().then(function(user) {
			$scope.setCurrentUser(null);
			$rootScope.$broadcast(AUTH_EVENTS.logoutSuccess);
            /*$location.path('/');*/
            window.location.href = "/#/index";
		});
	};
	/**
	 * 注册用户
	 * @param {对象} user 用户信息，包括：用户名，邮箱，密码。
	 */
	$scope.register = function(user) {
		if (!user.agree) {
			alert("请同意服务协议");
		}
		else {
			console.log(user);
			$http.defaults.headers.post['X-CSRFToken'] = getCookie("csrftoken");
			return $http
				.post($scope.urlApi + '/accounts/api/register/', $.param(user))
				.then(function() {
					$("#register").modal("toggle");
					$("#activate").modal();
					var emailSplit = user.email.split("@");
					emailSplit[0] = "mail";
					user.activate = emailSplit[0] + "." + emailSplit[1];
				}, function() {
					alert("注册失败");
				});
		};
	};
	// 用户建议
	$scope.suggest = function(userSuggest){
		$http.defaults.headers.post['X-CSRFToken'] = getCookie("csrftoken");
		console.log(userSuggest);
		return $http
			.post($scope.urlApi + '/accounts/api/userSuggest/', $.param(userSuggest))
			.then(function() {
				$("#suggest").modal("toggle");
			}, function() {
				alert("提交失败");
			});
	};
	//连接服务器验证用户名唯一性
	$scope.onlyUserName = function(userName) {
		$http.defaults.headers.post['X-CSRFToken'] = getCookie("csrftoken");
		var user={
			name: userName
		};
		console.log(user);
		return $http
			.post($scope.urlApi + '/accounts/api/unique_user/', $.param(user))
			.then(function() {
				$scope.isUserName=true;
			}, function() {
				$scope.isUserName=false;
			});
	};

	//连接服务器验证邮箱唯一性
	$scope.onlyEmail = function(userEmail) {
		$http.defaults.headers.post['X-CSRFToken'] = getCookie("csrftoken");
		var user={
			email: userEmail
		};
		console.log(user);
		return $http
			.post($scope.urlApi + '/accounts/api/unique_email/', $.param(user))
			.then(function() {
				$scope.isEmail=true;
			}, function() {
				$scope.isEmail=false;
			});
	};

}]);

app.controller('personalController', ['$scope', '$http', 'Session', function($scope, $http, Session) {
	/** 修改账户信息 */
	$scope.modifyAuth = function(user) {
		console.log("修改帐号信息,参数：");
		console.log(user);
		$http.defaults.headers.put['X-CSRFToken'] = getCookie("csrftoken");
		return $http
			.put($scope.urlApi + '/accounts/api/user/' + Session.userId + '/', $.param(user))
			.then(function(res) {
				/// @todo 验证邮箱的唯一性。
				console.log("修改成功！");
			}, function(res) {
				console.log("修改失败");
			});
	};
	/**  获取账户信息 */
	$scope.getAuth = function() {
		console.log("获取帐号信息。。");
		return $http
			.get($scope.urlApi + '/accounts/api/user/' + Session.userId + '/')
			.then(function(res) {
				$scope.user=res.data;
				console.log(res.data);
			}, function(res) {
				console.log("个人帐号获取失败!");
			});
	};
	// 获取用户资料
	$scope.getUserInfo = function() {
		console.log("获取用户资料中...");
		return $http
			.get($scope.urlApi + '/accounts/api/profile/' + Session.userId + '/')
			.then(function(res) {
				$scope.user=res.data;
				console.log($scope.userInfo);
			}, function(res) {
				console.log("个人资料获取失败!");
			});
	};
	// 提交用户资料
	$scope.putUserInfo = function(user){
		$http.defaults.headers.post['X-CSRFToken'] = getCookie("csrftoken");
		console.log(user);
		return $http
			.post($scope.urlApi + '/accounts/api/profile/' + Session.userId + '/', $.param(user))
			.then(function() {
				console.log("保存成功");
			}, function() {
				console.log("提交失败");
			});
	};
	//连接服务器验证邮箱唯一性
	$scope.onlyEmail = function(userEmail) {
		$http.defaults.headers.post['X-CSRFToken'] = getCookie("csrftoken");
		var user={
			email: userEmail
		};
		console.log(user);
		return $http
			.post($scope.urlApi + '/accounts/api/unique_email/', $.param(user))
			.then(function() {
				$scope.isEmail=true;
			}, function() {
				$scope.isEmail=false;
			});
	};
}]);

var shop = angular.module("shop", []);
shop.controller("shopController", ["$scope", "$http", function($scope, $http) {
	//获取商店首页商品
	$scope.getShop = function() {
		console.log("获取商店首页商品...");
		$http.get($scope.urlApi + "/shop/")
			.then(function(res) {
				$scope.latests = res.data.latest;
				$scope.hots = res.data.hot;
				console.log($scope.latests);
				console.log($scope.hots);
			}, function(res) {
				console.log("Failed!");
			});
	};
	$scope.getShop();
	//获取最新商品
	$scope.getShopLatest = function() {
		console.log("获取最新商品...");
		return $http
			.get($scope.urlApi + "/shop/latest/")
			.then(function(res) {
				$scope.latests = res.data;
				console.log($scope.latests);
			}, function() {
				console.log("获取失败");
			});
	};
	//获取最热商品
	$scope.getShopHot = function() {
		console.log("获取最热商品...");
		return $http
			.get($scope.urlApi + "/shop/hot/")
			.then(function(res) {
				$scope.hots = res.data;
				console.log($scope.hots);
			}, function() {
				console.log("获取失败");
			});
	};
	//获取分类商品
	$scope.getShopType = function(id) {
		console.log("获取分类商品...");
		return $http
			.get($scope.urlApi + "/shop/" + id + "/")
			.then(function(res) {
				$scope.types = res.data;
			}, function() {
				console.log("获取失败");
			});
	};
	//获取商品详情
	$scope.getShopDetail = function(id) {
		console.log("获取商品详情中...");
		console.log(id);
		return $http
			.get($scope.urlApi + "/shop_product/" + id + "/")
			.then(function(res) {
				$scope.details=res.data.product;
				console.log($scope.details);
			}, function(res) {
				console.log("获取失败!");
			});
	};
}]);


app.controller("feverController",["$scope","$http",function($scope,$http){
	//获取发现创意首页商品
	$scope.getFever = function() {
		console.log("获取发现创意首页商品");
		$http.get($scope.urlApi + "/fever/")
			.then(function(res) {
				$scope.fevers=res.data.hot;
				console.log($scope.fevers);
			}, function(res) {
				console.log("Failed!");
			});
	};
	$scope.getFever();
	//获取全部创意商品
	$scope.getFeverType = function(key) {
		console.log("获取第" + key + '分类创意商品...');
		return $http
			.get($scope.urlApi + '/fever/' + key + '/')
			.then(function(res) {
				$scope.types = res.data;
				console.log($scope.types);
			}, function() {
				console.log("获取失败");
			});
	};
	$scope.getFeverLatest = function() {
		console.log("获取最新创意商品...");
		return $http
			.get($scope.urlApi + "/fever/latest/")
			.then(function(res) {
				$scope.latest = res.data;
				console.log($scope.latest);
			}, function() {
				console.log("获取失败");
			});
	};
	$scope.getFeverSuccess = function() {
		console.log("获取成功案例创意商品...");
		return $http
			.get($scope.urlApi + "/fever/hot/")
			.then(function(res) {
				$scope.latest = res.data;
				console.log($scope.latest);
			}, function() {
				console.log("获取失败");
			});
	};
}]);

//发起创意步骤
app.controller("submitIdeaController",["$scope","$http",function($scope,$http){
	$scope.idea={
		type:"健康医疗",
		title:"生活是官方说法更加广泛",
		introduction:"事实告诉我们，能够真正服务于生活的创意才是我们要寻找的好设计。为此我们建立了一个投票环节，在这里，你所喜欢、支持的创意都有可能制作成产品并成功上市。一个好创意诞生很不容易，希望你们成为优秀的评审团。",
		label :"生活创意",
        detail: "temp",
    /*detail:"设计一款可根据按钮自由伸缩的耳塞装置，避免耳塞在使用后无处安放、使用前各种整理等问题，该装置大小控制在4-7cm范围内，比如5*5cm，越小巧越方便携带，装置的形状可以是云朵、叶子、花瓣等，也可根据个人爱好私人定制形状，装置的一面设置按钮，按钮位置视各个具体形状而定，一般设计在绕线处的轴心位置，轴心处的另一面，也就是装置的另一面，设置成耳塞插头的出口，出口处边缘以外的旁白部分可印制图案或产品标识，私人定制形状可印制个人喜欢图案。",*/
		video:"http://v.youku.com/v_show/id_XNjMyMDU2Nzgw.html?from=y1.3-music-new-4344-10220.91968-90792-90602.1-4"
	};
	$scope.submitIdea=function(idea){
        idea.detail = tiny_data();
		console.log(idea);
		$http.defaults.headers.post['X-CSRFToken'] = getCookie("csrftoken");
		return $http
			.post('/submit_idea/', $.param(idea))
			.then(function(response) {
				/// @todo 返回数据
				console.log("提交成功");
			},
			function(response) {
				console.log("提交失败");
			});
	};
}]);

// 商店商品详情页
app.controller('shopDetailController', ['$scope','$http', function($scope, $http){
	// 主图TAB切换
	$scope.index=0;
	$scope.imgHover=function($index){
		$scope.index=$index;
	};
}]);



