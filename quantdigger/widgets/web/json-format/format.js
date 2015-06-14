/**
 * Created by chenzhengtong on 2014/10/28.
 */

var json_login_request = {
    "id": "xxx",  // or email?
    "password": "xxx"
};

var json_login_response = {
    "status": 1,  // 0 for error, 1 for ok
    "message": "ok",  // error message or ok message
    "user": {
        "id": "xxx",
        "email": "xxx@xx.com",
        "name": "xxx",
        "gender": "",
        "age": 20,
        "birthday": 11111111,  // milliseconds?
        "register_time": 11111111,  // milliseconds?
        "others": {}
    }
};

var json_post_article_request = {
    "id": "xxx",
    "article": {},
    "post_date": new Date()
};

var json_post_article_response = {
    "status": 1,  // 0 for error, 1 for ok
    "message": "ok"
};