function like(classroomId) {
  const likeCount = document.getElementById(`likes-count-${classroomId}`);
  const likeButton = document.getElementById(`like-button-${classroomId}`);

  fetch(`/like-classroom/${classroomId}`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      likeCount.innerHTML = data["likes"];
      if (data["liked"] === true) {
        likeButton.className = "fas fa-thumbs-up";
      } else {
        likeButton.className = "far fa-thumbs-up";
      }
    })
    .catch((e) => alert("Could not like classroom."));
}
