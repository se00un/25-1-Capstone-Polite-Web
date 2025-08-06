// polite-front/src/components/CommentBox.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import PopupModal from "./PopupModal";

function CommentBox({
  userId,
  inputValue,
  setInputValue,
  onFinalSubmit,
  replyTargetId,
  setReplyTargetId,
  postId
}) {
  const [isRefined, setIsRefined] = useState(false);
  const [isPopupVisible, setIsPopupVisible] = useState(false);
  const [originalText, setOriginalText] = useState("");
  const [refinedText, setRefinedText] = useState("");
  const [logitPolite, setLogitPolite] = useState(null);
  const [isModified, setIsModified] = useState(false);

  useEffect(() => {
    setIsPopupVisible(false);
    setIsRefined(false);
    setOriginalText("");
    setRefinedText("");
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue || inputValue.trim().length < 1) return;

    try {
      const bertRes = await axios.post("http://localhost:8000/bert/predict", {
        text: isRefined ? originalText : inputValue,
      });

      const { predicted_class, probability } = bertRes.data;
      const logitOrig = probability;

      if (predicted_class === 1 && !isRefined) {
        const kobartRes = await axios.post("http://localhost:8000/kobart/generate", {
          text: inputValue,
        });

        const refined = kobartRes.data.polite_text;

        const politeLogitRes = await axios.post("http://localhost:8000/bert/predict", {
          text: refined,
        });

        setOriginalText(inputValue);
        setRefinedText(refined);
        setLogitPolite(politeLogitRes.data.probability);
        setIsPopupVisible(true);
        setIsRefined(true);
        return;
      }

      if (isRefined) {
        const isModified = inputValue !== refinedText;

        const finalPoliteLogitRes = await axios.post("http://localhost:8000/bert/predict", {
          text: inputValue,
        });

        const logit_polite = finalPoliteLogitRes.data.probability;

        await onFinalSubmit({
          post_id: postId,
          original: originalText,
          polite: inputValue,
          logit_original: logitOrig,
          logit_polite,
          selected_version: "polite",
          is_modified: isModified,
          reply_to: replyTargetId,
        });
      } else {
        await onFinalSubmit({
          post_id: postId,
          original: inputValue,
          polite: null,
          logit_original: logitOrig,
          logit_polite: null,
          selected_version: "original",
          is_modified: false,
          reply_to: replyTargetId,
        });
      }

      setInputValue("");
      setIsRefined(false);
      setRefinedText("");
      setOriginalText("");
      setReplyTargetId(null);
    } catch (error) {
      console.error("댓글 처리 실패:", error);
      alert("댓글 처리 중 문제가 발생했습니다.");
    }
  };

  const handleAccept = () => {
    setInputValue(refinedText);
    setIsPopupVisible(false);
    setIsRefined(true);
  };

  const handleChange = (e) => {
    const newValue = e.target.value;
    setInputValue(newValue);

    if (isRefined && newValue !== refinedText) {
      setIsModified(true);     
    } else {
      setIsModified(false);   
   }
  };

  const handleReject = async () => {
    const originalLogitRes = await axios.post("http://localhost:8000/bert/predict", {
      text: originalText,
    });

    const politeLogitRes = await axios.post("http://localhost:8000/bert/predict", {
      text: refinedText,
    });

    await onFinalSubmit({
      post_id: postId,
      original: originalText,
      polite: refinedText,
      logit_original: originalLogitRes.data.probability,
      logit_polite: politeLogitRes.data.probability,
      selected_version: "original",
      is_modified: isModified,
      reply_to: replyTargetId,
    });

    setInputValue("");
    setIsPopupVisible(false);
    setIsRefined(false);
    setReplyTargetId(null);
  };

  return (
    <div>
      <form onSubmit={handleSubmit} style={{ marginTop: "2rem", width: "100%" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "1rem", justifyContent: "center", marginBottom: "1rem" }}>
          <label style={{ fontWeight: "bold", fontSize: "1.1rem", whiteSpace: "nowrap" }}>
            {replyTargetId ? "💬 대댓글 작성" : "💬 댓글 작성"}
          </label>
          <textarea
            value={inputValue}
            onChange={handleChange}
            rows={3}
            style={{
              width: "100%",
              minHeight: "80px",
              padding: "0.75rem",
              fontSize: "1rem",
              borderRadius: "8px",
              border: "1px solid #ccc",
              backgroundColor: "#ffffff",
              color: "#000000", 
              resize: "vertical",
            }}
            placeholder={replyTargetId ? "대댓글을 입력하세요..." : "댓글을 입력하세요..."}
          />
        </div>

        <div style={{ textAlign: "center" }}>
          <button
            type="submit"
            style={{
              padding: "0.5rem 1.2rem",
              borderRadius: "6px",
              border: "none",
              backgroundColor: "#444",
              color: "#fff",
              cursor: "pointer",
            }}
          >
            {replyTargetId ? "대댓글 작성" : "댓글 작성"}
          </button>
        </div>

        {replyTargetId && (
          <div style={{ textAlign: "center", marginTop: "0.5rem" }}>
            <button
              type="button"
              onClick={() => setReplyTargetId(null)}
              style={{
                padding: "0.3rem 0.8rem",
                borderRadius: "6px",
                border: "none",
                backgroundColor: "#666",
                color: "#fff",
                cursor: "pointer",
                fontSize: "0.9rem",
              }}
            >
              대댓글 작성 취소
            </button>
          </div>
        )}
      </form>

      {isPopupVisible && (
        <PopupModal
          original={originalText}
          suggested={refinedText}
          onAccept={handleAccept}
          onReject={handleReject}
        />
      )}
    </div>
  );
}

export default CommentBox;
