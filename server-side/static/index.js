window.onload = () => {
  $("#sendbutton").click(() => {
    imagebox = $("#imagebox");
    link = $("#link");
    input = $("#imageinput")[0];
    if (input.files && input.files[0]) {
      let formData = new FormData();
      formData.append("video", input.files[0]);
      $.ajax({
        url: "/detect",
        type: "POST",
        data: formData,
        cache: false,
        processData: false,
        contentType: false,
        beforeSend: function () {
          $(".status").css("visibility", "visible");
          $(".statustext").text("Loading");
          $("#link").css("visibility", "hidden");
        },
        error: function (data) {
          $(".status").css("visibility", "visible");
          $(".statustext").text("Error");
        },
        success: function (data) {
          $("#link").css("visibility", "visible");
          $("#download").attr("href", "static/" + data);
        },
        complete: function () {
          $(".status").css("visibility", "hidden");
          $(".statustext").text("Completed");
        },
      });
    }
  });
};

function readUrl(input) {
  imagebox = $("#imagebox");
  console.log(imagebox);
  console.log("evoked readUrl");
  if (input.files && input.files[0]) {
    let reader = new FileReader();
    reader.onload = function (e) {
      console.log(e.target);

      imagebox.attr("src", e.target.result);
    };
    reader.readAsDataURL(input.files[0]);
  }
}
