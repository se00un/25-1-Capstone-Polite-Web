// polite-front/src/pages/IntroPage.jsx

import React from "react";
import { useNavigate } from "react-router-dom";

const IntroPage = () => {
  const navigate = useNavigate();

  return (
    <div style={{ backgroundColor: "#e0f2fe",           
                padding: "1.5rem",
                borderRadius: "10px",
                border: "2px solid #38bdf8",         
                boxShadow: "0 4px 10px rgba(0, 0, 0, 0.05)", 
                marginBottom: "2rem",
                maxHeight: "90vh",
                overflowY: "auto",
                }}>
      <h1 style={{ fontSize: "2rem", fontWeight: "bold", color: "#030608ff"}}>
         욕설 순화 시스템 실험 안내
      </h1>

      <p style={{ lineHeight: "1.6", marginBottom: "1rem" }}>
        이 웹사이트는 <strong>온라인 커뮤니케이션 환경 개선</strong>을 위한 실험용 시스템입니다. <br />
        참여자는 댓글을 자유롭게 작성하며 <strong>표현 방식, 감정 표현</strong>을 분석하는 연구에 기여하게 됩니다.
      </p>

      <h2 style={{ fontSize: "1.2rem", marginTop: "2rem" }}>⚠️ 이용 안내</h2>
      <ul style={{ marginLeft: "1.5rem", marginBottom: "1rem", lineHeight: "1.6" }}>
        <li>💥 욕설/공격적인 표현 사용이 <strong>허용</strong>됩니다.</li>
        <li>💡 단, 감지될 경우 <strong>AI가 순화된 문장을 제안</strong>하는 팝업이 등장할 수 있습니다. </li>
        <li>⌛️ 팝업 등장 시 <strong>10초 정도의 시간이 소요</strong>되며, 이때 다른 곳을 클릭하지말고 <strong>기다려주세요!</strong></li>
        <li>👍 제안 문장은 <strong>수락/거절</strong> 모두 가능하며, 거절 시 원래 문장이 등록됩니다.</li>
      </ul>

      <h2 style={{ fontSize: "1.2rem", marginTop: "2rem" }}>📷 팝업 예시</h2>
      <img
        src="/assets/popup_example.png"
        alt="팝업 예시"
        style={{ width: "100%", maxWidth: "500px", border: "1px solid #ddd", borderRadius: "8px", marginBottom: "2rem" }}
      />

      <h2 style={{ fontSize: "1.2rem", marginTop: "2rem" }}>📌 참여 방법</h2>
      <ol style={{ marginLeft: "1.5rem", lineHeight: "1.6" }}>
        <li> 로그인 후 게시글을 선택합니다.</li>
        <li> 비밀번호 입력 시 게시글 및 댓글을 확인할 수 있습니다.</li>
        <li> 댓글 작성 후, 팝업이 등장하게 된다면 원하는 문장을 선택해 주세요.</li>
      </ol>

      <div style={{ marginTop: "2rem", textAlign: "center" }}>
        <button
          onClick={() => navigate("/login")}
          style={{
            backgroundColor: "#4CAF50",
            color: "white",
            padding: "0.75rem 1.5rem",
            fontSize: "1rem",
            borderRadius: "6px",
            border: "none",
            cursor: "pointer"
          }}
        >
          시작하기
        </button>
      </div>
    </div>
  );
};

export default IntroPage;
