# AI 기반 댓글 순화 Moderation 플랫폼

자세한 백엔드 개발 후기는 블로그에 있습니다.
  <br/> 👉 블로그링크: https://blog.naver.com/develop0420/224214027214

<br>
<br>

## 1. 프로젝트 목표

본 프로젝트는 온라인 커뮤니티에서 발생하는 욕설 및 공격적 댓글 문제를 완화하기 위한 **AI 기반 댓글 moderation 시스템**을 연구하기 위해 개발된 실험용 웹 플랫폼이다.
사용자가 댓글을 작성하면 AI 모델이 댓글의 공격성을 탐지하고, 필요한 경우 더 정중한 문장을 생성하여 제안한다. 사용자는 이를 수락하거나 수정할 수 있으며, 이러한 상호작용 과정을 통해 moderation 방식이 사용자 경험과 커뮤니케이션에 어떤 영향을 미치는지를 분석할 수 있다.

해당 플랫폼은 실제 사용자 실험을 수행하기 위한 연구 환경으로 개발되었으며, 본 연구는 **ACM CHI Conference on Human Factors in Computing Systems (Poster Track)**에 채택되었다.


<br>
<br>

## 2. 시스템 개요

본 플랫폼은 댓글 작성 과정에서 AI moderation이 실시간으로 작동하는 웹 기반 실험 환경을 제공한다.

댓글이 작성되면 다음과 같은 moderation 파이프라인이 작동한다.

```
Comment Input
      ↓
Toxicity Detection (KoBERT)
      ↓
Moderation Decision
      ├─ Comment Block
      └─ Polite Suggestion Generation (KoBART)
                ↓
User Accept / Edit
                ↓
Final Comment Storage
```

이 구조를 통해 댓글 작성 과정에서 발생하는 **AI와 사용자 간 상호작용 데이터**를 수집할 수 있도록 설계하였다.


<br>
<br>

## 3. 기술 스택

### Backend

* **Python**

* **FastAPI**
  REST API 기반 웹 서버 구축

* **SQLAlchemy**
  ORM 기반 데이터베이스 모델 관리

* **Pydantic**
  API 요청 및 응답 데이터 스키마 정의



### AI Models

* **KoBERT**

  * 댓글의 공격성 및 욕설 여부 탐지
  * toxicity detection classifier

* **KoBART**

  * 공격적인 댓글을 정중한 표현으로 변환
  * text refinement generation

* **Hugging Face Transformers**

  * 모델 로딩 및 inference 관리



### Database

* **PostgreSQL / MySQL**

SQLAlchemy ORM을 사용하여 댓글 데이터와 moderation 결과를 저장할 수 있는 데이터 구조를 설계하였다.
데이터베이스는 댓글 작성 과정에서 발생하는 사용자 입력, AI 생성 결과, 최종 제출 댓글 등의 정보를 기록하여 이후 분석에 활용할 수 있도록 구성하였다.



### Deployment

* **Render**
  백엔드 서버 배포

* **Hugging Face Hub**
  AI 모델 관리 및 로딩

