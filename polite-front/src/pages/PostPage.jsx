// polite-front/src/pages/PostPage.jsx

import React, { useState } from "react";
import CommentBox from "../components/CommentBox";
import PopupModal from "../components/PopupModal";
import CommentItem from "../components/CommentItem";

const PostPage = () => {
  const post = {
    id: 1,
    title: "실험용 게시글",
    content: "이곳은 실험을 위한 게시글입니다. 댓글을 달아보세요!",
  };

  // 댓글 배열: 각 댓글에 대댓글 리스트 포함
  const [comments, setComments] = useState([]);

  const [inputValue, setInputValue] = useState("");
  const [showPopup, setShowPopup] = useState(false);
  const [suggestedText, setSuggestedText] = useState("");
  const [originalText, setOriginalText] = useState("");
  const [refinedComments, setRefinedComments] = useState({});

  // 대댓글 쓰기 대상 댓글 ID (null이면 새 댓글 작성 중)
  const [replyTargetId, setReplyTargetId] = useState(null);

  // 욕설 검사 및 순화 팝업 띄우기
  const handleToxicComment = (original, suggested) => {
    if (!suggested) {
      // 욕설 없는 댓글 or 대댓글 → 바로 등록 & 순화 기록 초기화
      addCommentOrReply(original, replyTargetId);
      setShowPopup(false);
      setRefinedComments({});
      setReplyTargetId(null);
      return;
    }

    if (refinedComments[original]) {
      // 이미 순화 완료 댓글 → 바로 등록
      addCommentOrReply(original, replyTargetId);
      setShowPopup(false);
      setReplyTargetId(null);
    } else {
      setOriginalText(original);
      setSuggestedText(suggested);
      setShowPopup(true);
    }
  };

  // 대댓글 or 새 댓글 등록 함수
  const addCommentOrReply = (text, parentId) => {
    if (!parentId) {
      // 새 댓글
      setComments((prev) => [
        ...prev,
        { id: Date.now(), text, replies: [] },
      ]);
    } else {
      // 대댓글
      setComments((prev) =>
        prev.map((comment) =>
          comment.id === parentId
            ? {
                ...comment,
                replies: [...comment.replies, { id: Date.now(), text }],
              }
            : comment
        )
      );
    }
  };

  // 순화문 채택 시 댓글창에 순화문 내려놓고 팝업 닫기
  const handleAcceptSuggestion = () => {
    setInputValue(suggestedText);
    setShowPopup(false);
  };

  // 원래 댓글 유지 시 바로 댓글 or 대댓글 등록하고 팝업 닫기
  const handleRejectSuggestion = () => {
    addCommentOrReply(originalText, replyTargetId);
    setInputValue("");
    setShowPopup(false);
    setReplyTargetId(null);
  };

  // 최종 제출: 댓글 또는 대댓글 등록 + 입력창 초기화 + 순화 기록 초기화
  const handleFinalSubmit = (finalText) => {
    addCommentOrReply(finalText, replyTargetId);
    setInputValue("");
    setRefinedComments({});
    setReplyTargetId(null);
  };

  // 대댓글 입력창 켜기 (댓글 ID 전달)
  const startReply = (commentId) => {
    setReplyTargetId(commentId);
    setInputValue(""); // 입력창 초기화
  };

  return (
    <div
      style={{
        maxWidth: "700px",
        margin: "0 auto",
        padding: "2rem",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        alignItems: "center",
        minHeight: "100vh",
        textAlign: "center",
      }}
    >
      <h1>{post.title}</h1>
      <p>{post.content}</p>

      <hr style={{ width: "100%" }} />

      <h2 style={{ alignSelf: "flex-start" }}>댓글</h2>

      <div style={{ width: "100%", textAlign: "left" }}>
        {comments.map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            startReply={startReply}
          />
        ))}
      </div>

      <CommentBox
        inputValue={inputValue}
        setInputValue={setInputValue}
        onToxicDetected={handleToxicComment}
        onFinalSubmit={handleFinalSubmit}
        replyTargetId={replyTargetId}
      />

      {showPopup && (
        <PopupModal
          original={originalText}
          suggested={suggestedText}
          onAccept={handleAcceptSuggestion}
          onReject={handleRejectSuggestion}
        />
      )}
    </div>
  );
};

export default PostPage;

