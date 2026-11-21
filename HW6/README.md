# HW6

- 이름: 박지호
- 학번: 21010856

## 실행 방법

1. `sales_clean.csv`와 `hw6.ipynb`가 같은 폴더에 있는 상태에서 Python 환경에 `pandas`, `scikit-learn`, `joblib`, `jupyter`, `flask`, `flask-restx`를 설치합니다.
2. Jupyter에서 `hw6.ipynb`를 열고 커널 재시작 후 **Run All**을 실행합니다. 노트북이 `sales_model.pkl`을 저장합니다.
3. 이 폴더에서 `flask --app app run`을 실행한 뒤 `http://127.0.0.1:5000/api/docs`를 엽니다.
4. Swagger UI에서 `POST /api/sales/predict`의 **Try it out** → **Execute**를 누릅니다. 예시 입력은 `{"quantity": 40, "unit_price": 200000}`이며 응답은 `{"total_sales": 8000000}`입니다. **Response body**가 보이는 화면을 캡처하여 이 폴더에 `docs.png`로 저장합니다.

## 단계 ③ 답

기본 선형 회귀는 `quantity`와 `unit_price`의 가중합으로 예측하므로, 두 값의 곱으로 정해지는 총액을 정확히 표현하지 못해 test R²가 0.862입니다. `qp = quantity × unit_price`를 추가하면 모델이 실제 계산식을 표현할 수 있어 test R²가 1.000이 됩니다.

## 단계 ⑤ 결정과 이유

트리의 `max_depth`는 **8**을 선택했습니다. 5-fold 교차검증 평균 R²가 depth 8에서 0.992, depth 12에서 0.995로 차이가 0.003뿐인 반면, 잎 수는 250개에서 781개로 늘어납니다. 이 데이터에는 `총액 = 수량 × 단가`라는 실제 규칙이 있어 제한 없는 트리의 training R² 1.000과 test R² 0.994도 가깝습니다.

## 단계 ⑦ 답

API에는 **`qp`를 추가한 선형 회귀**를 사용했습니다. 수량 40, 단가 200,000원의 실제 곱은 8,000,000원이며, 이 모델의 예측도 8,000,000원입니다. depth 8 트리의 예측은 7,362,301원이고, 곱셈 규칙을 직접 반영한 선형 회귀가 이 과제의 범위에서 더 적합합니다.
