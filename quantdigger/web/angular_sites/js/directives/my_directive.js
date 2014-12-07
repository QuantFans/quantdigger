/**
 * 创意产品网格视图，可以与不同的项视图结合使用。
 * 组合成商店，预售商店，投票商店。
 */
app.directive("ideashopgridview", function() {
    return {
        restrict:"AE",
        /*templateUrl:"views/idea_sites/idea_gridview.html",*/
        template: '<div class="container" id="product-three-columns"' +
                       '<div ng-transclude></div>' +
                  '</div>',
        transclude: true,
        link: function(scope, element, attrs) {
            scope.items = scope.loadData();
        }
    }
});

//失去焦点是验证表单
// app.directive("myFocus", function() {
//     return{
//     	require: 'ngModel',
//         restrict: "AE",
//         link:function(scope,element,attrs,ngModel){
//         	if(!ngModel) return;
//         	ngModel.$focused = false;
//         	element.bind("focus",function(){
//                 scope.$apply(function() {
//                     ngModel.$focused = true;
//                 });
//         	}).bind("blur",function(){
//                 scope.$apply(function() {
//                     ngModel.$focused = false;
//                 });
//         	});
//         }
//     };
// });