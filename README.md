# StackOverflow-lite

[![Build Status](https://travis-ci.org/abadojack/StackOverflow-lite.svg?branch=master)](https://travis-ci.org/abadojack/StackOverflow-lite) [![Coverage Status](https://coveralls.io/repos/github/abadojack/StackOverflow-lite/badge.svg?branch=master)](https://coveralls.io/github/abadojack/StackOverflow-lite?branch=master)

StackOverflow-lite is a platform where people can ask questions and provide answers



# Endpoints
## Sign up
```json
POST /api/v1/auth/signup
```

```json
{
  "username": "abadojack",
  "password": "password",
  "email"   : "abadojack@gmail.com"
}
```

## Login
```json
POST /api/v1/auth/login
```

```json
{
  "username": "abadojack",
  "password": "password"
}
```

## Sign out
```json
POST /api/v1/auth/signout
```

## Fetch all questions
```json
GET /api/v1/questions
```
##### Header
```json
{
  "token": "token_from_login"
}
```


## Get a specific question
```json
GET /api/v1/questions/{question_id}
```
##### Header
```json
{
  "token": "token_from_login"
}
```

## Post a question
```json
POST /api/v1/questions
```
##### Header
```json
{
  "token": "token_from_login"
}
```
##### Body
```json
{
  "title": "question title", 
  "body" : "question body"
  }
```

## Delete question
```json
DELETE /api/v1/questions/{question_id}
```
##### Header
```json
{
  "token": "token_from_login"
}
```


## Post an answer to a question
```json
POST /api/v1/questions/{questiond_id}/answers
```
##### Header
```json
{
  "token": "token_from_login"
}
```
##### Body
```json
{ 
  "body" : "answer body"
}
```

## Mark an answer as accepted or update an answer.

```json
PUT /questions/{question_id}/answers/{answer_id}
```
##### Header
```json
{
  "token": "token_from_login"
}
```
##### Body
```json
{ 
  "body" : "answer body"
}
```
## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.