// polite-front/src/pages/PostDetailPage.jsx

import React, { useEffect, useState } from "react";
import { useLocation, useParams } from "react-router-dom";
import axios from "axios";
import Comments from "./Comments"; // 기존 댓글 컴포넌트

function PostDetailPage() {
  const { id } = useParams();
  const { state } = useLocation();
  const [post, setPost] = useState(null);
  const [verified, setVerified] = useState(false);

  useEffect(() => {
    if (!state?.password) return;

    axios.post(`http://localhost:8000/posts/${id}/verify`, { password: state.password })
      .then((res) => {
        if (res.data.valid) {
          setVerified(true);
          setPost(res.data.post);
        } else {
          alert("비밀번호가 틀렸습니다.");
        }
      })
      .catch((err) => console.error(err));
  }, [id, state]);

  if (!verified) return <p>비밀번호를 확인 중입니다...</p>;
  if (!post) return <p>로딩 중...</p>;

  return (
    <div style={{ margin: "5%" }}>
      {/* 제목 */}
      <h1
        style={{
          fontSize: "20px",           // text-xl
          fontWeight: "600",          // font-semibold
          color: "#374151",           // text-gray-700
          marginBottom: "8px",        // mb-2
        }}
      >
        {post.title}
      </h1>

      {/* 본문 */}
      <p
        style={{
          fontSize: "14px",           // text-sm
          color: "#6B7280",           // text-gray-500
          marginBottom: "24px",       // mb-6
        }}
      >
        {post.content}
      </p>

      {/* 댓글 영역 */}
      <Comments postId={post.id} />
    </div>
  );
}

export default PostDetailPage;

