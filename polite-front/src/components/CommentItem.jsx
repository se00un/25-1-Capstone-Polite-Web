// polite-front/src/components/CommentItem.jsx
import React, { useState } from "react";


const formattedDate = (timestamp) => {
  try {
    const date = new Date(timestamp);
    if (isNaN(date)) return "";
    return date.toLocaleString("ko-KR", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  } catch {
    return "";
  }
};

const CommentItem = ({ comment, startReply, depth = 0 }) => {
  const isTopLevel = depth === 0;
  const isReply = depth === 1;
  const isNestedReply = depth >= 2;
  return (
    <div 
      style={{
        marginLeft: `${depth * 16}px`,
        marginTop: depth > 0 ? "4px" : "3px", 
        backgroundColor: isTopLevel ? "#fff" : isReply ? "#f5f5f5" : "transparent",
        padding: isNestedReply ? "2px 0px" : "10px 12px",
        borderRadius: isNestedReply ? "0px" : "8px",
        marginBottom: isNestedReply ? "3px" : "5px",
        lineHeight: "1.4",
        fontSize: isNestedReply ? "15px" : "15px",
        boxShadow: isTopLevel ? "0 1px 2px rgba(0, 0, 0, 0.04)" : "none",
        border: isReply ? "1px solid #eee" : "none",
        maxWidth: "90%",
      }}
    >
      <p style={{ margin: 0 }}>
        <strong>{comment.user_id || "익명"}:</strong>{" "}
        {comment.selected_version === "polite" ? comment.polite : comment.original}
      </p>
      <p style={{ fontSize: "0.75rem", color: "#aaa", marginTop: "4px", marginBottom: 0 }}>
        {new Date(comment.created_at).toLocaleString()}{" "}
        <span
          style={{ cursor: "pointer", color: "#999", marginLeft: "1rem" }}
          onClick={() => startReply(comment.id, comment.user_id || "익명")}
        >
          답글쓰기
        </span>
      </p>

      {comment.replies && comment.replies.length > 0 && (
        comment.replies.map((reply) => (
          <CommentItem
            key={reply.id}
            comment={reply}
            startReply={startReply}
            depth={reply.depth}
          />
        ))
      )}
    </div>
  );
  }
    

export default CommentItem;
