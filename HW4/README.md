# HW4 : todo 앱에 API 더하기

## 더한 것
- 설명 칸(note)을 API로도 주고받게 했습니다.
- GET /api/todos/?done=true로 완료한 것만 골라 받게 했습니다.

## 실행하는 법
    pip install -r requirements.txt
    flask --debug run
    화면 http://127.0.0.1:5000/  
    문서 http://127.0.0.1:5000/api/docs

## 화면
### 1. 주소 여섯 줄이 모두 보이는 문서
![docs](docs.png)

### 2. note를 넣어 만들었더니 201이 온 모습
![post](post.png)

### 3. 없는 번호를 불렀더니 404가 온 모습
![404](notfound.png)