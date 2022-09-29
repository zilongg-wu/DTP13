/*Styling for like button*/


/*This code allows user to be able to like number increase and unlike number decrease*/
function like(classroomId) {
  const likeCount = document.getElementById(`likes-count-${classroomId}`);
  const likeButton = document.getElementById(`like-button-${classroomId}`);

  /*This is the form submission for the like button using javascript*/
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
