// polite-front/src/pages/Comments.jsx
import React, { useState, useEffect } from "react";
import axios from "axios";
import CommentBox from "../components/CommentBox";
import PopupModal from "../components/PopupModal";
import CommentItem from "../components/CommentItem";

const Comments = ({ postId }) => {
  const [userId, setUserId] = useState("");
  const [inputValue, setInputValue] = useState("");
  const [comments, setComments] = useState([]);

  const [replyTargetId, setReplyTargetId] = useState(null);
  const [replyNickname, setReplyNickname] = useState("");

  const [showModal, setShowModal] = useState(false);
  const [modalData, setModalData] = useState({
    original: "",
    polite: "",
    logit_original: null,
    logit_polite: null,
    selected_version: "original",
  });

  useEffect(() => {
    const storedId = localStorage.getItem("userId");
    if (storedId) setUserId(storedId);
    fetchComments();
  }, []);

  const fetchComments = async () => {
    try {
      const res = await axios.get(`http://localhost:8000/comments/${postId}`);
      setComments(res.data);
    } catch (error) {
      console.error("댓글 불러오기 실패:", error);
    }
  };

  const handleFinalSubmit = async ({
    original,
    polite,
    logit_original,
    logit_polite,
    selected_version,
    reply_to = null,
    is_modified = false,
  }) => {
    try {
      const res = await axios.post("http://localhost:8000/comments/add", {
        user_id: userId,
        post_id: postId,
        original,
        polite,
        logit_original,
        logit_polite,
        selected_version,
        reply_to,
        is_modified,
      });
      console.log("댓글 등록 성공!", res.data);
      fetchComments();
      setInputValue("");
      setReplyTargetId(null);
      setReplyNickname("");
    } catch (error) {
      console.error("댓글 등록 실패:", error);
      alert("댓글 등록 중 오류가 발생했습니다.");
    }
  };

  const handleAccept = async () => {
    await handleFinalSubmit({
      original: modalData.original,
      polite: modalData.polite,
      logit_original: modalData.logit_original,
      logit_polite: modalData.logit_polite,
      selected_version: "polite",
      reply_to: replyTargetId, 
    });
  };

  const handleReject = async () => {
    await handleFinalSubmit({
      original: modalData.original,
      polite: modalData.polite,
      logit_original: modalData.logit_original,
      logit_polite: modalData.logit_polite,
      selected_version: "original",
      reply_to: replyTargetId,  
    });
  };

  const buildCommentTree = (flatComments) => {
    const map = {};
    const roots = [];

    flatComments.forEach((comment) => {
      map[comment.id] = { ...comment, replies: [], depth: 0 };
    });

    flatComments.forEach((comment) => {
      if (comment.reply_to) {
        const parent = map[comment.reply_to];
        if (parent) {
          map[comment.id].depth = parent.depth + 1;
          parent.replies.push(map[comment.id]);
        }
      } else {
        roots.push(map[comment.id]);
      }
    });

    const sortByDate = (a, b) =>
      new Date(a.created_at) - new Date(b.created_at);

    const sortReplies = (comments) => {
      comments.sort(sortByDate);
      comments.forEach((comment) => {
        if (comment.replies && comment.replies.length > 0) {
          sortReplies(comment.replies);
        }
      });
    };

    sortReplies(roots);
    return roots;
  };

  const startReply = (commentId, nickname) => {
    setReplyTargetId(commentId);
    setReplyNickname(nickname);
    setInputValue(`@${nickname} `);
  };

  return (
    <div style={{ 
        maxWidth: "960px",
        margin: "2rem auto",
        backgroundColor: "#f8f9fa",
        padding: "2rem",
        borderRadius: "8px",
        color: "#000",
        }}>
      <h1>남자들 자아가 왜 이렇게 비대하죠ㅋㅋ </h1>
      <p>
        도대체 남성들은 왜 이렇게 자아가 부풀어 있죠? 그냥 조용히 넘기려다 너무 역겨워서 한 마디 했더니, “지령이다”, “계정 샀다”, “OO생 인증해라”… 
        뭐 하나 제대로 반박은 못하고, 정신승리만 늘어놓는 수준에 실소만 나옵니다. 이쯤 되면 현실 부정도 병 아닙니까? <br /><br />

        그냥 말할게요. 저는 남성이 싫습니다. 
        남성들은 언제나 방관자이거나 가해자였어요. 그러면서 여성들이 말 꺼내면 “너무 예민하다”, “남혐이다”? 그런 말 할 자격이 있나요? <br /><br />
        지금도 남초 커뮤니티는 똑같죠. 여자들이 연대하면 “좌표 찍었다”, “대대적 조작이다”, “내 주변 여자는 안 그런데?” 그 말을 믿는 사람들 보며 묻고 싶습니다. 
        당신 주변 여자가 왜 아무 말도 안 했는지 진짜 몰라서 그래요? 당신 같은 사람이 조롱하고 가스라이팅할까봐 입 다물고 있었던 거잖아요. <br /><br />
        여성들이 조용히 있으면 무시하고, 말하면 공격하고, 연대하면 혐오하고. 대체 어떻게 해야 만족하죠? 
        여자들이 계속 착하게, 조용히, 순응하면서 살아주길 원하나요? 그렇게 노예처럼 말이죠? <br /><br />
        이 사회에서 여성으로 산다는 건 계속해서 침묵하라는 압박을 견디는 일입니다. “나는 페미니스트가 아닙니다”라고 말하길 기대하지 마세요. 
        지금 이 상황에서 페미니즘은 선택이 아니라 최소한의 생존 전략입니다. <br /><br />
        이 글이 불편한가요? 그렇다면 당신은 그동안 얼마나 편하게 살아왔는지 곰곰이 돌아보시길 바랍니다.
      </p>
      <hr />
      <h3>댓글</h3>

      <div
        style={{
        maxHeight: "400px",     
        overflowY: "auto",      
        paddingRight: "10px",  
        border: "1px solid #444",
        backgroundColor: "#fff",
        marginBottom: "2rem",
        borderRadius: "6px"
      }}
      >
        {buildCommentTree(comments).map((comment) => (
          <CommentItem
            key={comment.id}
            comment={comment}
            startReply={startReply}
            depth={comment.depth}
          />
        ))}
      </div>

      <CommentBox
        userId={userId}
        postId={postId}
        inputValue={inputValue}
        setInputValue={setInputValue}
        onFinalSubmit={handleFinalSubmit}
        setShowModal={setShowModal}
        setModalData={setModalData}
        replyTargetId={replyTargetId}
        setReplyTargetId={setReplyTargetId}
        replyNickname={replyNickname}
      />

      {showModal && (
        <PopupModal
          original={modalData.original}
          suggested={modalData.polite}
          onAccept={handleAccept}
          onReject={handleReject}
        />
      )}
    </div>
  );
};

export default Comments;
