// src/pages/Login.jsx
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";

function Login() {
  const [userId, setUserId] = useState("");
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!userId.trim()) {
      alert("ID를 입력해주세요");
      return;
    }

    try {
      const response = await axios.post("http://localhost:8000/users/verify", {
        user_id: userId,
      });

      if (response.data.exists) {
        localStorage.setItem("userId", userId);
        navigate("/posts");
      } else {
        alert("존재하지 않는 아이디입니다. \n먼저 '새로운 아이디 만들기'를 눌러주세요. '새로운 아이디 만들기'를 누르면 아이디가 자동으로 등록됩니다!");
      }
    } catch (err) {
      console.error("로그인 확인 오류:", err);
      alert("로그인 도중 오류가 발생했습니다!");
    }
  };

  const handleRegister = async () => {
    if (!userId.trim()) {
      alert("ID를 입력해주세요");
      return;
    }

    try {
      await axios.post("http://localhost:8000/users/register", {
        user_id: userId,
      });
      localStorage.setItem("userId", userId);
      navigate("/posts");
    } catch (error) {
      alert("아이디 등록 실패! 이미 존재하는 ID입니다.");
      console.error("등록 에러:", error);
    }
  };

  return (
    <div style={{ textAlign: "center", marginTop: "10%" }}>
      <h2> 로그인</h2>

      <input
        type="text"
        placeholder="사용자 ID를 입력하세요"
        value={userId}
        onChange={(e) => setUserId(e.target.value)}
        style={{ padding: "10px", fontSize: "16px" }}
      />

      <div style={{ marginTop: "1rem" }}>
        <button onClick={handleLogin} style={{ marginRight: "10px", padding: "10px 20px" }}>
          입장
        </button>

        <button onClick={handleRegister} style={{ padding: "10px 20px" }}>
          새로운 아이디 만들기
        </button>
      </div>
    </div>
  );
}

export default Login;

