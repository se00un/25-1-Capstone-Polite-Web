import React, { useEffect, useState } from "react";

const PopupModal = ({ original = "", suggested = "", onAccept, onReject }) => {
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");
    setIsDarkMode(mediaQuery.matches);

    const handler = (e) => setIsDarkMode(e.matches);
    mediaQuery.addEventListener("change", handler);

    return () => mediaQuery.removeEventListener("change", handler);
  }, []);

  const backgroundColor = isDarkMode ? "#222" : "#eee";
  const textColor = isDarkMode ? "white" : "black";
  const buttonContainerStyle = {
    marginTop: "1.5rem",
    display: "flex",
    gap: "1rem",
    justifyContent: "center",
  };

  return (
    <div style={overlayStyle}>
      <div style={{ ...modalStyle, backgroundColor, color: textColor }}>
        <h3>⚠️ 부정적 표현 감지됨!</h3>
        <p>
          <strong>사용자 입력:</strong> {original || "(입력 없음)"}
        </p>
        <p>
          <strong>순화 제안:</strong> {suggested || "(순화 문장이 없습니다)"}
        </p>
        <p style={{ marginTop: "1rem" }}>
          위 문장은 <strong>욕설 포함 가능성이 높은 댓글</strong>입니다.
          <br />
          아래 순화 문장으로 수정하시겠습니까?
        </p>
        <div style={buttonContainerStyle}>
          <button
            onClick={onAccept}
            style={{
              backgroundColor: "#4CAF50",
              color: "white",
              padding: "10px 20px",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            ✅ 순화된 문장 채택
          </button>
          <button
            onClick={onReject}
            style={{
              backgroundColor: "#f44336",
              color: "white",
              padding: "10px 20px",
              border: "none",
              borderRadius: "4px",
              cursor: "pointer",
            }}
          >
            ❌ 원래 댓글 유지
          </button>
        </div>
      </div>
    </div>
  );
};

const overlayStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  width: "100vw",
  height: "100vh",
  backgroundColor: "rgba(0,0,0,0.7)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  zIndex: 1000,
};

const modalStyle = {
  padding: "2rem",
  borderRadius: "8px",
  width: "500px",
  boxShadow: "0 0 20px rgba(0,0,0,0.8)",
};

export default PopupModal;
